import streamlit as st


from model.r_ai_n import Conc_AI
from page_contents.input_components import (
    conc_input,
    sidebar_mc_params,
    mc_regr_input,
    m_mcft_params,
)
from model.r_regression import fit2A, fit2C, test_MonteCarlo


def pg001_mc_init():
    ntimes, nsets = sidebar_mc_params(key="mc_params_pg001_mc_init")
    return ntimes, nsets


def pg001_findC(conc: Conc_AI, ntimes, nsets):
    fc1, fc2, ag1, ag2, pv1, pv2, w1, w2 = mc_regr_input(
        wmin=0.001, wmax=0.050, w1=0.005, w2=0.040, wstep=0.001
    )
    c1, c2 = st.columns([2, 0.5])
    with c2:
        bt001_00 = st.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            key="btn001_00_findC",
        )
    if bt001_00:
        fcr: tuple = (fc1, fc2)
        agr: tuple = (ag1, ag2)
        pvr: tuple = (pv1, pv2)
        # find C
        st.write("### :blue[Regression to find parameter C]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            # find C
            wr: tuple = (w1, w2)
            C, mape, smape, r2 = fit2C(
                conc=conc, fcr=fcr, wr=wr, agr=agr, pvr=pvr, ntimes=ntimes, nsets=nsets
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                "$ f_c$",
                fcr,
                ". . $a_g$",
                agr,
                ". . $p_v$",
                pvr,
                ":red[. . **w**]",
                wr,
            )
        with st.container(border=True, key="pg001_f00_C"):
            st.write(f":red[**C : {C:.6f}**]")
            st.write(
                "MAPE",
                round(mape, 6),
                ". . SMAPE",
                round(smape, 6),
                ". . R2",
                round(r2, 6),
            )
            st.write(f"##### :green[C ‣ {round(C,1)}]")


def pg001_findA(conc: Conc_AI, ntimes, nsets):
    c1, c2 = st.columns([4, 1])
    with c1:
        fc1, fc2, ag1, ag2, pv1, pv2, w1, w2 = mc_regr_input(
            wmin=0.001, wmax=2.000, w1=0.010, w2=1.600, wstep=0.001
        )
    with c2:
        with st.container(key="container_gC_pg001_findA", border=True):
            gC = st.slider(
                "Constant C",
                key="gC_pg001_findA",
                min_value=0.0,
                max_value=2.0,
                value=0.5,
            )
    c1, c2 = st.columns([2, 0.5])
    with c2:
        bt001_00 = st.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            key="btn001_00_findA",
        )
    if bt001_00:
        fcr: tuple = (fc1, fc2)
        agr: tuple = (ag1, ag2)
        pvr: tuple = (pv1, pv2)
        # find A
        st.write("### :blue[Regression to find parameter A]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            wr: tuple = (w1, w2)
            C = gC
            A0, mape0, smape0, r2_0, mape8, smape8, r2_8 = fit2A(
                conc=conc,
                fcr=fcr,
                wr=wr,
                agr=agr,
                pvr=pvr,
                ntimes=ntimes,
                nsets=nsets,
                C=C,
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                "$ f_c$",
                fcr,
                ". . $a_g$",
                agr,
                ". . $p_v$",
                pvr,
                ":red[. . **w**]",
                wr,
                ":red[. . **C**]",
                C,
            )
        with st.container(border=True, key="pg001_f00_A"):
            st.write(f":red[**A : {A0:.6f}**]")
            st.write(
                "MAPE",
                round(mape0, 6),
                ". . SMAPE",
                round(smape0, 6),
                ". . R2",
                round(r2_0, 6),
            )
            st.write(f"##### :green[A ‣ 8]")
            st.write(
                "MAPE",
                round(mape8, 6),
                ". . SMAPE",
                round(smape8, 6),
                ". . R2",
                round(r2_8, 6),
            )


def pg001_MC(conc: Conc_AI, ntimes, nsets):
    fc1, fc2, ag1, ag2, pv1, pv2, w1, w2 = mc_regr_input(
        wmin=0.001,
        wmax=2.000,
        w1=0.010,
        w2=1.600,
        wstep=0.001,
        fc1=30,
        fc2=140,
        ag1=10,
    )
    pA, pB, pC, pE = m_mcft_params()
    c1, c2 = st.columns([2, 0.5])
    with c2:
        bt001_00 = st.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            key="btn001_00_mc",
        )
    if bt001_00:
        fcr: tuple = (fc1, fc2)
        agr: tuple = (ag1, ag2)
        pvr: tuple = (pv1, pv2)
        wr: tuple = (w1, w2)

        st.write("### :rainbow[Test with considered params (A, B, C, E)]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            # make the test data
            C = pC
            A = pA
            # running
            mape_test, smape_test, r2_test, fig_test, fig2 = test_MonteCarlo(
                conc=conc,
                wr=wr,
                agr=agr,
                pvr=pvr,
                fcr=fcr,
                ntimes=ntimes,
                nsets=nsets,
                C=C,
                A=A,
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                ":red[. . **$ f_c$**]",
                fcr,
                ":red[. . **$a_g$**]",
                agr,
                ":red[. . **$p_v$**]",
                pvr,
                ":red[. . **w**]",
                wr,
            )
        st.write(
            ":blue[**A**]",
            A,
            ":blue[. . **B**]",
            16 - A,
            ":blue[. . **C**]",
            C,
            ":blue[. . **E**]",
            2,
        )
        st.write(
            "MAPE",
            round(mape_test, 6),
            ". . SMAPE",
            round(smape_test, 6),
            ". . R2",
            round(r2_test, 6),
        )
        st.pyplot(fig=fig_test, use_container_width=True)
        st.pyplot(fig=fig2, use_container_width=True)


def pg001_typical_ana(conc: Conc_AI, ntimes, nsets):
    with st.expander("Input information"):
        conc, conc_name = conc_input(
            conc, key="conc_in_pg001_typical_ana", b_fc=False, b_ag=False, b_pv=False
        )

    c1, c2 = st.columns([2, 0.5])
    with c2:
        bt001_00 = st.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            key="btn001_00_typical_ana",
        )
    if bt001_00:
        fcr: tuple = (20, 180)
        agr: tuple = (16, 32)
        pvr: tuple = (0.1, 1)
        # find C
        st.write("### :blue[Regression to find parameter C]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            # find C
            wr: tuple = (0.005, 0.04)
            C, mape, smape, r2 = fit2C(
                conc=conc, fcr=fcr, wr=wr, agr=agr, pvr=pvr, ntimes=ntimes, nsets=nsets
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                "$ f_c$",
                fcr,
                ". . $a_g$",
                agr,
                ". . $p_v$",
                pvr,
                ":red[. . **w**]",
                wr,
            )
        with st.container(border=True, key="pg001_f00_C"):
            st.write(f":red[**C : {C:.6f}**]")
            st.write(
                "MAPE",
                round(mape, 6),
                ". . SMAPE",
                round(smape, 6),
                ". . R2",
                round(r2, 6),
            )
            st.write(f"##### :green[C ‣ {round(C,1)}]")
        # find A with C = 0.5
        st.write("### :blue[Regression to find parameter A]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            # find A
            wr = (0.01, 1.6)
            C = 0.5
            A0, mape0, smape0, r2_0, mape8, smape8, r2_8 = fit2A(
                conc=conc,
                fcr=fcr,
                wr=wr,
                agr=agr,
                pvr=pvr,
                ntimes=ntimes,
                nsets=nsets,
                C=C,
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                "$ f_c$",
                fcr,
                ". . $a_g$",
                agr,
                ". . $p_v$",
                pvr,
                ":red[. . **w**]",
                wr,
                ":red[. . **C**]",
                C,
            )
        with st.container(border=True, key="pg001_f00_A"):
            st.write(f":red[**A : {A0:.6f}**]")
            st.write(
                "MAPE",
                round(mape0, 6),
                ". . SMAPE",
                round(smape0, 6),
                ". . R2",
                round(r2_0, 6),
            )
            st.write(f"##### :green[**A ‣ 8.0**]")
            st.write(
                "MAPE",
                round(mape8, 6),
                ". . SMAPE",
                round(smape8, 6),
                ". . R2",
                round(r2_8, 6),
            )
        # Monte Carlo Simulation for Testing
        st.write("### :rainbow[Test with considered params (A, B, C, E)]")
        with st.status(":rainbow[Monte Carlo Simulation]", expanded=True):
            # make the test data
            wr = (0.01, 1.6)
            agr = (10, 32)
            pvr = (0.1, 1)
            fcr = (30, 140)
            nsets = 400
            C = 0.5
            A = 8
            # running
            mape_test, smape_test, r2_test, fig_test, fig2 = test_MonteCarlo(
                conc=conc,
                wr=wr,
                agr=agr,
                pvr=pvr,
                fcr=fcr,
                ntimes=ntimes,
                nsets=nsets,
                C=C,
                A=A,
            )
            st.write("ntimes", ntimes, ". . nsets", nsets)
            st.write(
                ":red[. . **$ f_c$**]",
                fcr,
                ":red[. . **$a_g$**]",
                agr,
                ":red[. . **$p_v$**]",
                pvr,
                ":red[. . **w**]",
                wr,
            )
        st.write(
            ":blue[**A**]",
            A,
            ":blue[. . **B**]",
            16 - A,
            ":blue[. . **C**]",
            C,
            ":blue[. . **E**]",
            2,
        )
        st.write(
            "MAPE",
            round(mape_test, 6),
            ". . SMAPE",
            round(smape_test, 6),
            ". . R2",
            round(r2_test, 6),
        )
        st.pyplot(fig=fig_test, use_container_width=True)
        st.pyplot(fig=fig2, use_container_width=True)
