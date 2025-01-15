import streamlit as st
from page_contents.input_components import (
    ags_input,
    conc_input,
    pvs_input,
    ws_deltas_input,
)
from model.r_ai_n import *
from model.r_ai_mcft import *
import pandas as pd
import matplotlib.pyplot as plt
from supp_funcs import colorBetween, randColor, randMarker


def pg000_f00(conc: Conc_AI):
    with st.expander("Input information"):
        conc, conc_name = conc_input(conc, key="conc_in_pg000_f00")
        ws, deltas = ws_deltas_input(key="ws_deltas_in_pg000_f00")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        bt000_00 = st.button(
            "Get the result",
            use_container_width=True,
            type="primary",
        )

    if bt000_00:
        with st.status("Running", expanded=True):
            df: pd.DataFrame = AI_Calculate.calStress_w_delta(
                conc=conc, ws=ws, deltas=deltas
            )
            st.success(f"  For w in {np.round(ws,2).tolist()}")

        st.divider()

        # visualize data
        def create_fig(retType1="ts", retType2="ns"):
            fig = plt.figure(f"{conc_name}: {retType1} and {retType2}", figsize=(6, 7))
            # >> set limits for visualization
            limits = [0, 2, 0, 20]
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.axis(limits)
            ax1.set_title(
                f"{conc.repr_info()}", fontsize=8, pad=60, loc="center", color="blue"
            )
            ax1.set_facecolor("#f6faf8")
            ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
            ax2.axis(limits)
            ax2.invert_yaxis()
            ax2.set_facecolor("#fdfdf5")
            colors = colorBetween(0, 0.5, 1, 1, 0, 0, len(ws))
            for i, w in enumerate(ws):
                dfw = df.loc[df["w"] == w]
                xmax = dfw["delta"].max() + 0.02
                ymax1 = dfw[retType1].max()
                ymax2 = dfw[retType2].max()
                c = colors[i]
                ax1.plot(
                    dfw["delta"],
                    dfw[retType1],
                    color=c,
                    alpha=1,
                    linewidth=i * 0.1 + 1,
                    label=f"w : {w:.2f}",
                )
                ax1.text(
                    xmax,
                    ymax1,
                    f"w : {w:.2f}",
                    fontsize=6.5,
                    verticalalignment="center",
                    color=c,
                )
                ax2.plot(
                    dfw["delta"],
                    dfw[retType2],
                    color=c,
                    alpha=1,
                    linewidth=i * 0.1 + 1,
                    label=f"w : {w:.2f}",
                )
                ax2.text(
                    xmax,
                    ymax2,
                    f"w : {w:.2f}",
                    fontsize=6.5,
                    verticalalignment="center",
                    color=c,
                )

            ax2.set_xlabel("Δ (mm)", fontsize=8)
            ax1.set_ylabel(f"{retType1}" + r"$_{w}$ " + r"$(N/mm^2)$", fontsize=8)
            ax2.set_ylabel(f"{retType2}" + r"$_{w}$ " + r"$(N/mm^2)$", fontsize=8)

            ax1.grid(alpha=0.2)
            ax2.grid(alpha=0.2)

            ax1.legend(
                ncol=(len(ws) + 1) // 2,
                loc="lower center",
                fontsize=8,
                fancybox=True,
                shadow=False,
                bbox_to_anchor=(0.5, 1.05),
            )

            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax1.get_yticklabels(), fontsize=8)
            plt.setp(ax2.get_xticklabels(), fontsize=8)
            plt.setp(ax2.get_yticklabels(), fontsize=8)

            plt.tight_layout()
            plt.subplots_adjust(hspace=0, wspace=10)
            return fig

        # ai by fine agg
        with st.expander("AI by Fine aggregates"):
            fig = create_fig(retType1="ts_ai_f", retType2="ns_ai_f")
            st.pyplot(fig=fig)
        # ai by coarse agg
        with st.expander("AI by Coarse aggregates"):
            fig = create_fig(retType1="ts_ai_c", retType2="ns_ai_c")
            st.pyplot(fig=fig)
        # ai by all agg
        with st.expander("AI by All aggregates"):
            fig = create_fig(retType1="ts_ai", retType2="ns_ai")
            st.pyplot(fig=fig)
        # macro shear friction
        with st.expander("Macro shear friction"):
            fig = create_fig(retType1="ts_fr", retType2="ns_fr")
            st.pyplot(fig=fig)
        # shear friction: AI + Macro shear friction
        st.write("### Total shear friction")
        fig = create_fig(retType1="ts", retType2="ns")
        st.pyplot(fig=fig)


