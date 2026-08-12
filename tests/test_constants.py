"""Interpreted-mode tests for the scalar constant tables.

Exact SI constants are checked against their defining literals (BIPM 9th
SI brochure); derived constants against independent computations; measured
constants against hardcoded CODATA 2022 values. No scipy required (see
test_scipy_compat.py for the optional comparison sweep).
"""

import math

import ppconstants as ppc


class TestMathematical:
    def test_pi(self):
        assert ppc.pi == math.pi

    def test_golden(self):
        assert ppc.golden == (1.0 + 5.0 ** 0.5) / 2.0
        assert abs(ppc.golden - (1.0 + math.sqrt(5.0)) / 2.0) < 1e-15
        # Defining property: x^2 = x + 1.
        assert abs(ppc.golden ** 2 - (ppc.golden + 1.0)) < 1e-15

    def test_alias(self):
        assert ppc.golden_ratio == ppc.golden


class TestExactSI:
    """SI defining constants (2019 redefinition); equality must be bit-exact."""

    def test_defining_constants(self):
        assert ppc.c == 299792458.0
        assert ppc.h == 6.62607015e-34
        assert ppc.e == 1.602176634e-19
        assert ppc.k == 1.380649e-23
        assert ppc.N_A == 6.02214076e23

    def test_conventional_constants(self):
        # Exact by adoption, not an SI defining constant (CGPM 1901).
        assert ppc.g == 9.80665

    def test_aliases(self):
        assert ppc.speed_of_light == ppc.c
        assert ppc.Planck == ppc.h
        assert ppc.elementary_charge == ppc.e
        assert ppc.Boltzmann == ppc.k
        assert ppc.Avogadro == ppc.N_A


class TestDerivedExact:
    def test_hbar(self):
        assert ppc.hbar == ppc.h / (2.0 * math.pi)

    def test_gas_constant(self):
        assert ppc.R == ppc.N_A * ppc.k
        assert ppc.gas_constant == ppc.R

    def test_stefan_boltzmann(self):
        # sigma = 2 pi^5 k^4 / (15 h^3 c^2)
        formula = (
            2.0 * math.pi ** 5 * ppc.k ** 4 / (15.0 * ppc.h ** 3 * ppc.c ** 2)
        )
        assert abs(ppc.sigma - formula) / formula < 1e-14
        assert ppc.Stefan_Boltzmann == ppc.sigma

    def test_wien(self):
        # b = (h c / k) / x with x = 4.965114231744276 (Lambert-W root).
        formula = (ppc.h * ppc.c / ppc.k) / 4.965114231744276
        assert abs(ppc.Wien - formula) / formula < 1e-14


class TestCODATA2022:
    def test_measured_values(self):
        assert ppc.mu_0 == 1.25663706127e-06
        assert ppc.epsilon_0 == 8.8541878188e-12
        assert ppc.G == 6.6743e-11
        assert ppc.alpha == 0.0072973525643
        assert ppc.Rydberg == 10973731.568157
        assert ppc.m_e == 9.1093837139e-31
        assert ppc.m_p == 1.67262192595e-27
        assert ppc.m_n == 1.67492750056e-27
        assert ppc.m_u == 1.66053906892e-27

    def test_aliases(self):
        assert ppc.gravitational_constant == ppc.G
        assert ppc.fine_structure == ppc.alpha
        assert ppc.electron_mass == ppc.m_e
        assert ppc.proton_mass == ppc.m_p
        assert ppc.neutron_mass == ppc.m_n
        assert ppc.u == ppc.m_u
        assert ppc.atomic_mass == ppc.m_u

    def test_consistency_relations(self):
        # alpha = e^2 / (4 pi epsilon_0 hbar c), good to measured precision.
        alpha = ppc.e ** 2 / (4.0 * math.pi * ppc.epsilon_0 * ppc.hbar * ppc.c)
        assert abs(alpha - ppc.alpha) / ppc.alpha < 1e-9
        # mu_0 epsilon_0 c^2 = 1, good to measured precision.
        assert abs(ppc.mu_0 * ppc.epsilon_0 * ppc.c ** 2 - 1.0) < 1e-9

    def test_types(self):
        for name in ("mu_0", "G", "Rydberg", "m_e"):
            assert isinstance(getattr(ppc, name), float)
