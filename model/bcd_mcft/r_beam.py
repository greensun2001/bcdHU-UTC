from dataclasses import dataclass


@dataclass
class FactorSetting:
    phi: float = 1
    lbd: float = 1


@dataclass
class Geometry:
    a: float
    b: float
    d: float

    def a_d(self):
        return self.a / self.d

    def area(self):
        return self.b * self.d


@dataclass
class Material:
    fc: float
    e_s: float
    steel_ratio: float
    ag: float = 20
    e_c: float = 50000  # Ec is necessary in CSCT Model


@dataclass
class Beam:
    geo: Geometry
    mat: Material
    factors: FactorSetting