def pg000_f01(conc: Conc_AI):
    with st.expander("Input information"):
        conc, conc_name = conc_input(
            conc, b_pv=False, b_pvf=False, key="conc_in_pg000_f01"
        )
        pvs = pvs_input(key="pvs_in_pg000_f01")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        bt000_01 = st.button(
            "Get the result",
            use_container_width=True,
            type="primary",
        )
    if bt000_01:
        with st.status("Running", expanded=True):
            ws = np.linspace(0.100, 1.600, 15, endpoint=True)
            deltas = np.linspace(0.000, 2.000, 20, endpoint=True)

            elev = 37
            azim = 215
            fig_n = plt.figure(
                figsize=(6.5, 4),
                num="Visualization of surveyed test data - normal stresses",
            )

            axes_n = fig_n.add_subplot(111, projection="3d")
            # axes_n.view_init(16, 64)
            axes_n.view_init(elev=elev, azim=azim)
            axes_n.tick_params(axis="both", labelsize=8, colors="blue")
            axes_n.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
            axes_n.xaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
            axes_n.zaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))

            fig_t = plt.figure(
                figsize=(6.5, 4),
                num="Visualization of surveyed test data - shear stresses",
            )

            axes_t = fig_t.add_subplot(111, projection="3d")
            # axes_t.view_init(16, 64)
            axes_t.view_init(elev=elev, azim=azim)
            axes_t.tick_params(axis="both", labelsize=8, colors="blue")
            axes_t.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
            axes_t.xaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
            axes_t.zaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))

            l_pv = pvs.tolist()

            for index, p_v in enumerate(l_pv):
                conc.pv = p_v
                df = pd.DataFrame(columns=["w", "delta", "ns", "ts"])
                # run every case in (ws, deltas)
                i = 0
                for w in ws:
                    for delta in deltas:
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
                        ) = conc.calStresses_all(w=w, delta=delta)
                        df.loc[i, "w"] = w
                        df.loc[i, "delta"] = delta
                        df.loc[i, "ns"] = ns
                        df.loc[i, "ts"] = ts
                        i += 1

                # visualize the results
                alpha1 = 1
                alpha2 = 0.45  # 0.5 - p_v * 0.25
                cl = randColor(index)
                mk = randMarker(index)
                loc = len(deltas) - 1

                y = df["w"].astype(dtype=np.float64)
                x = df["delta"].astype(dtype=np.float64)
                z_n = df["ns"].astype(dtype=np.float64)

                axes_n.scatter(
                    x.iloc[loc],
                    y.iloc[loc],
                    z_n.iloc[loc],
                    linewidth=1,
                    color=cl,
                    label="$p_v$" + f" = {conc.pv:.2f}",
                    s=25,
                    alpha=alpha1,
                    marker=mk,
                )
                axes_n.plot_trisurf(x, y, z_n, color=cl, alpha=alpha2)

                z_t = df["ts"].astype(dtype=np.float64)
                axes_t.scatter(
                    x.iloc[loc],
                    y.iloc[loc],
                    z_t.iloc[loc],
                    linewidth=1,
                    color=cl,
                    label="$p_v$" + f" = {conc.pv:.2f}",
                    s=25,
                    alpha=alpha1,
                    marker=mk,
                )
                axes_t.plot_trisurf(x, y, z_t, color=cl, alpha=alpha2)
            min_n = df["ns"].min()
            max_n = df["ns"].max()
            min_t = df["ts"].min()
            max_t = df["ts"].max()
            axes_t.set_ylabel("w (mm)", fontsize=8)
            axes_t.set_xlabel("$Δ$ (mm)", fontsize=8)
            axes_t.set_zlabel("Shear stress (N/$mm^2)$", fontsize=8)
            # axes_t.set_zlim(0.3, max_t)
            axes_t.set_zlim(0.3, 20)
            axes_t.set_xlim(-0.2, 2)
            axes_t.set_ylim(-0.1, 1.6)
            axes_t.tick_params(axis="x", labelrotation=90, pad=-4)
            axes_t.tick_params(axis="y", labelrotation=90, pad=-4)

            axes_n.set_ylabel("w (mm)", fontsize=8)
            axes_n.set_xlabel("$Δ$ (mm)", fontsize=8)
            axes_n.set_zlabel("Normal stress (N/$mm^2)$", fontsize=8)
            # axes_n.set_zlim(0.2, max_n)
            axes_n.set_zlim(0.3, 20)
            axes_n.set_xlim(-0.2, 2)
            axes_n.set_ylim(-0.1, 1.6)
            axes_n.tick_params(axis="x", labelrotation=90, pad=-4)
            axes_n.tick_params(axis="y", labelrotation=90, pad=-4)

            fig_n.legend(ncol=4, loc="upper center", fontsize=8, frameon=True)
            fig_t.legend(ncol=4, loc="upper center", fontsize=8, frameon=True)
            # fig_n.tight_layout()
            # fig_t.tight_layout()
            st.success(f"  For $p_v$ in {l_pv}")

        st.divider()
        st.write("### Shear stresses")
        st.pyplot(fig_t, use_container_width=True)
        st.write("### Normal stresses")
        st.pyplot(fig_n, use_container_width=True)


