from dataclasses import dataclass, field, asdict
from math import sqrt, asin, pi
from typing import Self
from scipy import integrate
from copy import deepcopy
import pandas as pd
import numpy as np


def f(d: float, af: float) -> float:
    """
    The F function is only valid if d < af < 0. Otherwise, it will be set to zero
    """
    if af > 0:
        if d > af:
            return 0
        else:
            x = d / af
            ret = 0.727 * (x**0.5) - x**2
            ret += 0.144 * (x**4) + 0.036 * (x**6)
            ret += 0.016 * (x**8) + 0.01 * (x**10)
            if ret < 0:
                ret = 0
            return ret
    else:
        return 0


def supf(d: float, w: float, delta: float) -> float:
    sq_dspl = w * w + delta * delta
    ret = d * d / sq_dspl - 1
    if ret < 0:
        ret = 0
    ret = sqrt(ret)
    return ret


def umax(d: float, w: float, delta: float) -> float:
    ret = (delta * supf(d, w, delta) - w) / 2
    if ret < 0:
        ret = 0
    return ret


def g1(d: float, w: float, delta: float) -> float:
    """function to consider the growing contact"""
    try:
        um = umax(d, w, delta)
        ret = um**2
        ret = ret / (d**3)
        if ret < 0:
            ret = 0
    except:
        ret = 0
    return ret


def g2(d: float, w: float, delta: float) -> float:
    """function to consider the growing contact"""
    try:
        sf = supf(d, w, delta)
        um = umax(d, w, delta)
        ret = (delta - sf) * w * um
        ret += (um + w) * sqrt(d * d / 4 - (w + um) * (w + um))
        ret -= w * sqrt(d * d / 4 - w * w)
        ret += 0.25 * d * d * asin(2 * (um + w) / d)
        ret -= 0.25 * d * d * asin(2 * w / d)
        ret = ret / (d**3)
        if ret < 0:
            ret = 0
    except:
        ret = 0
    return ret


def g3(d: float, w: float, delta: float) -> float:
    """function to consider the maximum contact"""
    try:
        ret = (d / 2 - w) ** 2
        ret = ret / (d**3)
        if ret < 0:
            ret = 0
    except:
        ret = 0
    return ret


def g4(d: float, w: float, delta: float) -> float:
    """function to consider the maximum contact"""
    try:
        ret = d * d * pi / 8 - w * sqrt(d * d / 4 - w * w)
        ret -= 0.25 * d * d * asin(2 * w / d)
        ret = ret / (d**3)
        if ret < 0:
            ret = 0
    except:
        ret = 0
    return ret


def validRange(s, e) -> bool:
    return s <= e


def findRange(x1, x2, xa, xb):
    """
    return {valid status and a range} as a result of intersection between [x1,x2] and [xa,xb]
    """
    if validRange(x1, x2) and validRange(xa, xb):
        # assume sd < ed and d1 < d2
        ds = max(x1, xa)
        de = min(x2, xb)
        return validRange(ds, de), ds, de
    else:
        return False, 0, 0


