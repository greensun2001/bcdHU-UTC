from dataclasses import dataclass
import math
from model.bcd_mcft.r_beam import *
import model.bcd_mcft.r_coreF_bcdMCFT as cF


@dataclass
class BCD_RunSetting:
    # for m0 model: pv is set to 1, for m1 model: keep the original pv but C=0
    eps_tolerance: float = 1e-3
    init_ex: float = 1e-3
    relative_step_ex: float = 1e-2
    pv: float = 1
    # for f = (ag+A)*pv + B
    f_A: float = 8
    f_B: float = 8
    # for g = 1 + C*(1-pv)
    g_C: float = 0.5


@dataclass
class NBCD_RunSetting(BCD_RunSetting):
    # for the new idea of
    # for X = 1 - H.w, wherein H = E/ag. The E value is 2 by default
    h_E: float = 2


@dataclass
class Mdl_bcdMCFT(Beam):
    r_setting: BCD_RunSetting

    def _calF(self):
        f = (self.mat.ag + self.r_setting.f_A) * self.r_setting.pv + self.r_setting.f_B
        return f

    def _calG(self):
        g = 1 + self.r_setting.g_C * (1 - self.r_setting.pv)
        return g

    def _cal_a_s(self):
        return self.geo.area() * self.mat.steel_ratio

    def _cal_sze(self) -> float:
        """
        function to calculate the equivalent crack spacing sze
        """
        # the effective shear depth, taken as the greater of 0.9d or 0.72hf
        dv = 0.9 * self.geo.d
        s_z = dv  # the crack spacing parameter, shall be taken as dv
        f = self._calF()
        value = 35 * s_z / f
        return value

    def _ex2vc(self, ex: float):
        """
        Function to calculate the shear force (vc) from
        the longitudinal strain (ex)
        """
        # calculating beta factor, effective shear depth, and shear force
        #   g
        g = self._calG()
        #   sze
        sze = self._cal_sze()
        #   beta
        e1, theta, beta = cF.ex2all(g=g, sxe=sze, ex=ex)
        dv = 0.9 * self.geo.d
        vc = beta * math.sqrt(self.mat.fc) * self.geo.b * dv
        return vc, beta, e1, theta

    def _vc2ex(self, vc: float) -> float:
        """
        function to calculate the longitudinal strain (ex) from
        a specific shear force (vc)
        Examples:
        Args:
            vc (float): the value of shear force Vc
        Returns:
            float: the value of calculated longitudinal strain
        """
        # the longitudinal steel ratio
        a_s = self._cal_a_s()
        a = self.geo.a
        d = self.geo.d
        e_s = self.mat.e_s
        value = vc * (1 + 1.1 * a / d) / (2 * e_s * a_s)
        return value

    def _smallOldex(self, o_ex: float, n_ex: float):
        """return -1 if True, 1 if False"""
        if o_ex < n_ex:
            return 1
        else:
            return -1

    def loop_ex(self):
        """ """
        lowest_step = math.ulp(0.001)
        r_setting = self.r_setting
        step = r_setting.relative_step_ex * r_setting.init_ex
        o_ex = r_setting.init_ex
        # calculate the shear force (vc)
        vc, beta, e1, theta = self._ex2vc(o_ex)
        # calculate the new value of longitudinal strain (n_ex)
        n_ex = self._vc2ex(vc)
        old_compa = self._smallOldex(o_ex, n_ex)
        diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
        print(
            f"o_ex: {o_ex:.7f}, n_ex: {n_ex:.7f}, diff: {diff:.7f}, shear stress: {vc/self.geo.area():.7f}, step: {step}"
        )
        while True:
            if step > lowest_step:
                o_ex += old_compa * step
            else:
                break
            # calculate the shear force (vc)
            vc, beta, e1, theta = self._ex2vc(o_ex)
            # calculate the new value of longitudinal strain (n_ex)
            n_ex = self._vc2ex(vc)
            # check the change of ex
            new_compa = self._smallOldex(o_ex, n_ex)
            if new_compa * old_compa < 0:
                step = step / 2
                diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
                print(
                    f"o_ex: {o_ex:.7f}, n_ex: {n_ex:.7f}, diff: {diff:.7f}, shear stress: {vc/self.geo.area():.7f}, step: {step}"
                )
                # check the condition of tolerance
                if diff < r_setting.eps_tolerance:
                    break
            old_compa = new_compa

    def getShearStrength_F(self):
        """ """
        lowest_step = math.ulp(0.001)
        r_setting = self.r_setting
        step = r_setting.relative_step_ex * r_setting.init_ex
        o_ex = r_setting.init_ex
        # calculate the shear force (vc)
        vc, beta, e1, theta = self._ex2vc(o_ex)
        # calculate the new value of longitudinal strain (n_ex)
        n_ex = self._vc2ex(vc)
        old_compa = self._smallOldex(o_ex, n_ex)
        while True:
            if step > lowest_step:
                o_ex += old_compa * step
            else:
                break
            # calculate the shear force (vc)
            vc, beta, e1, theta = self._ex2vc(o_ex)
            # calculate the new value of longitudinal strain (n_ex)
            n_ex = self._vc2ex(vc)
            # check the change of ex
            new_compa = self._smallOldex(o_ex, n_ex)
            if new_compa * old_compa < 0:
                step = step / 2
                diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
                # check the condition of tolerance
                if diff < r_setting.eps_tolerance:
                    break
            old_compa = new_compa

        return vc, beta, e1, theta, o_ex

    def getShearStrength_S(self):
        """ """
        vc, beta, e1, theta, ex = self.getShearStrength_F()
        return vc / self.geo.area(), beta, e1, theta, ex

    def t_results(self):
        self.loop_ex()


