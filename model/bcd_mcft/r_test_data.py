import pandas as pd

from model.bcd_mcft.r_beam import *
from model.bcd_mcft.r_mdl_bcdMCFT import *


def process_data(df: pd.DataFrame, fA=8, fB=8, gC=0.5, hE=2):
    """* process_dataB
    - m0: Original MCFT with pv=1, A, B, C, E=0
    - m1: MCFT based on agm with real pv, A=0, B=16, C=0, E=0
    - m2: new MCFT (by BCD) with real pv, A, B, C, E
    """
    # new columns to the dataframe
    df["m0_theta"] = None
    df["m0_b"] = None
    df["m0_s"] = None
    df["m0_w"] = None

    df["m1_theta"] = None
    df["m1_b"] = None
    df["m1_s"] = None
    df["m1_w"] = None

    df["m2_theta"] = None
    df["m2_b"] = None
    df["m2_s"] = None
    df["m2_w"] = None
    # calculate beta and shear strength
    nr = df.shape[0]
    for i in range(nr):
        # factor setting
        factors = FactorSetting()
        # run setting
        r0_setting = BCD_RunSetting()

        r1_setting = BCD_RunSetting()
        r1_setting.f_A = 0
        r1_setting.f_B = 16
        r1_setting.g_C = 0
        r1_setting.pv = df["pv"][i]

        r2_setting = NBCD_RunSetting(f_A=fA, f_B=fB, g_C=gC, h_E=hE)
        r2_setting.pv = df["pv"][i]
        # get the material data
        mat = Material(
            fc=df["fc"][i],
            e_s=df["Es"][i],
            steel_ratio=df["s_ratio"][i],
            ag=df["ag"][i],
            e_c=df["Ec"][i],
        )
        # get the geometrical data
        a = df["a"][i]
        b = df["b"][i]
        d = df["d"][i]
        geo = Geometry(a=a, b=b, d=d)

        # create beam data for the model
        m0_model = Mdl_bcdMCFT(geo, mat, factors, r0_setting)
        m1_model = Mdl_bcdMCFT(geo, mat, factors, r1_setting)
        m2_model = NMdl_bcdMCFT(geo, mat, factors, r2_setting)

        # calculate shear strength with original steel ratio
        m0_vc_s, m0_beta, m0_e1, m0_theta, m0_ex = m0_model.getShearStrength_S()
        df.loc[i, "m0_s"] = m0_vc_s
        df.loc[i, "m0_b"] = m0_beta
        df.loc[i, "m0_theta"] = m0_theta
        m0_w = d * 0.9 * m0_e1 / math.sin(m0_theta)
        df.loc[i, "m0_w"] = m0_w

        m1_vc_s, m1_beta, m1_e1, m1_theta, m1_ex = m1_model.getShearStrength_S()
        df.loc[i, "m1_theta"] = m1_theta
        df.loc[i, "m1_s"] = m1_vc_s
        df.loc[i, "m1_b"] = m1_beta
        m1_w = d * 0.9 * m1_e1 / math.sin(m1_theta)
        df.loc[i, "m1_w"] = m1_w

        m2_vc_s, m2_beta, m2_e1, m2_theta, m2_ex = m2_model.getShearStrength_S()
        df.loc[i, "m2_theta"] = m2_theta
        df.loc[i, "m2_s"] = m2_vc_s
        df.loc[i, "m2_b"] = m2_beta
        m2_w = d * 0.9 * m2_e1 / math.sin(m2_theta)
        df.loc[i, "m2_w"] = m2_w

    return df
