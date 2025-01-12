import streamlit as st
from model.r_ai_n import *
import numpy as np


def sidebar_param_setting2conc(key="sidebar_params"):
    with st.sidebar.expander(":blue[Parameter setting]", expanded=False):
        fc2fcc = st.number_input(
            "Factor for converting $f_c$ to $f_{cc}$",
            min_value=1.0,
            max_value=1.4,
            step=0.1,
            value=1.2,
            key=f"{key}_fc2fcc",
        )
        shape_factor = st.number_input(
            "Factor for shape",
            min_value=0.8,
            max_value=1.6,
            step=0.1,
            value=1.0,
            key=f"{key}_shape_factor",
        )

        cf_factor = st.number_input(
            "Macro friction factor ($C_f$)",
            min_value=0.20,
            max_value=0.50,
            step=0.05,
            value=0.35,
            key=f"{key}_cf_factor",
        )

        ls_t = ["Walravel 1980", "Walraven 1990"]
        sig_pu_cal_type_s = st.selectbox(
            "Method to calculate $σ_{pu}$",
            ls_t,
            index=1,
            key=f"{key}_sigpu_cal_type",
        )
        sig_pu_cal_type = ls_t.index(sig_pu_cal_type_s)
    conc = Conc_AI()
    conc.FACTOR_fc2fcc = round(fc2fcc, 2)
    conc.FACTOR_shape = round(shape_factor, 2)
    conc.Cf = round(cf_factor, 2)
    conc.sig_puCalType = sig_pu_cal_type
    return conc


def conc_input(
    conc: Conc_AI,
    key="conc_in",
    b_pk=True,
    b_fc=True,
    b_muy=True,
    b_ag=True,
    b_pv=True,
    b_af=True,
    b_pvf=True,
):
    with st.container(border=True, key=key):
        st.write("Concrete properties")
        # Controls
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            name = st.text_input("Name", key=f"{key}_name", value="concrete1")
            conc.pk = st.number_input(
                "Agg volume ratio ($p_k$)",
                min_value=0.05,
                max_value=1.00,
                step=0.05,
                value=0.75,
                disabled=not (b_pk),
                key=f"{key}_pk",
            )
        with c2:
            conc.fc = st.number_input(
                "Comp strength ($f_c$)",
                min_value=15.00,
                max_value=200.00,
                step=5.00,
                value=40.00,
                disabled=not (b_fc),
                key=f"{key}_fc",
            )
            conc.muy = st.number_input(
                "Agg-matrix friction ($μ$)",
                min_value=0.05,
                max_value=1.00,
                step=0.05,
                value=0.40,
                disabled=not (b_muy),
                key=f"{key}_muy",
            )
        with c3:
            conc.ag = st.number_input(
                "Coarse size ($a_g$)",
                min_value=6.00,
                max_value=32.00,
                step=1.00,
                value=20.00,
                disabled=not (b_ag),
                key=f"{key}_ag",
            )
            conc.pv = st.number_input(
                "Unbroken coarse ($p_v$)",
                min_value=0.00,
                max_value=1.00,
                step=0.10,
                value=1.00,
                disabled=not (b_pv),
                key=f"{key}_pv",
            )
        with c4:
            conc.af = st.number_input(
                "Fine size ($a_f$)",
                min_value=2.00,
                max_value=6.00,
                step=0.05,
                value=4.75,
                disabled=not (b_af),
                key=f"{key}_af",
            )
            conc.pvf = st.number_input(
                "Unbroken fine ($p_{vf}$)",
                min_value=0.10,
                max_value=1.00,
                step=0.10,
                value=1.00,
                disabled=not (b_pvf),
                key=f"{key}_pvf",
            )
    return conc, name


def ws_deltas_input(b_ws=True, b_deltas=True, key="ws_deltas_in"):
    with st.container(border=True, key=key):
        st.write("Ranges for crack width (w) and slip (Δ)")
        # Controls
        c1, c2, c3 = st.columns(3)
        with c1:
            ws_min = st.number_input(
                "w min",
                min_value=0.10,
                max_value=0.50,
                step=0.10,
                value=0.10,
                disabled=not (b_ws),
                key=f"{key}_wmin",
            )
            delta_min = st.number_input(
                "Δ min",
                min_value=0.00,
                max_value=0.10,
                step=0.01,
                value=0.00,
                disabled=not (b_deltas),
                key=f"{key}_deltamin",
            )
        with c2:
            ws_max = st.number_input(
                "w max",
                min_value=ws_min,
                max_value=2.00,
                step=0.10,
                value=1.00,
                disabled=not (b_ws),
                key=f"{key}_wmax",
            )
            delta_max = st.number_input(
                "Δ max",
                min_value=delta_min,
                max_value=4.00,
                step=0.10,
                value=2.00,
                disabled=not (b_deltas),
                key=f"{key}_deltamax",
            )
        with c3:
            ws_step = st.number_input(
                "w step",
                min_value=0.05,
                max_value=0.5,
                step=0.05,
                value=0.10,
                disabled=not (b_ws),
                key=f"{key}_wstep",
            )
            delta_step = st.number_input(
                "Δ step",
                min_value=0.01,
                max_value=0.50,
                step=0.005,
                value=0.02,
                disabled=not (b_deltas),
                key=f"{key}_deltastep",
            )
    ws = np.arange(start=ws_min, stop=ws_max * 1.000001, step=ws_step)
    deltas = np.arange(start=delta_min, stop=delta_max * 1.000001, step=delta_step)
    return ws, deltas


