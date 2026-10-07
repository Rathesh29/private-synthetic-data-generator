# Differential Privacy & Risk Evaluation Analysis

## 1. Formal Definition of Differential Privacy

A randomized mechanism $\mathcal{M}$ satisfies $(\varepsilon, \delta)$-Differential Privacy if for all pairs of neighboring datasets $D, D'$ differing on at most one individual employee record, and for all measurable subsets of query outputs $S \subseteq \mathrm{Range}(\mathcal{M})$:

$$\mathbb{P}[\mathcal{M}(D) \in S] \le e^\varepsilon \cdot \mathbb{P}[\mathcal{M}(D') \in S] + \delta$$

- **$\varepsilon$ (Epsilon - Privacy Loss Budget)**: Controls the multiplicative bound on output probability. Smaller $\varepsilon$ provides stronger protection against inference.
- **$\delta$ (Delta - Failure Probability)**: Probability that the $\varepsilon$-bound fails. Typically chosen such that $\delta \ll \frac{1}{|D|}$ (e.g., $10^{-5}$ for $|D| = 1,000$).

---

## 2. Privacy Accounting via Rényi Differential Privacy (RDP)

In DP-SGD, batch updates compose across thousands of iterations. Naive advanced composition yields loose bounds. The system implements the **Rényi Differential Privacy (RDP) Accountant** for the Subsampled Gaussian Mechanism.

For Renyi order $\alpha > 1$, the RDP of the mechanism $\mathcal{M}$ is defined as:
$$D_\alpha(\mathcal{M}(D) \,||\, \mathcal{M}(D')) = \frac{1}{\alpha - 1} \ln \int \left( \frac{p(x)^\alpha}{q(x)^{\alpha-1}} \right) dx$$

### Composition Property
Across $T$ sequential gradient steps, RDP accumulates linearly:
$$\varepsilon_{\text{total}}(\alpha) = \sum_{t=1}^T \varepsilon_t(\alpha)$$

### Conversion to $(\varepsilon, \delta)$-DP
We convert accumulated RDP to standard $(\varepsilon, \delta)$-DP by optimizing over Renyi orders:
$$\varepsilon(\delta) = \min_{\alpha > 1} \left( \varepsilon_{\text{total}}(\alpha) + \frac{\ln(1/\delta)}{\alpha - 1} \right)$$

---

## 3. Privacy-Utility Tradeoff Curve

```
Privacy Level (Lower ε) <================================> Utility Level (Higher ε)
ε = 0.2                                   ε = 1.0                             ε = 5.0
High Noise (σ = 2.5)                      Calibrated Noise (σ = 1.1)          Low Noise (σ = 0.5)
Strict Privacy Guarantee                  Balanced Protection                 High Statistical Utility
Retained Utility ~ 70%                    Retained Utility ~ 88-92%           Retained Utility ~ 97%
```

---

## 4. Empirical Privacy Risk Metrics

1. **Distance to Closest Record (DCR)**:
   Calculates minimum Euclidean distance from each synthetic record $s \in D_{\text{synth}}$ to all real training records $r \in D_{\text{real}}$:
   $$\mathrm{DCR}(s) = \min_{r \in D_{\text{real}}} \|s - r\|_2$$
   - $\mathrm{DCR} = 0$: Indicates exact record memorization / replica.
   - $\mathrm{DCR} > 0$: Quantifies novelty and dispersion.

2. **Membership Inference Risk**:
   Evaluates empirical susceptibility by measuring classification advantage over random chance (50% baseline).

> **Important Scientific Distinction**: Empirical risk tests evaluate observed properties of a specific dataset, but they **cannot prove** that a method is differentially private. Differential privacy is a mathematical property of the training algorithm itself, certified by DP-SGD gradient clipping and privacy accounting.
