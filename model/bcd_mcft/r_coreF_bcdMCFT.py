import math
import inspect
from model.bcd_mcft.r_eng_support import *
from model.bcd_mcft.r_beam import *


# CONSTANTS
class Const:
    EPS_TOR = 0.001
    RELATIVE_STEP_E1 = 0.01


def get_beta(e1: float, theta: float):
    # according Eq.19 - MCFT
    beta = 0.33 / math.tan(theta)
    beta = beta / (1 + math.sqrt(500 * e1))
    return beta


def e1_theta(ex: float, e1: float):
    # according Eq.26 - MCFT
    try:
        a = 1 / (15000 * (1 + math.sqrt(500 * e1)))
        b = ex
        c = ex - e1
        l = quadratic_eq(a, b, c)
        t = max(l)
        theta = math.atan(1 / math.sqrt(t))
        return theta
    except Exception as e:
        raise Exception("e1_theta")
        # print(f"Exception with {inspect.stack()[0][3]}: {e}")
        # print(f"temp rets: ex={ex}, e1={e1}")


def gen_e1theta_func(ex: float, func):
    def wrapper(e1: float):
        return func(ex, e1)

    return wrapper


def theta_e1(g: float, sxe: float, theta: float):
    # according Eq.23 - MCFT
    try:
        a = 1.258 * sxe / math.sin(theta)
        b = -math.sqrt(500) * math.tan(theta)
        c = 0.568 * g - math.tan(theta)
        l = quadratic_eq(a, b, c)
        t = max(l)
        e1 = t * t
        return e1

    except Exception as e:
        print(f"Exception with {inspect.stack()[0][3]}: {e}")


def gen_theta_e1_func(g: float, sxe: float, func):
    def wrapper(theta: float):
        return func(g, sxe, theta)

    return wrapper


def e23_smallleft(g: float, sxe: float, e1: float, theta: float):
    """return -1 if True, 1 if False"""
    l = (1 + math.sqrt(500 * e1)) * math.tan(theta)
    r = 0.568 * g + 1.258 * sxe * e1 / math.sin(theta)
    if l < r:
        return -1, l, r
    else:
        return 1, l, r


def ex2all(g: float, sxe: float, ex: float):
    """
    given g, sxe, and a specific ex, make the loop to get (e1, theta)
    """
    # get the initial value for e1
    step = Const.RELATIVE_STEP_E1 * ex
    st_e1 = ex + step
    o_e1 = st_e1
    theta = e1_theta(ex, o_e1)
    old_compa, l, r = e23_smallleft(g, sxe, o_e1, theta)
    # looping
    while True:
        o_e1 += old_compa * step
        theta = e1_theta(ex, o_e1)
        new_compa, l, r = e23_smallleft(g, sxe, o_e1, theta)
        if new_compa * old_compa < 0:
            step = step / 2
            diff = math.fabs((l - r) / min(l, r))
            if diff < Const.EPS_TOR:
                break
        old_compa = new_compa

    # get the results
    e1 = o_e1
    beta = get_beta(e1, theta)
    return e1, theta, beta


# FOR NEW ID ACCORDING TO EQ. 23_n


def n_theta_e1(f: float, g: float, h: float, sx: float, theta: float):
    # according Eq.23_n - BCD and MCFT
    try:
        sqrt500 = math.sqrt(500)
        sx_sin = sx / math.sin(theta)
        tanth = math.tan(theta)

        k3 = sqrt500 * h * sx_sin
        k2 = (h + 44 / f / tanth) * sx_sin
        k1 = -sqrt500
        k0 = 0.568 * g / tanth - 1
        l = polynomial_eq([k3, k2, k1, k0])
        t = max(l)
        e1 = t * t
        return e1

    except Exception as e:
        # print(f"Exception with {inspect.stack()[0][3]}: {e}")
        raise Exception("n1_theta_e1")


def gen_n_theta_e1_func(f: float, g: float, h: float, sx: float, func):
    def wrapper(theta: float):
        return func(f, g, h, sx, theta)

    return wrapper


def n_e32_L_smthan_R(f: float, g: float, h: float, sx: float, e1: float, theta: float):
    """return 1 if True, -1 if False"""
    l = 0.33 / (1 + math.sqrt(500 * e1)) / math.tan(theta)
    w = sx * e1 / math.sin(theta)
    r = 0.18 * (1 - h * w) / (0.31 * g + 24 * w / f)
    if l < r:
        return 1, l, r
    else:
        return -1, l, r


def n_ex2all(f: float, g: float, h: float, sx: float, ex: float):
    """
    given a specific ex, make the loop to get (e1, theta)
    """
    try:
        STEP_FACTOR = 1.5
        step = Const.RELATIVE_STEP_E1 * ex
        st_e1 = ex + step
        n_e1 = st_e1
        o_e1 = n_e1
        theta = e1_theta(ex, n_e1)
        new_compa, l, r = n_e32_L_smthan_R(f, g, h, sx, n_e1, theta)
        old_compa = new_compa
        # looping
        while True:
            # ** intermediate results
            # w = sx * o_e1 / math.sin(theta)
            # print(f">> e1: {n_e1}, theta: {theta}, L: {l}, R: {r}, w: {w}")
            # **
            n_e1 += old_compa * step
            theta = e1_theta(ex, n_e1)
            new_compa, l, r = n_e32_L_smthan_R(f, g, h, sx, n_e1, theta)
            if new_compa * old_compa > 0:
                step = step * STEP_FACTOR
                old_compa = new_compa
                o_e1 = n_e1
                # ** intermediate results
                # print(f"----- step: {step}")
                # **
            else:
                if old_compa > 0:
                    pos_e1, neg_e1 = o_e1, n_e1
                else:
                    pos_e1, neg_e1 = n_e1, o_e1
                # ** intermediate results
                # print("----- bi-sectional iteration")
                # **
                break

        while True:
            # ** intermediate results
            # w = sx * n_e1 / math.sin(theta)
            # print(
            #     f">> e1: {n_e1}, theta: {theta}, L: {l}, R: {r}, w: {w}, +e1: {pos_e1}, -e1: {neg_e1}"
            # )
            # **
            n_e1 = (pos_e1 + neg_e1) * 0.5
            theta = e1_theta(ex, n_e1)
            new_compa, l, r = n_e32_L_smthan_R(f, g, h, sx, n_e1, theta)
            if new_compa > 0:
                pos_e1 = n_e1
            else:
                neg_e1 = n_e1

            diff = math.fabs((l - r) / min(l, r))
            if diff < Const.EPS_TOR:
                # ** intermediate results
                # w = sx * n_e1 / math.sin(theta)
                # print(
                #     f">> found e1: {n_e1}, theta: {theta}, L: {l}, R: {r}, w: {w}, diff_e1: {diff}"
                # )
                # **
                break

        # get the results
        e1 = n_e1
        beta = get_beta(e1, theta)
        return e1, theta, beta
    except:
        return -1, -1, -1