def pg000_f02(conc: Conc_AI):
    with st.expander("Input information"):
        conc, conc_name = conc_input(conc, b_ag=False, key="conc_in_pg000_f02")
        ags = ags_input(key="ags_in_pg000_f02")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        bt000_02 = st.button(
            "Get the result",
            use_container_width=True,
            type="primary",
        )
    if bt000_02:
        with st.status("Running", expanded=True):
            # code
            # make an array of crack width values
            ws = np.linspace(0.01, 4, 100, endpoint=True)  # 0.01 to 4

            # plt.figure(conc.__str__())
            fig = plt.figure()
            a1 = fig.add_subplot(111)
            # calculate and visualize data for concretes
            concW = deepcopy(conc)
            concW.pv = 1
            for index, ag in enumerate(ags):
                conc.ag = ag
                concW.ag = ag
                df = pd.DataFrame(
                    columns=["w", "delta_m", "tsW", "ts_ai_c", "ts_ai_f", "ts_fr", "ts"]
                )
                i = 0
                for w in ws:
                    df.loc[i, "w"] = w
                    # Walraven with pv=1
                    _, tsW, _, _, _, _, _ = concW.calMaxStresses_ai(w=w)
                    df.loc[i, "tsW"] = tsW
                    # BCD
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
                    ) = conc.calMaxStresses_all(w)
                    df.loc[i, "ts_fr"] = ts_fr
                    df.loc[i, "ts_ai_c"] = ts_ai_c
                    df.loc[i, "ts_ai_f"] = ts_ai_f
                    df.loc[i, "ts"] = ts
                    df.loc[i, "delta_m"] = delta
                    i += 1

                # Walraven with pv = 1
                color = randColor(index)

                a1.plot(
                    df["w"],
                    df["tsW"],
                    label=f"{conc.ag} - Walraven",
                    linestyle=":",
                    c=color,
                )
                # for ai coarse aggregate only - bcd
                a1.plot(
                    df["w"],
                    df["ts_ai_c"],
                    label=f"{conc.ag} - ai coarse",
                    linestyle=":",
                    linewidth=3,
                    alpha=0.6,
                    c=color,
                )
                # for ai fine aggregate only - bcd
                a1.plot(
                    df["w"],
                    df["ts_ai_f"],
                    label=f"{conc.ag} - ai fine",
                    linestyle="-",
                    linewidth=2,
                    alpha=0.3,
                    c=color,
                )
                # for ai of the whole concrete - bcd
                a1.plot(
                    df["w"],
                    df["ts_fr"],
                    label=f"{conc.ag} - macro friction",
                    linestyle="-",
                    linewidth=4,
                    alpha=0.5,
                    c=color,
                )
                # for shear stress of the whole concrete - bcd
                a1.plot(
                    df["w"],
                    df["ts"],
                    label=f"{conc.ag} - shear conc",
                    linestyle="solid",
                    linewidth=1,
                    alpha=1,
                    c=color,
                )
            # limits = [0, 4, 0, 25]
            # plt.axis(limits)
            # plt.title(input('Input the title of the analysis case: '))
            a1.set_xlabel("w (mm)", fontsize=8)
            a1.set_ylabel("$τ_{max}$ " + r"$(N/mm^2)$", fontsize=8)
            a1.grid()
            a1.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.28),
                fancybox=False,
                shadow=False,
                ncol=3,
                fontsize=8,
            )
            # fig.tight_layout()
            # announcement
            st.success(f"  For $a_g$ in {ags.tolist()}")
        st.divider()
        st.pyplot(fig, use_container_width=True)


