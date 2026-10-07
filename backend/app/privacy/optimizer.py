"""
DP-SGD Optimizer Wrapper and Per-Sample Gradient Clipping Engine.
Implements DP-SGD with L2 gradient clipping and calibrated Gaussian noise injection.
"""

import torch
from torch.optim import Optimizer

class DPSGDManager:
    """
    Manages DP-SGD gradient clipping and noise injection for PyTorch models.
    Supports per-sample gradient accumulation and micro-batch clipping.
    """
    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: Optimizer,
        clipping_norm: float = 1.0,
        noise_multiplier: float = 1.1,
        batch_size: int = 64
    ):
        self.model = model
        self.optimizer = optimizer
        self.clipping_norm = float(clipping_norm)
        self.noise_multiplier = float(noise_multiplier)
        self.batch_size = max(1, int(batch_size))
        
    def step_with_dp(self, loss_fn, x_batch, *args, **kwargs):
        """
        Executes a DP-SGD training step on a batch with per-sample gradient clipping
        and Gaussian noise injection.
        """
        self.optimizer.zero_grad()
        batch_len = x_batch.size(0)
        
        # Accumulator for clipped gradients
        accumulated_grads = {
            name: torch.zeros_like(param)
            for name, param in self.model.named_parameters()
            if param.requires_grad
        }
        
        total_loss = 0.0
        
        # Compute per-sample gradient for true DP clipping
        for i in range(batch_len):
            self.model.zero_grad()
            sample_x = x_batch[i:i+1]
            sample_loss = loss_fn(self.model, sample_x, *args, **kwargs)
            total_loss += sample_loss.item()
            
            sample_loss.backward(retain_graph=(i < batch_len - 1))
            
            # Calculate L2 norm across all trainable parameters for this sample
            total_norm_sq = 0.0
            for name, param in self.model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    total_norm_sq += param.grad.data.norm(2).item() ** 2
            sample_norm = total_norm_sq ** 0.5
            
            # Clip factor: min(1, C / ||g||_2)
            clip_coef = min(1.0, self.clipping_norm / (sample_norm + 1e-6))
            
            for name, param in self.model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    accumulated_grads[name] += param.grad.data * clip_coef
                    
        # Average clipped gradients and inject calibrated Gaussian noise
        # Noise scale = (sigma * C) / batch_size
        noise_std = (self.noise_multiplier * self.clipping_norm) / float(batch_len)
        
        self.optimizer.zero_grad()
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                avg_grad = accumulated_grads[name] / float(batch_len)
                noise = torch.randn_like(param) * noise_std
                param.grad = avg_grad + noise
                
        self.optimizer.step()
        
        avg_loss = total_loss / float(batch_len)
        return avg_loss
