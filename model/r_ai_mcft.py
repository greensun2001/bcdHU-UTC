from math import sqrt
import pandas as pd
import matplotlib.pyplot as plt


def vci_mcft(fc: float, ag: float, w: float, pv: float = 1) -> float:
    numerator = sqrt(fc)
    denominator = 0.31 + 24 * w / (ag * pv + 16)
    return numerator / denominator