@dataclass
class NMdl_bcdMCFT(Beam):
    r_setting: NBCD_RunSetting

    def _calF(self):
        f = (self.mat.ag + self.r_setting.f_A) * self.r_setting.pv + self.r_setting.f_B
        return f

    def _calG(self):
        g = 1 + self.r_setting.g_C * (1 - self.r_setting.pv)
        return g

    def _calH(self):
        return self.r_setting.h_E / self.mat.ag

    def _cal_a_s(self):
        return self.geo.area() * self.mat.steel_ratio

    # importantly different than Mdl_bcdMCFT
    def _ex2vc(self, ex: float):
        """
        Function to calculate the shear force (vc) from
        the longitudinal strain (ex)
        """
        # calculating beta factor, effective shear depth, and shear force
        #   f,g,h
        f = self._calF()
        g = self._calG()
        h = self._calH()
        #   sx
        sx = dv = 0.9 * self.geo.d
        #   beta
        e1, theta, beta = cF.n_ex2all(f, g, h, sx, ex)
        vc = beta * math.sqrt(self.mat.fc) * self.geo.b * dv
        return vc, beta, e1, theta

    def _vc2ex(self, vc: float) -> float:
        """
        function to calculate the longitudinal strain (ex) from
        a specific shear force (vc)
        Examples:
        Args:
            vc (float): the value of shear force Vc
        Returns:
            float: the value of calculated longitudinal strain
        """
        # the longitudinal steel ratio
        a_s = self._cal_a_s()
        a = self.geo.a
        d = self.geo.d
        e_s = self.mat.e_s
        value = vc * (1 + 1.1 * a / d) / (2 * e_s * a_s)
        return value

    def _smallOldex(self, o_ex: float, n_ex: float):
        """return -1 if True, 1 if False"""
        if o_ex < n_ex:
            return 1
        else:
            return -1


    def loop_ex(self):
        """ """
        r_setting = self.r_setting
        step = r_setting.relative_step_ex * r_setting.init_ex
        o_ex = r_setting.init_ex
        # calculate the shear force (vc)
        vc, beta, e1, theta = self._ex2vc(o_ex)
        # calculate the new value of longitudinal strain (n_ex)
        n_ex = self._vc2ex(vc)
        diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
        print(
            f"RETURN >> o_ex: {o_ex:.7f}, n_ex: {n_ex:.7f}, diff: {diff:.7f}, shear stress: {vc/self.geo.area():.7f}, step: {step}"
        )
        print()
        while True:
            o_ex = (o_ex + n_ex) * 0.5
            # calculate the shear force (vc)
            vc, beta, e1, theta = self._ex2vc(o_ex)
            # calculate the new value of longitudinal strain (n_ex)
            n_ex = self._vc2ex(vc)

            diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
            print(
                f"RETURN >> o_ex: {o_ex:.7f}, n_ex: {n_ex:.7f}, diff_ex: {diff:.7f}, shear stress: {vc/self.geo.area():.7f}, step: {step}"
            )
            print()

            if diff < r_setting.eps_tolerance:
                break

    def getShearStrength_F(self):
        """ """
        r_setting = self.r_setting
        step = r_setting.relative_step_ex * r_setting.init_ex
        o_ex = r_setting.init_ex
        # calculate the shear force (vc)
        vc, beta, e1, theta = self._ex2vc(o_ex)
        # calculate the new value of longitudinal strain (n_ex)
        n_ex = self._vc2ex(vc)
        diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
        while True:
            o_ex = (o_ex + n_ex) * 0.5
            # calculate the shear force (vc)
            vc, beta, e1, theta = self._ex2vc(o_ex)
            # calculate the new value of longitudinal strain (n_ex)
            n_ex = self._vc2ex(vc)

            diff = math.fabs(n_ex - o_ex) / min(o_ex, n_ex)
            if diff < r_setting.eps_tolerance:
                break

        return vc, beta, e1, theta, o_ex


    def getShearStrength_S(self):
        """ """
        vc, beta, e1, theta, ex = self.getShearStrength_F()
        return vc / self.geo.area(), beta, e1, theta, ex

    def t_results(self):
        self.loop_ex()
