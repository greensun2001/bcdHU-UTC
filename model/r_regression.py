import random
import numpy as np
import pandas as pd
from model.r_ai_n import *
from scipy.optimize import curve_fit
import sklearn.metrics as metrics
import matplotlib.pyplot as plt


def _metrics_results(y, yhat):
    r2 = metrics.r2_score(y, yhat)
    mape = metrics.mean_absolute_percentage_error(y, yhat)
    smape = np.mean(2 * np.abs((y - yhat) / (y + yhat)))
    return mape, smape, r2


def _genMonteCarlo(
    conc: Conc_AI,
    seed_code=1,
    ntimes: int = 5,
    nsets: int = 400,
    fcr: tuple = (20, 180),
    wr: tuple = (0.01, 1.6),
    agr: tuple = (16, 32),
    pvr: tuple = (0.1, 1),
):
    """
    randomize survey/train data n_times times, and nsets for each time
    >> tuple for a variable (min,max)

    return a dataframe of (fcs,ws,ags,pvs)
    """

    def cal_ts(row):
        conc.fc = row["fc"]
        conc.ag = row["ag"]
        conc.pv = row["pv"]
        (
            ns_ai,
            ts_ai,
            ns_ai_c,
            ts_ai_c,
            ns_ai_f,
            ts_ai_f,
            ns,
            ts,
            ns_fr,
            ts_fr,
            delta,
        ) = conc.calMaxStresses_all(w=row["w"])
        return ts

    dataset = []
    fcs, ws, ags, pvs = [], [], [], []

    fc0 = fcr[0]
    stepfc = fcr[1] - fcr[0]

    w0 = wr[0]
    stepw = wr[1] - wr[0]

    ag0 = agr[0]
    stepag = agr[1] - agr[0]

    pv0 = pvr[0]
    steppv = pvr[1] - pvr[0]

    for time in range(ntimes):
        n = (time + 1) * seed_code
        # fc
        random.seed(1 * n)
        for i in range(nsets):
            fc = random.random() * stepfc + fc0
            fcs.append(fc)
        # w
        random.seed(2 * n)
        for i in range(nsets):
            w = random.random() * stepw + w0
            ws.append(w)
        # ag
        random.seed(3 * n)
        for i in range(nsets):
            ag = random.random() * stepag + ag0
            ags.append(ag)
        # pv
        random.seed(4 * n)
        for i in range(nsets):
            pv = random.random() * steppv + pv0
            pvs.append(pv)

    dataset = list(zip(fcs, ws, ags, pvs))
    df = pd.DataFrame(dataset, columns=["fc", "w", "ag", "pv"])
    df["ts"] = df.apply(cal_ts, axis=1)
    # df.to_excel("MC.xlsx")
    return (
        (
            df["fc"].to_numpy(dtype=np.float64),
            df["ag"].to_numpy(dtype=np.float64),
            df["pv"].to_numpy(dtype=np.float64),
            df["w"].to_numpy(dtype=np.float64),
        ),
        df["ts"].to_numpy(),
    )


def _orient_funcC(X, C: float):
    fcs, ags, pvs, ws = X
    if C > 0:
        numerator = np.sqrt(fcs) * (1 - 2 * ws / ags)
        denominator = 0.31 * (1 + C * (1 - pvs))
        y = numerator / denominator
        return y
    else:
        y = ws * 0
        return y


def orient_funcA(C: float):
    def wrapperA(X, A: float):
        fcs, ags, pvs, ws = X
        B = 16 - A
        if B > 0:
            numerator = np.sqrt(fcs) * (1 - 2 * ws / ags)
            denominator = 0.31 * (1 + C * (1 - pvs)) + 24 * ws / (pvs * (ags + A) + B)
            y = numerator / denominator
            return y
        else:
            y = ws * 0
            return y

    return wrapperA