def pvs_input(key="pvs_in"):
    with st.container(border=True, key=key):
        st.write("Surveyed range of [$p_v$]")
        c1, c2, c3 = st.columns(3)
        with c1:
            pv_min = st.number_input(
                "$p_v$ min",
                min_value=0.00,
                max_value=1.00,
                step=0.10,
                value=0.00,
                key=f"{key}_pvmin",
            )
        with c2:
            pv_max = st.number_input(
                "$p_v$ max",
                min_value=pv_min,
                max_value=1.00,
                step=0.10,
                value=1.00,
                key=f"{key}_pvmax",
            )
        with c3:
            pv_step = st.number_input(
                "$p_v$ step",
                min_value=0.10,
                max_value=1.00,
                step=0.05,
                value=0.3,
                key=f"{key}_pvstep",
            )
    pvs0 = np.arange(start=pv_min, stop=pv_max * 1.000001, step=pv_step)
    pvs = np.round(pvs0, 2)
    return pvs


def ags_input(key="ags_in"):
    with st.container(border=True, key=key):
        st.write("Surveyed range of [$a_g$]")
        c1, c2, c3 = st.columns(3)
        with c1:
            ag_min = st.number_input(
                "$a_g$ min",
                min_value=6.00,
                max_value=32.00,
                step=1.00,
                value=8.00,
                key=f"{key}_agmin",
            )
        with c2:
            ag_max = st.number_input(
                "$a_g$ max",
                min_value=ag_min,
                max_value=32.00,
                step=1.00,
                value=32.00,
                key=f"{key}_agmax",
            )
        with c3:
            ag_step = st.number_input(
                "$a_g$ step",
                min_value=1.00,
                max_value=16.00,
                step=1.00,
                value=12.00,
                key=f"{key}_agstep",
            )
    ags0 = np.arange(start=ag_min, stop=ag_max * 1.000001, step=ag_step)
    ags = np.round(ags0, 2)
    return ags


def sidebar_m_mcft_params(
    key="sidebar_mmcft_params",
):
    with st.sidebar.expander(":blue[Parameters for m_MCFT]", expanded=True):
        col1, col2 = st.columns(2)
        pA = col1.slider(label="Parameter A", min_value=0, max_value=15, value=8)
        pB = col2.slider(label="Parameter B", value=16 - pA, disabled=True)
        pC = col1.slider(
            label="Parameter C", min_value=0.0, max_value=2.0, value=0.5, step=0.1
        )
        pE = col2.slider(label="Parameter E", min_value=0, max_value=10, value=2)
        return pA, pB, pC, pE


def m_mcft_params(
    key="mmcft_params",
):
    with st.expander(":blue[Parameters for m_MCFT]", expanded=True):
        c1, c2, c3, c4 = st.columns(4, gap="large")
        pA = c1.slider(label="Parameter A", min_value=0, max_value=15, value=8)
        pB = c2.slider(label="Parameter B", value=16 - pA, disabled=True)
        pC = c3.slider(
            label="Parameter C", min_value=0.0, max_value=2.0, value=0.5, step=0.1
        )
        pE = c4.slider(label="Parameter E", min_value=0, max_value=10, value=2)
        return pA, pB, pC, pE


def mc_regr_input(
    key="mc_regr_in",
    fcmin=15,
    fcmax=200,
    fc1=20,
    fc2=180,
    fcstep=5,
    agmin=10,
    agmax=40,
    ag1=16,
    ag2=32,
    agstep=2,
    pvmin=0.00,
    pvmax=1.00,
    pv1=0.10,
    pv2=1.00,
    pvstep=0.10,
    wmin=0.001,
    wmax=2.000,
    w1=0.005,
    w2=0.040,
    wstep=0.001,
):
    with st.container(border=True, key=key):
        c1, c2, c3, c4 = st.columns(4, gap="large")
        vfc1, vfc2 = c1.slider(
            "f$_c$ range",
            min_value=fcmin,
            max_value=fcmax,
            value=(fc1, fc2),
            key=f"{key}_fc",
            step=fcstep,
        )
        vag1, vag2 = c2.slider(
            "$a_g$ range",
            min_value=agmin,
            max_value=agmax,
            value=(ag1, ag2),
            key=f"{key}_ag",
            step=agstep,
        )
        vpv1, vpv2 = c3.slider(
            "p$_v$ range",
            min_value=pvmin,
            max_value=pvmax,
            value=(pv1, pv2),
            key=f"{key}_pv",
            step=pvstep,
            format="%f",
        )
        vw1, vw2 = c4.slider(
            "w range",
            min_value=wmin,
            max_value=wmax,
            value=(w1, w2),
            step=wstep,
            format="%f",
        )
        return vfc1, vfc2, vag1, vag2, vpv1, vpv2, vw1, vw2


def sidebar_mc_params(key="mc_sim_parms"):
    with st.sidebar.expander(":blue[Params for Monte Carlo]", expanded=True):
        col1, col2 = st.columns(2)
        ntimes = col1.slider(
            label="Number of times",
            min_value=5,
            max_value=200,
            value=5,
            step=5,
            key=f"{key}_ntimes",
        )
        nsets = col2.slider(
            label="Number of sets",
            min_value=50,
            max_value=5000,
            value=50,
            step=50,
            key=f"{key}_nsets",
        )
        return ntimes, nsets
