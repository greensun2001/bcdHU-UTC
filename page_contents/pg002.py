import streamlit as st
import pandas as pd
from page_contents.input_components import sidebar_m_mcft_params
from model.bcd_mcft.r_test_data import process_data
import numpy as np
import plotly.graph_objects as go


def pg002_f00():
    pA, pB, pC, pE = sidebar_m_mcft_params()

    """get the data sample format"""
    df_sample = pd.read_csv("data/data_sample_u8.csv")
    vip_cols = ["a", "b", "d", "fc", "Es", "ag", "Ec", "pv", "s_ratio"]
    df0 = df_sample[vip_cols]
    data_name = "sample data"

    with st.expander("### :rainbow[Data Sample]"):
        st.write("The data file must have data with columns as below")
        st.dataframe(data=df0.head(2), hide_index=True, use_container_width=True)

    st.sidebar.subheader("Select the data file", divider="rainbow")

    uploaded_file = st.sidebar.file_uploader(
        "Please select a csv file",
        key="upfile1",
        type="csv",
        help="",
        label_visibility="collapsed",
    )
    if uploaded_file is not None:
        with st.expander(":blue[Selected Data Table]"):
            df1 = pd.read_csv(uploaded_file)
            if set(vip_cols).issubset(df1.columns):
                data_name = uploaded_file.name
                df = df1
                st.write("The format of data file is correct")
                st.dataframe(data=df, hide_index=True, height=300)
    else:
        df = df_sample

    st.sidebar.write(":green[Selected file: ]", data_name)
    col1, col2 = st.columns([2, 0.5])
    with col1:
        st.write(":gray[*(if no file was selected, sample data will be used)*]")
    with col2:
        btnRun = st.button(
            "Run prediction",
            key="pg002_f00_btnRun",
            type="primary",
            use_container_width=True,
        )
    if btnRun:
        s0 = "    - m0 - Original MCFT with "
        s1 = "    - m1 - MCFT based on $a_{gm}$ with "
        s2 = "    - m2 - new MCFT by BCD with "
        st.write(s0, " $p_v$ ", 1, ", A ", 8, ", B ", 8, ", C ", 0.5, ", E ", 0)
        st.write(s1, " :blue[real $p_v$] ", ", A ", 0, ", B ", 16, ", C ", 0, ", E ", 0)
        st.write(
            s2,
            " :blue[real $p_v$] ",
            ", :red[**A**] ",
            pA,
            ", :red[**B**] ",
            pB,
            ", :red[**C**] ",
            pC,
            ", :red[**E**] ",
            pE,
        )

        df_ret = process_data(df=df, fA=pA, fB=pB, gC=pC, hE=pE)

        st.subheader("Result Table", divider="rainbow")
        st.dataframe(df_ret, hide_index=True)
        # compare with experiment
        if "shear_s_exp" in df_ret.columns:
            df_compare = df_ret.copy()
            df_compare["m0_safe"] = (
                df_compare["shear_s_exp"] / df_compare["m0_s"]
            ) > 0.9
            df_compare["m1_safe"] = (
                df_compare["shear_s_exp"] / df_compare["m1_s"]
            ) > 0.9
            df_compare["m2_safe"] = (
                df_compare["shear_s_exp"] / df_compare["m2_s"]
            ) > 0.9
            df_compare["b_exp"] = df_compare["shear_s_exp"] / np.sqrt(df_compare["fc"])
            df_compare["b_m0"] = df_compare["m0_s"] / np.sqrt(df_compare["fc"])
            df_compare["b_m1"] = df_compare["m1_s"] / np.sqrt(df_compare["fc"])
            df_compare["b_m2"] = df_compare["m2_s"] / np.sqrt(df_compare["fc"])

            def class_d(row):
                d = row["d"]
                if d < 450:
                    s = "0 < d < 450"
                elif d < 700:
                    s = "450 < d < 700"
                else:
                    s = "d > 700"
                return s

            df_compare["d_class"] = df_compare.apply(class_d, axis=1)

            def class_pv(row):
                if row["pv"] > 0.55:
                    s = "pv > 0.55"
                else:
                    s = "0 < pv < 0.55"
                return s

            df_compare["pv_class"] = df_compare.apply(class_pv, axis=1)

            df_chart = df_compare[
                [
                    "d_class",
                    "pv_class",
                    "b_exp",
                    "b_m0",
                    "b_m1",
                    "b_m2",
                    "m0_safe",
                    "m1_safe",
                    "m2_safe",
                ]
            ]
            st.subheader("Compared with experimental results", divider="rainbow")
            st.write("##### :blue[Comparison table]")
            st.dataframe(df_chart)

            st.write("##### :blue[Beta factors]")
            df_chart_beta = df_chart.groupby(
                ["d_class", "pv_class"], as_index=False
            ).agg({"b_exp": "mean", "b_m0": "mean", "b_m1": "mean", "b_m2": "mean"})
            st.dataframe(df_chart_beta)

            x = [df_chart_beta["d_class"], df_chart_beta["pv_class"]]
            fig_beta = go.Figure()
            fig_beta.add_bar(
                x=x, y=df_chart_beta["b_exp"], name="experiment", marker_color="red"
            )
            fig_beta.add_bar(
                x=x, y=df_chart_beta["b_m0"], name="m0", marker_color="pink"
            )
            fig_beta.add_bar(
                x=x, y=df_chart_beta["b_m1"], name="m1", marker_color="green"
            )
            fig_beta.add_bar(
                x=x, y=df_chart_beta["b_m2"], name="m2", marker_color="blue"
            )
            fig_beta.update_layout(
                barmode="group",
                legend=dict(
                    yanchor="top",
                    y=1.15,
                    xanchor="center",
                    x=0.5,
                    borderwidth=1,
                    bordercolor="#c3c0c0",
                ),
                legend_orientation="h",
            )
            st.plotly_chart(fig_beta)

            st.write("##### :blue[Safe design results]")
            df_chart_safe = df_chart.groupby(
                ["d_class", "pv_class"], as_index=False
            ).agg(
                num=("m0_safe", "count"),
                m0=("m0_safe", "sum"),
                m1=("m1_safe", "sum"),
                m2=("m2_safe", "sum"),
            )
            s_num = df_chart_safe.num.sum()
            s_m0 = df_chart_safe.m0.sum()
            s_m1 = df_chart_safe.m1.sum()
            s_m2 = df_chart_safe.m2.sum()
            df_chart_safe.loc[len(df_chart_safe.index)] = [
                "All",
                "",
                s_num,
                s_m0,
                s_m1,
                s_m2,
            ]
            st.dataframe(df_chart_safe)

            x = [df_chart_safe["d_class"], df_chart_safe["pv_class"]]
            fig_safe = go.Figure()
            fig_safe.add_bar(
                x=x,
                y=100 * df_chart_safe.m0 / df_chart_safe.num,
                name="m0",
                marker_color="pink",
            )
            fig_safe.add_bar(
                x=x,
                y=100 * df_chart_safe.m1 / df_chart_safe.num,
                name="m1",
                marker_color="green",
            )
            fig_safe.add_bar(
                x=x,
                y=100 * df_chart_safe.m2 / df_chart_safe.num,
                name="m2",
                marker_color="blue",
            )

            fig_safe.update_layout(
                barmode="group",
                legend=dict(
                    yanchor="top",
                    y=1.15,
                    xanchor="center",
                    x=0.5,
                    borderwidth=1,
                    bordercolor="#c3c0c0",
                ),
                legend_orientation="h",
            )
            st.plotly_chart(fig_safe)
