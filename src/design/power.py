# from future import annotations
from dataclasses import dataclass
from math import sqrt
from scipy.stats import norm

@dataclass
class PowerResult:
    n_per_group: int
    total_n: int
    p1: float
    p2: float
    alpha: float
    power: float
    mde: float

def sample_size_proportions(baseline: float, mde: float, power: float = 0.8, alpha: float = 0.05) -> PowerResult:
    p1 = baseline
    p2 = baseline + mde
    if not (0 < p1 < 1 and 0 < p2 < 1 and p2 != p1):
        raise ValueError("Invalid rates; ensure 0<p<1 and mde != 0")
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    p_bar = (p1 + p2) / 2.0
    num = (z_alpha * sqrt(2 * p_bar * (1 - p_bar)) + z_beta * sqrt(p1*(1-p1) + p2*(1-p2))) ** 2
    n = int((num / ((p2 - p1) ** 2)) + 0.999)
    return PowerResult(n_per_group=n, total_n=2*n, p1=p1, p2=p2, alpha=alpha, power=power, mde=mde)
