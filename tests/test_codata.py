"""Tests for the CODATA table and its accessors.

`ppconstants._codata` is the one interpreted-only module in the package
(spec §9.1 CPython-boundary code), so these tests exercise Python
behaviour rather than compiled kernels. Reference values are the CODATA
2022 figures; scipy parity is checked separately in test_scipy_compat.py.
"""

import warnings

import pytest

import ppconstants as ppc
from ppconstants import _codata


class TestTableShape:
    def test_entry_is_value_unit_uncertainty(self):
        entry = ppc.physical_constants["speed of light in vacuum"]
        assert entry == (299792458.0, "m s^-1", 0.0)

    def test_table_is_populated(self):
        assert len(ppc.physical_constants) > 400
        assert len(_codata._CURRENT_KEYS) > 300

    def test_current_and_obsolete_partition_the_table(self):
        keys = set(ppc.physical_constants)
        assert _codata._CURRENT_KEYS <= keys
        assert _codata._OBSOLETE_KEYS <= keys
        assert not (_codata._CURRENT_KEYS & _codata._OBSOLETE_KEYS)
        assert _codata._CURRENT_KEYS | _codata._OBSOLETE_KEYS == keys

    def test_every_entry_is_well_formed(self):
        for key, entry in ppc.physical_constants.items():
            assert len(entry) == 3, key
            val, unit_str, unc = entry
            assert isinstance(val, float), key
            assert isinstance(unit_str, str), key
            assert isinstance(unc, float), key
            assert unc >= 0.0, key


class TestAccessors:
    def test_value(self):
        assert ppc.value("elementary charge") == 1.602176634e-19

    def test_unit(self):
        assert ppc.unit("elementary charge") == "C"

    def test_precision_is_relative_uncertainty(self):
        key = "proton mass"
        val, _, unc = ppc.physical_constants[key]
        assert ppc.precision(key) == unc / val

    def test_precision_of_exact_constant_is_zero(self):
        assert ppc.precision("speed of light in vacuum") == 0.0

    def test_missing_key_raises_keyerror(self):
        with pytest.raises(KeyError):
            ppc.value("no such constant")


class TestFind:
    def test_substring_search_is_case_insensitive(self):
        assert ppc.find("boltzmann") == ppc.find("BOLTZMANN")

    def test_results_are_sorted(self):
        result = ppc.find("mass")
        assert result == sorted(result)

    def test_known_hits(self):
        hits = ppc.find("boltzmann")
        assert "Boltzmann constant" in hits
        assert "Stefan-Boltzmann constant" in hits

    def test_no_argument_returns_all_current_keys(self):
        assert set(ppc.find()) == set(_codata._CURRENT_KEYS)

    def test_find_only_searches_current_keys(self):
        for key in ppc.find():
            assert key in _codata._CURRENT_KEYS

    def test_disp_prints_and_returns_none(self, capsys):
        assert ppc.find("boltzmann", disp=True) is None
        printed = capsys.readouterr().out.splitlines()
        assert printed == ppc.find("boltzmann")

    def test_no_match_returns_empty_list(self):
        assert ppc.find("definitely not a constant name") == []


class TestConstantWarning:
    def test_is_a_deprecation_warning(self):
        assert issubclass(ppc.ConstantWarning, DeprecationWarning)

    def test_obsolete_key_warns(self):
        with pytest.warns(ppc.ConstantWarning, match="not in current"):
            ppc.value("Wien displacement law constant")

    def test_current_key_does_not_warn(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", ppc.ConstantWarning)
            ppc.value("elementary charge")
            ppc.unit("elementary charge")
            ppc.precision("elementary charge")

    def test_alias_keys_do_not_warn(self):
        # Every alias, not one arbitrary key: set iteration order varies per
        # run, and some aliases are also current keys where this is vacuous.
        assert _codata._ALIAS_KEYS, "alias set should not be empty"
        for alias in sorted(_codata._ALIAS_KEYS):
            with warnings.catch_warnings():
                warnings.simplefilter("error", ppc.ConstantWarning)
                ppc.value(alias)

    def test_some_aliases_are_genuinely_obsolete_keys(self):
        # Guards the test above from becoming vacuous: the alias mechanism
        # only matters for keys that would otherwise warn.
        assert _codata._ALIAS_KEYS & _codata._OBSOLETE_KEYS

    def test_all_three_accessors_warn(self):
        key = "Wien displacement law constant"
        for accessor in (ppc.value, ppc.unit, ppc.precision):
            with pytest.warns(ppc.ConstantWarning):
                accessor(key)


class TestConsistencyWithCompiledConstants:
    """The POST constants and the CODATA table must not drift apart."""

    def test_exact_si_constants_agree(self):
        pairs = [
            (ppc.c, "speed of light in vacuum"),
            (ppc.h, "Planck constant"),
            (ppc.e, "elementary charge"),
            (ppc.k, "Boltzmann constant"),
            (ppc.N_A, "Avogadro constant"),
        ]
        for constant, key in pairs:
            assert constant == ppc.value(key), key

    def test_measured_constants_agree(self):
        pairs = [
            (ppc.G, "Newtonian constant of gravitation"),
            (ppc.alpha, "fine-structure constant"),
            (ppc.Rydberg, "Rydberg constant"),
            (ppc.m_e, "electron mass"),
            (ppc.m_p, "proton mass"),
            (ppc.m_n, "neutron mass"),
            (ppc.m_u, "atomic mass constant"),
            (ppc.mu_0, "vacuum mag. permeability"),
            (ppc.epsilon_0, "vacuum electric permittivity"),
        ]
        for constant, key in pairs:
            assert constant == ppc.value(key), key

    def test_derived_constants_agree(self):
        assert ppc.hbar == ppc.value("reduced Planck constant")
        assert ppc.R == ppc.value("molar gas constant")
        assert ppc.sigma == ppc.value("Stefan-Boltzmann constant")

    def test_standard_gravity_agrees(self):
        assert ppc.g == ppc.value("standard acceleration of gravity")


def test_scipy_stale_value_anomaly_is_reproduced():
    """Pin the two keys where scipy publishes a stale CODATA 2018 value.

    See the module docstring of ppconstants._codata. If scipy fixes this,
    this test fails and the table should be re-synced.
    """
    assert ppc.physical_constants["natural unit of momentum"] == (
        2.730924488e-22, "kg m s^-1", 3.4e-30,
    )
    assert ppc.physical_constants["natural unit of momentum in MeV/c"] == (
        0.5109989461, "MeV/c", 3.1e-09,
    )