@dataclass
class Conc_AI:
    pk: float = 0.75
    ag: float = 20  # maximum size of all the aggregates
    af: float = 4.75  # the maximum size of fine aggregates
    fc: float = 40
    muy: float = 0.4
    # the probability of aggregate vicinity fracture - for coarse aggregates
    pv: float = 1
    # the probability of aggregate vicinity fracture - for fine aggregates
    pvf: float = 1
    # type of function to calculate sig_pu: 0 or 1 or 2
    sig_puCalType: int = field(repr=False, default=1)
    FACTOR_fc2fcc: float = 1.2  # according to EC2
    FACTOR_shape: float = 1  # 1.23
    # 2024.06.18 - factor for friction caused by macro roughness
    Cf: float = 0.35

    def data2dict(self) -> dict:
        return asdict(self)

    def dict2data(self, d: dict):
        self.__init__(**d)

    def repr_info(
        self,
        b_pk: bool = True,
        b_ag: bool = True,
        b_muy: bool = True,
        b_pv: bool = True,
        b_fc: bool = True,
        b_sigpuCalType=True,
        b_factor_fc2fcc=True,
        b_shapeFactor=True,
    ) -> str:
        s = ""
        if b_pk:
            s += f"pk: {self.pk:.2f}, "
        if b_ag:
            s += f"ag: {self.ag:.2f}, "
        if b_muy:
            s += f"muy: {self.muy:.2f}, "
        if b_pv:
            s += f"pv: {self.pv:.2f}, "
        if b_fc:
            s += f"fc: {self.fc:.2f}, fcc: {self.fc*self.FACTOR_fc2fcc:.2f}, sigpu: {self.fc2sig_pu():.2f}, "
        s += "\n"
        if b_factor_fc2fcc:
            s += f"fc2fccFACTOR: {self.FACTOR_fc2fcc:.2f}, "
        if b_sigpuCalType:
            s += f"sigpuCalType: {self.sig_puCalType:.0f}, "
        if b_shapeFactor:
            s += f"shapeFACTOR: {self.FACTOR_shape:.2f}"

        return s

    def __fc2sig_pu0(self):
        """
        calculate sig_pu from fc, based on Walraven - 1981
        """
        _fcc = self.fc * self.FACTOR_fc2fcc
        return 5.83 * (_fcc**0.63)

    def __fc2sig_pu1(self):
        """
        calculate sig_pu from fc, based on Yang, Walraven, Uiji - 2016, ASCE
        """
        _fcc = self.fc * self.FACTOR_fc2fcc
        return 6.39 * (_fcc**0.56)

    def __fc2sig_pu2(self):
        """
        calculate sig_pu from fc, based on suggested modification of Walraven, Reinhardt 1990 - Heron
        """
        _fcc = self.fc * self.FACTOR_fc2fcc
        return 4.76 * (_fcc**0.64)

    def fc2sig_pu(self):
        """
        calculate sig_pu from fc, based on (1): Yang, Walraven, Uiji - 2016, ASCE, or (0): Walraven - 1981
        """
        if self.sig_puCalType == 0:
            f = self.__fc2sig_pu0()
        elif self.sig_puCalType == 1:
            f = self.__fc2sig_pu1()
        else:
            f = self.__fc2sig_pu2()
        return f

    def orgL_A(self, aa: float):
        """
        calculate unit expected length-area caused by aggregates in [0,aa] without considering (pv,pvf)
        """
        sd, ed = 0, aa
        fD = lambda d: self.pk * f(d, aa) * sqrt(aa / self.ag) / d
        ret = integrate.quad(fD, sd, ed)[0]
        return ret

    def orgL_A_D(self, aa: float, d1: float, d2: float):
        """
        calculate unit expected length-area of intersected circles with diameters in [d1,d2]
        caused by aggregates in [0,aa] without considering (pv,pvf)
        """
        l_ret = 0
        sdA = 0
        edA = aa
        valid, sd, ed = findRange(sdA, edA, d1, d2)
        if valid:
            fD = lambda d: self.pk * f(d, aa) * sqrt(aa / self.ag) / d
            l_ret = integrate.quad(fD, sd, ed)[0]
        return l_ret

    def orgAxy_0_aa(self, w: float, delta: float, aa: float):
        """
        calculate original Ax, Ay contributed by aggregate sizes [0,aa]. It means that pv is not considered
        """
        pk = self.pk
        ag = self.ag
        d1 = 0
        d2 = aa
        if delta < w:  # case A
            if delta == 0.00:
                delta = 0.00001
            # consider the range
            sdA = (w * w + delta * delta) / delta
            edA = ag
            valid, sd, ed = findRange(sdA, edA, d1, d2)
            # calculate
            if valid:
                fAy = lambda d: f(d, aa) * g1(d, w, delta)
                aAy = integrate.quad(fAy, sd, ed)[0]
                aAy = aAy * (4 * pk / pi) * sqrt(aa / ag)

                fAx = lambda d: f(d, aa) * g2(d, w, delta)
                aAx = integrate.quad(fAx, sd, ed)[0]
                aAx = aAx * (4 * pk / pi) * sqrt(aa / ag)
            else:
                aAx = 0
                aAy = 0

        else:  # case B (delta > w)
            sdB1 = 2 * w
            edB1 = (w * w + delta * delta) / w
            # ed1 = (w * w + delta * delta) / delta
            # in Walraven 1979 - it might be WRONG: # ed1 = (w * w + delta * delta) / delta
            sdB2 = edB1
            edB2 = ag

            # consider the range
            valid1, sd1, ed1 = findRange(sdB1, edB1, d1, d2)
            valid2, sd2, ed2 = findRange(sdB2, edB2, d1, d2)

            aAy = 0
            aAx = 0
            if valid1:
                fAy1 = lambda d: f(d, aa) * g3(d, w, delta)
                aAy += integrate.quad(fAy1, sd1, ed1)[0]
                fAx1 = lambda d: f(d, aa) * g4(d, w, delta)
                aAx += integrate.quad(fAx1, sd1, ed1)[0]
            if valid2:
                fAy2 = lambda d: f(d, aa) * g1(d, w, delta)
                aAy += integrate.quad(fAy2, sd2, ed2)[0]
                fAx2 = lambda d: f(d, aa) * g2(d, w, delta)
                aAx += integrate.quad(fAx2, sd2, ed2)[0]

            aAy = aAy * (4 * pk / pi) * sqrt(aa / ag)
            aAx = aAx * (4 * pk / pi) * sqrt(aa / ag)

        return aAx * self.FACTOR_shape, aAy * self.FACTOR_shape

    def calAxy(self, w: float, delta: float):
        """
        calculate Ax,Ay of coarse and fine aggregates
        - oAx_all, oAy_all: for all aggregates without considering pv (pv=1)
        - Ax_c, Ay_c: for coarse aggregates, with pv
        - Ax_f, Ay_f: for fine aggregates, with pvf

        return nAx_c, nAy_c, oAx_f, oAy_f
        """
        # Ax, Ay caused by all aggregates without considering pv (pv=1) - same as Walraven
        oAx_all, oAy_all = self.orgAxy_0_aa(w=w, delta=delta, aa=self.ag)
        # Ax, Ay caused by fine aggregates without considering pv (pv=1) - aggregates in [0,af]
        aa_f = min(self.af, self.ag)
        oAx_f, oAy_f = self.orgAxy_0_aa(w=w, delta=delta, aa=aa_f)
        # Ax, Ay caused by coarse aggregates without considering pv (pv=1)
        oAx_c, oAy_c = oAx_all - oAx_f, oAy_all - oAy_f

        # Ax, Ay caused by fine aggregates with actual pvf
        nAx_f, nAy_f = self.pvf * oAx_f, self.pvf * oAy_f
        # Ax, Ay caused by coarse aggregates with actual pv
        nAx_c, nAy_c = self.pv * oAx_c, self.pv * oAy_c

        return nAx_c, nAy_c, nAx_f, nAy_f

    def calStresses_ai(self, w: float, delta: float):
        """
        calculate shear and normal stresses produced aggregate interlock of coarse and fine aggregates

        return ns, ts, ns_c, ts_c, ns_f, ts_f
        """
        sig_pu = self.fc2sig_pu()
        muy = self.muy
        # contact areas
        aAx_c, aAy_c, aAx_f, aAy_f = self.calAxy(w=w, delta=delta)
        # streses
        ns_ai_c = sig_pu * (aAx_c - muy * aAy_c)
        ts_ai_c = sig_pu * (aAy_c + muy * aAx_c)
        ns_ai_f = sig_pu * (aAx_f - muy * aAy_f)
        ts_ai_f = sig_pu * (aAy_f + muy * aAx_f)
        ns_ai = ns_ai_c + ns_ai_f
        ts_ai = ts_ai_c + ts_ai_f

        return ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f

    def calStresses_all(self, w: float, delta: float):
        """
        calculate stresses of all aspects including
        aggregate interlock and friction of macro roughness

        return: ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, ns, ts, ns_fr, ts_fr
        """
        sig_pu = self.fc2sig_pu()
        muy = self.muy
        # contact areas
        aAx_c, aAy_c, aAx_f, aAy_f = self.calAxy(w=w, delta=delta)

        # streses caused by aggregate interlocking
        ns_ai_c = sig_pu * (aAx_c - muy * aAy_c)
        ts_ai_c = sig_pu * (aAy_c + muy * aAx_c)
        ns_ai_f = sig_pu * (aAx_f - muy * aAy_f)
        ts_ai_f = sig_pu * (aAy_f + muy * aAx_f)
        ns_ai = ns_ai_c + ns_ai_f
        ts_ai = ts_ai_c + ts_ai_f

        # stresses caused by friction of macro roughness
        #   length of macro roughness friction: 1 - length of aggregate interlocking
        l_ai_f0 = self.orgL_A(aa=self.af)
        l_ai_c0 = self.pk - l_ai_f0
        l_fr_ma = 1 - (l_ai_f0 * self.pvf + l_ai_c0 * self.pv)
        #   stresses according to original Walraven, assuming that no aggregate-cutting fracture
        aAx_c0, aAy_c0, aAx_f0, aAy_f0 = aAx_c, aAy_c, aAx_f, aAy_f
        if self.pv > 0:
            aAx_c0, aAy_c0 = aAx_c0 / self.pv, aAy_c0 / self.pv
        if self.pvf > 0:
            aAx_f0, aAy_f0 = aAx_f0 / self.pvf, aAy_f0 / self.pvf
        aAx0, aAy0 = aAx_c0 + aAx_f0, aAy_c0 + aAy_f0
        ns0 = sig_pu * (aAx0 - muy * aAy0)
        ts0 = sig_pu * (aAy0 + muy * aAx0)

        ns_fr, ts_fr = ns0 * self.Cf * l_fr_ma, ts0 * self.Cf * l_fr_ma

        # combined stresses
        ns, ts = ns_ai + ns_fr, ts_ai + ts_fr

        # return values
        return ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, ns, ts, ns_fr, ts_fr

    def calMaxStresses_ai(self, w: float):
        """
        calculate the maximum stresses - along with the maximum contact of aggregate interlock
        """
        ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f = 0, 0, 0, 0, 0, 0
        delta = 10000  # for the case of error
        # calculate the delta value in line with the maximum shear stress
        # * note that when the biggest aggregate get maximum contact status, other aggregate also get it.
        # * this is because of the rigid-plastic stress-train relation assumption for the cement paste
        t = w * self.ag - w * w
        if t >= 0:
            delta = sqrt(t)
            ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f = self.calStresses_ai(
                w=w, delta=delta
            )

        return ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, delta

    def calMaxStresses_all(self, w: float):
        """
        calculate the maximum stresses - along with the maximum contact of aggregate interlock
        """
        ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, ns, ts, ns_fr, ts_fr = (
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        delta = 10000  # for the case of error
        # calculate the delta value in line with the maximum shear stress
        # * note that when the biggest aggregate get maximum contact status, other aggregate also get it.
        # * this is because of the rigid-plastic stress-train relation assumption for the cement paste
        t = w * self.ag - w * w
        if t >= 0:
            delta = sqrt(t)
            ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, ns, ts, ns_fr, ts_fr = (
                self.calStresses_all(w=w, delta=delta)
            )

        return (
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
        )


class AI_Calculate:
    @staticmethod
    def calStress_w_delta(
        conc: Conc_AI, ws: np.array, deltas: np.array
    ) -> pd.DataFrame:
        """
        return the basic results: normal stress and shear stress
        """
        df_w = pd.DataFrame({"w": ws})
        df_delta = pd.DataFrame({"delta": deltas})
        df = pd.merge(df_w, df_delta, how="cross")
        a_w = df["w"].to_numpy().flatten()
        a_delta = df["delta"].to_numpy().flatten()

        def func(t_conc: Conc_AI, w, delta):
            ns_ai, ts_ai, ns_ai_c, ts_ai_c, ns_ai_f, ts_ai_f, ns, ts, ns_fr, ts_fr = (
                t_conc.calStresses_all(w=w, delta=delta)
            )
            return (
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
            )

        f_cal = np.vectorize(func)
        (
            a_ns_ai,
            a_ts_ai,
            a_ns_ai_c,
            a_ts_ai_c,
            a_ns_ai_f,
            a_ts_ai_f,
            a_ns,
            a_ts,
            a_ns_fr,
            a_ts_fr,
        ) = f_cal(conc, a_w, a_delta)

        df_ret = pd.DataFrame(
            {
                "w": a_w,
                "delta": a_delta,
                "ns_ai": a_ns_ai,
                "ts_ai": a_ts_ai,
                "ns_ai_c": a_ns_ai_c,
                "ts_ai_c": a_ts_ai_c,
                "ns_ai_f": a_ns_ai_f,
                "ts_ai_f": a_ts_ai_f,
                "ns": a_ns,
                "ts": a_ts,
                "ns_fr": a_ns_fr,
                "ts_fr": a_ts_fr,
            }
        )

        return df_ret