def pg000_f03(conc: Conc_AI):
    with st.expander("Input information"):
        conc, conc_name = conc_input(
            conc, b_ag=False, key="conc_in_pg000_f03", b_pv=False
        )
        ags = ags_input(key="ags_in_pg000_f03")
        pvs = pvs_input(key="pvs_in_pg000_f03")

        with st.container(border=True, key="ag_pv_in_pg000_03"):
            c1, c2 = st.columns(2)
            with c1:
                ag_choice = st.selectbox(
                    "Choose an $a_g$ for illustration",
                    ags,
                    placeholder="Click to select",
                    label_visibility="visible",
                    index=0,
                )
                if ag_choice == None:
                    ag_choice = ags[-1]
            with c2:
                pv_choice = st.selectbox(
                    "Choose an $p_v$ for illustration",
                    pvs,
                    placeholder="Click to select",
                    label_visibility="visible",
                    index=0,
                )
                if pv_choice == None:
                    pv_choice = pvs[-1]

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        bt000_03 = st.button(
            "Get the result",
            use_container_width=True,
            type="primary",
        )
    if bt000_03:
        with st.status(":rainbow[Running]", expanded=True):
            ws = np.linspace(0.01, 1.6, 100, endpoint=True)  # 0.01 to 4: 200 points

            # data processing
            concW = deepcopy(conc)  # for Walraven 1990
            concW.pv = 1
            concW0 = deepcopy(concW)  # for Walraven 1981
            concW0.sig_puCalType = 0

            # calculate data for concretes
            df = pd.DataFrame(
                columns=[
                    "ag",
                    "pv",
                    "w",
                    "ts_ai_c",
                    "ts_ai_f",
                    "ts_ai",
                    "ts",
                    "ts_fr",
                    "tsW",
                    "tsW0",
                    "ts_mcft",
                ]
            )
            i = 0
            for ag in ags:
                conc.ag = ag
                concW.ag = ag
                concW0.ag = ag
                for p_v in pvs:
                    conc.pv = p_v
                    for w in ws:
                        df.loc[i, "ag"] = ag
                        df.loc[i, "pv"] = p_v
                        df.loc[i, "w"] = w
                        # Walraven - or with pv=1
                        #   1990
                        _, tsW, _, _, _, _, _ = concW.calMaxStresses_ai(w=w)
                        df.loc[i, "tsW"] = tsW
                        #   1981
                        _, tsW0, _, _, _, _, _ = concW0.calMaxStresses_ai(w=w)
                        df.loc[i, "tsW0"] = tsW0
                        # BCD
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
                        ) = conc.calMaxStresses_all(w)
                        df.loc[i, "ts"] = ts
                        df.loc[i, "ts_fr"] = ts_fr
                        df.loc[i, "ts_ai"] = ts_ai
                        df.loc[i, "ts_ai_c"] = ts_ai_c
                        df.loc[i, "ts_ai_f"] = ts_ai_f
                        # mcft
                        df.loc[i, "ts_mcft"] = vci_mcft(conc.fc, conc.ag, w, pv=1)

                        i += 1

            # announcement
            st.success(
                f"$a_g$ in {ags.tolist()}, $p_v$ in {pvs.tolist()}, w in [{ws.min()} to {ws.max()}]",
            )

        st.write("#### :rainbow[Calculation]")
        with st.expander("Result Table"):
            st.dataframe(df, hide_index=True)

        # selected by ag
        st.write(
            f"##### :blue[Illustration for $a_g$ = {ag_choice} over $p_v$ in {pvs.tolist()}]"
        )
        df_ag_all = df.loc[df["ag"] == float(ag_choice)]
        fig_ag = plt.figure(figsize=(6.5, 3))
        aag = fig_ag.add_subplot(111)
        for id, pv in enumerate(pvs):
            df_ag = df_ag_all.loc[df["pv"] == pv].sort_values("w")
            color = randColor(id)
            aag.plot(
                df_ag["w"],
                df_ag["ts"],
                label=f"{pv} - m_2P",
                linestyle="solid",
                linewidth=1,
                alpha=1,
                c=color,
            )
            # for aggregate - Walraven pv = 1
            aag.plot(
                df_ag["w"],
                df_ag["tsW"],
                label=f"{pv} - 2P",
                linestyle=":",
                linewidth=2,
                c=color,
                alpha=1,
            )
            # for mcft
            aag.plot(
                df_ag["w"],
                df_ag["ts_mcft"],
                label=f"{pv} - MCFT",
                linestyle="--",
                linewidth=4,
                alpha=0.4,
                c=color,
            )
        aag.set_title(f"$p_v$: {pvs.tolist()}", fontsize=8)
        aag.set_xlabel("w (mm)")
        aag.set_ylabel(r"$τ_{max}$ " + r"$(N/mm^2)$")
        aag.grid()
        aag.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.35),
            fancybox=False,
            shadow=False,
            ncol=len(pvs),
            fontsize=8,
        )
        st.pyplot(fig_ag)

        # selected by pv
        st.write(
            f"##### :blue[Illustration for $p_v$ = {pv_choice} over $a_g$ in {ags.tolist()}]",
        )
        df_pv_all = df.loc[df["pv"] == float(pv_choice)]
        fig_pv = plt.figure(figsize=(6.5, 3))
        apv = fig_pv.add_subplot(111)
        for id, ag in enumerate(ags):
            df_pv = df_pv_all.loc[df["ag"] == ag].sort_values("w")
            color = randColor(id)
            apv.plot(
                df_pv["w"],
                df_pv["ts"],
                label=f"{ag} - m_2P",
                linestyle="solid",
                linewidth=1,
                alpha=1,
                c=color,
            )
            # for aggregate - Walraven pv = 1
            apv.plot(
                df_pv["w"],
                df_pv["tsW"],
                label=f"{ag} - 2P",
                linestyle=":",
                linewidth=2,
                c=color,
                alpha=1,
            )
            # for mcft
            apv.plot(
                df_pv["w"],
                df_pv["ts_mcft"],
                label=f"{ag} - MCFT",
                linestyle="--",
                linewidth=4,
                alpha=0.4,
                c=color,
            )
        apv.set_title(f"$a_g$: {ags.tolist()}", fontsize=8)
        apv.set_xlabel("w (mm)")
        apv.set_ylabel(r"$τ_{max}$ " + r"$(N/mm^2)$")
        apv.grid()
        apv.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.35),
            fancybox=False,
            shadow=False,
            ncol=len(ags),
            fontsize=8,
        )
        st.pyplot(fig_pv)