def fit2C(
    conc: Conc_AI,
    fcr: tuple = (20, 180),
    wr: tuple = (0.005, 0.04),
    agr: tuple = (16, 32),
    pvr: tuple = (0.1, 1),
    ntimes: int = 5,
    nsets: int = 400,
    seed_code=1,
):
    X_trainC, y_trainC = _genMonteCarlo(
        conc,
        seed_code=seed_code,
        fcr=fcr,
        wr=wr,
        agr=agr,
        pvr=pvr,
        ntimes=ntimes,
        nsets=nsets,
    )

    popt, pcov = curve_fit(_orient_funcC, X_trainC, y_trainC)
    C = popt[0]
    yhat_trainC = _orient_funcC(X_trainC, C)
    mape, smape, r2 = _metrics_results(y_trainC, yhat_trainC)

    return C, mape, smape, r2


def fit2A(
    conc: Conc_AI,
    fcr: tuple = (20, 180),
    wr: tuple = (0.01, 1.6),
    agr: tuple = (16, 32),
    pvr: tuple = (0.1, 1),
    ntimes: int = 5,
    nsets: int = 400,
    seed_code=10,
    C=0.5,
):
    X_trainA, y_trainA = _genMonteCarlo(
        conc, seed_code=seed_code, fcr=fcr, wr=wr, agr=agr, pvr=pvr
    )

    ort_funcA = orient_funcA(C)
    popt, pcov = curve_fit(ort_funcA, X_trainA, y_trainA)
    A0 = popt[0]

    yhat_trainA = ort_funcA(X_trainA, A0)
    mape0, smape0, r2_0 = _metrics_results(y_trainA, yhat_trainA)

    A = 8
    x = X_trainA[3]
    yhat_trainA = ort_funcA(X_trainA, A)
    mape8, smape8, r2_8 = _metrics_results(y_trainA, yhat_trainA)

    return A0, mape0, smape0, r2_0, mape8, smape8, r2_8


def test_MonteCarlo(
    conc: Conc_AI,
    wr: tuple = (0.01, 1.6),
    agr: tuple = (10, 32),
    pvr: tuple = (0.1, 1),
    fcr: tuple = (30, 140),
    ntimes: int = 5,
    nsets: int = 400,
    seed_code=1000,
    C=0.5,
    A=8,
):
    # TESTING DATA
    ort_funcA = orient_funcA(C=C)
    X_test, y_test = _genMonteCarlo(
        conc=conc,
        seed_code=seed_code,
        ntimes=ntimes,
        nsets=nsets,
        fcr=fcr,
        wr=wr,
        agr=agr,
        pvr=pvr,
    )
    yhat_test1 = ort_funcA(X_test, A)
    mape, smape, r2 = _metrics_results(y_test, yhat_test1)

    # VISUALIZATION
    x = X_test[3]
    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(111)
    ax1.scatter(
        x,
        y_test,
        # facecolors="none",
        # edgecolors="r",
        color="red",
        label="Revised theory",
        alpha=0.35,
        marker="o",
        s=20,
    )
    ax1.scatter(
        x,
        yhat_test1,
        facecolors="none",
        edgecolors="green",
        # color="green",
        label="Eq (23)",
        alpha=0.4,
        marker="D",
        s=15,
    )
    ax1.legend(
        loc="upper center",
        fontsize=10,
        frameon=True,
        bbox_to_anchor=(0.5, 1.2),
        fancybox=True,
        ncol=2,
    )
    ymin, ymax = plt.ylim()
    ax1.text(
        1,
        ymax + 1.2,
        f"MAPE = {mape:.3f}, sMAPE = {smape:.3f}",
        color="green",
        horizontalalignment="left",
        verticalalignment="center",
        fontsize=10,
        fontweight="bold",
    )
    ax1.set_xlabel("w (mm)")
    ax1.set_ylabel("$τ_{max}$ (N/$mm^2)$")
    ax1.grid(alpha=0.5)

    fig2 = plt.figure(figsize=(8, 4))
    ax2 = fig2.add_subplot(111)
    ax2.set_xlabel("Revised theory")
    ax2.set_ylabel("Predicted by Eq (23)")
    ax2.scatter(
        y_test,
        yhat_test1,
        facecolors="none",
        edgecolors="blue",
        # color="green",
        label="",
        alpha=0.2,
        marker="o",
        s=10,
    )
    h1 = y_test.max()
    v1 = yhat_test1.max()

    ax2.plot([0, h1], [0, v1], color="red", linewidth=2, alpha=0.3)

    return mape, smape, r2, fig, fig2
