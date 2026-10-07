"""
Differentially Private Neural Generative Model (DP-Tabular-VAE).
Implements a Variational Autoencoder trained with DP-SGD (gradient clipping & Gaussian noise),
paired with formal Rényi Differential Privacy accounting.
"""

from typing import Dict, Any, List, Optional, Callable
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from app.ml.preprocessor import TabularDataPreprocessor
from app.privacy.accountant import RDPAccountant
from app.privacy.optimizer import DPSGDManager

class TabularVAE(nn.Module):
    """
    Variational Autoencoder tailored for preprocessed tabular vectors.
    """
    def __init__(self, input_dim: int, latent_dim: int = 16, hidden_dim: int = 64):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder_shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LeakyReLU(0.2)
        )
        self.fc_mu = nn.Linear(hidden_dim // 2, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim // 2, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid() # Outputs continuous values in [0, 1]
        )

    def encode(self, x: torch.Tensor):
        h = self.encoder_shared(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        # Clamp logvar to prevent extreme exponentiation
        logvar = torch.clamp(logvar, min=-10.0, max=10.0)
        return mu, logvar

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)

    def forward(self, x: torch.Tensor):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_recon = self.decode(z)
        return x_recon, mu, logvar

def vae_loss_function(model: TabularVAE, x: torch.Tensor) -> torch.Tensor:
    """
    Computes per-sample or batch reconstruction loss (MSE) + KL-divergence.
    """
    recon_x, mu, logvar = model(x)
    recon_loss = nn.functional.mse_loss(recon_x, x, reduction="sum")
    # KL divergence: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    # Balance beta-VAE weight for tabular representation
    return recon_loss + 0.1 * kl_loss

class DPNeuralGenerator:
    """
    Orchestrates DP-SGD training of Tabular VAE and synthetic sample generation.
    Computes rigorous privacy expenditure via Rényi Differential Privacy.
    """
    def __init__(
        self,
        latent_dim: int = 16,
        hidden_dim: int = 64,
        clipping_norm: float = 1.0,
        noise_multiplier: float = 1.1,
        learning_rate: float = 0.001,
        epochs: int = 20,
        batch_size: int = 64,
        target_delta: float = 1e-5
    ):
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.clipping_norm = clipping_norm
        self.noise_multiplier = noise_multiplier
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.target_delta = target_delta

        self.model: Optional[TabularVAE] = None
        self.preprocessor: Optional[TabularDataPreprocessor] = None
        self.privacy_details: Dict[str, Any] = {}
        self.training_loss_history: List[Dict[str, Any]] = []
        self.is_trained = False

    def fit(
        self,
        df: pd.DataFrame,
        preprocessor: TabularDataPreprocessor,
        progress_callback: Optional[Callable[[int, int, float, float], None]] = None
    ):
        self.preprocessor = preprocessor
        x_np = self.preprocessor.transform(df)
        dataset_size, input_dim = x_np.shape
        
        self.model = TabularVAE(input_dim=input_dim, latent_dim=self.latent_dim, hidden_dim=self.hidden_dim)
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        dp_manager = DPSGDManager(
            model=self.model,
            optimizer=optimizer,
            clipping_norm=self.clipping_norm,
            noise_multiplier=self.noise_multiplier,
            batch_size=self.batch_size
        )

        tensor_x = torch.tensor(x_np, dtype=torch.float32)
        indices = np.arange(dataset_size)
        
        self.training_loss_history = []
        effective_batch_size = min(self.batch_size, dataset_size)

        for epoch in range(1, self.epochs + 1):
            np.random.shuffle(indices)
            epoch_loss = 0.0
            num_batches = 0

            for start_idx in range(0, dataset_size, effective_batch_size):
                end_idx = min(start_idx + effective_batch_size, dataset_size)
                batch_idx = indices[start_idx:end_idx]
                x_batch = tensor_x[batch_idx]

                batch_loss = dp_manager.step_with_dp(vae_loss_function, x_batch)
                epoch_loss += batch_loss
                num_batches += 1

            avg_epoch_loss = epoch_loss / max(1, num_batches)
            
            # Compute current cumulative privacy
            current_privacy = RDPAccountant.get_privacy_spent(
                dataset_size=dataset_size,
                batch_size=effective_batch_size,
                noise_multiplier=self.noise_multiplier,
                epochs=epoch,
                target_delta=self.target_delta,
                clipping_norm=self.clipping_norm
            )
            
            self.training_loss_history.append({
                "epoch": epoch,
                "loss": round(float(avg_epoch_loss), 4),
                "epsilon": current_privacy["epsilon"],
                "delta": current_privacy["delta"]
            })

            if progress_callback:
                progress_callback(epoch, self.epochs, avg_epoch_loss, current_privacy["epsilon"])

        # Final privacy accounting
        self.privacy_details = RDPAccountant.get_privacy_spent(
            dataset_size=dataset_size,
            batch_size=effective_batch_size,
            noise_multiplier=self.noise_multiplier,
            epochs=self.epochs,
            target_delta=self.target_delta,
            clipping_norm=self.clipping_norm
        )
        self.is_trained = True
        return self

    def generate(self, num_records: int) -> pd.DataFrame:
        if not self.is_trained or self.model is None:
            raise ValueError("Model is not trained yet.")

        self.model.eval()
        with torch.no_grad():
            # Sample latent z from standard normal N(0, I)
            z = torch.randn(num_records, self.latent_dim)
            synthetic_norm_tensor = self.model.decode(z)
            synthetic_norm = synthetic_norm_tensor.cpu().numpy()

        synthetic_df = self.preprocessor.inverse_transform(synthetic_norm)
        return synthetic_df

    @property
    def has_formal_dp_guarantee(self) -> bool:
        return True

    @property
    def guarantee_statement(self) -> str:
        eps = self.privacy_details.get("epsilon", "N/A")
        delta = self.privacy_details.get("delta", "N/A")
        return (
            f"FORMAL DIFFERENTIAL PRIVACY GUARANTEE: Trained under ({eps}, {delta})-Differential Privacy "
            f"using DP-SGD with per-sample L2 clipping norm {self.clipping_norm} and Gaussian noise multiplier {self.noise_multiplier}. "
            "Guarantees that individual records in the source dataset cannot be inferred with confidence above the privacy budget."
        )
