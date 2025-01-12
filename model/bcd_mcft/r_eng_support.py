import math
import numpy as np


def polynomial_eq(k: list):
    """solve a polynomial equation, found real values in the asc sort"""
    rcs = np.roots(k)
    rs = []
    for r in rcs:
        if np.isreal(r):
            rs.append(r.real)
    rs.sort()
    return rs


def quadratic_eq(a: float, b: float, c: float):
    """solve a quadratic equation, found values are in the asc sort
    return: a list of found values sorted ascendingly
    """
    delta = b * b - 4 * a * c
    l = []
    if delta > 0:
        r_d = math.sqrt(delta)
        x1 = (-b - r_d) / 2 / a
        x2 = (-b + r_d) / 2 / a
        l.append(x1)
        l.append(x2)
    elif delta < 0:
        l = []
    else:
        x = -b / 2 / a
        l.append(x)
    return l


def fc2Ec(fc: float) -> float:
    """calculate Ec (Mpa) from fc (Mpa) based on ACI formula"""
    return 4730 * math.sqrt(fc)


def fc2ft(fc: float) -> float:
    """calculate ft (Mpa) from fc (Mpa) based on JCI formula"""
    k = 0.13
    n = 0.85
    return k * (fc**n)
