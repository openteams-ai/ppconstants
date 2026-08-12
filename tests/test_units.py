"""Interpreted-mode tests for the unit conversion catalog.

Values are checked against their defining relations (international
yard-and-pound agreement, NIST SP 811) rather than restating the decimals
that _units already computes. The exact-equality sweep against
scipy.constants lives in test_scipy_compat.py.
"""

import math

import ppconstants as ppc


class TestMass:
    def test_avoirdupois_chain(self):
        assert ppc.grain == 64.79891e-6
        assert ppc.lb == 7000.0 * ppc.grain
        assert ppc.pound == ppc.lb
        assert ppc.oz == ppc.pound / 16.0
        assert ppc.stone == 14.0 * ppc.pound
        assert ppc.long_ton == 2240.0 * ppc.pound
        assert ppc.short_ton == 2000.0 * ppc.pound

    def test_pound_is_defined_value(self):
        # 1959 agreement: 1 lb == 0.45359237 kg, to float64 rounding.
        assert abs(ppc.pound - 0.45359237) < 1e-16

    def test_troy_chain(self):
        assert ppc.troy_ounce == 480.0 * ppc.grain
        assert ppc.troy_pound == 12.0 * ppc.troy_ounce

    def test_slug_family(self):
        assert ppc.slinch == ppc.blob
        assert ppc.slug == ppc.blob / 12.0

    def test_slug_family_values(self):
        # Independent pins: a blob is one lbf*s^2 per inch, a slug per foot.
        assert abs(ppc.blob - ppc.lbf / ppc.inch) < 1e-12
        assert abs(ppc.slug - ppc.lbf / ppc.foot) < 1e-12
        # Published decimals, so a wrong derivation cannot pass silently.
        assert abs(ppc.blob - 175.12683524647636) < 1e-10
        assert abs(ppc.slug - 14.593902937206364) < 1e-12

    def test_metric(self):
        assert ppc.gram == 1e-3
        assert ppc.metric_ton == 1e3
        assert ppc.carat == 200e-6


class TestAngle:
    def test_degree(self):
        assert ppc.degree == math.pi / 180.0
        assert abs(360.0 * ppc.degree - 2.0 * math.pi) < 1e-15

    def test_subdivisions(self):
        assert ppc.arcmin == ppc.degree / 60.0
        assert ppc.arcsec == ppc.arcmin / 60.0
        assert ppc.arcminute == ppc.arcmin
        assert ppc.arcsecond == ppc.arcsec


class TestTime:
    def test_ladder(self):
        assert ppc.minute == 60.0
        assert ppc.hour == 3600.0
        assert ppc.day == 86400.0
        assert ppc.week == 7.0 * ppc.day
        assert ppc.year == 365.0 * ppc.day
        assert ppc.Julian_year == 365.25 * ppc.day


class TestLength:
    def test_imperial_chain(self):
        assert ppc.inch == 0.0254
        assert ppc.foot == 12.0 * ppc.inch
        assert ppc.yard == 3.0 * ppc.foot
        assert ppc.mile == 1760.0 * ppc.yard
        assert ppc.mil == ppc.inch / 1000.0
        assert ppc.pt == ppc.inch / 72.0
        assert ppc.point == ppc.pt

    def test_survey_units_differ_from_international(self):
        # The survey foot is 1200/3937 m, very slightly longer.
        assert ppc.survey_foot > ppc.foot
        assert ppc.survey_mile == 5280.0 * ppc.survey_foot

    def test_survey_foot_value(self):
        # NIST SP 811: exactly 1200/3937 m, i.e. 2 ppm longer than 0.3048.
        assert abs(ppc.survey_foot - 0.3048006096012192) < 1e-16
        assert abs(ppc.survey_foot / ppc.foot - 1.0 - 2e-6) < 1e-9
        assert abs(ppc.survey_mile - 1609.3472186944373) < 1e-9

    def test_metric_and_astronomical(self):
        assert ppc.fermi == 1e-15
        assert ppc.angstrom == 1e-10
        assert ppc.micron == 1e-6
        assert ppc.nautical_mile == 1852.0
        assert ppc.au == 149597870700.0
        assert ppc.astronomical_unit == ppc.au

    def test_light_year_is_julian_year_of_light(self):
        assert ppc.light_year == ppc.Julian_year * ppc.c

    def test_parsec_definition(self):
        # One au subtending one arcsecond.
        assert ppc.parsec == ppc.au / ppc.arcsec
        assert abs(ppc.parsec / ppc.light_year - 3.26156) < 1e-4


class TestPressure:
    def test_atm_and_derived(self):
        assert ppc.atm == 101325.0
        assert ppc.atmosphere == ppc.atm
        assert ppc.bar == 1e5
        assert ppc.torr == ppc.atm / 760.0
        assert ppc.mmHg == ppc.torr

    def test_psi_is_pound_force_per_square_inch(self):
        assert ppc.psi == ppc.pound * ppc.g / (ppc.inch * ppc.inch)
        assert abs(ppc.atm / ppc.psi - 14.6959) < 1e-3


class TestAreaAndVolume:
    def test_area(self):
        assert ppc.hectare == 1e4
        assert ppc.acre == 43560.0 * (ppc.foot * ppc.foot)

    def test_litre(self):
        # A litre is a cubic decimetre: (0.1 m)^3 = 1e-3 m^3, exactly.
        assert ppc.litre == 1e-3
        assert ppc.liter == ppc.litre
        assert abs(ppc.litre - (0.1 * 0.1 * 0.1)) < 1e-18

    def test_us_volume_chain(self):
        assert ppc.gallon == 231.0 * (ppc.inch * ppc.inch * ppc.inch)
        assert ppc.gallon_US == ppc.gallon
        assert ppc.fluid_ounce == ppc.gallon / 128.0
        assert ppc.bbl == 42.0 * ppc.gallon
        assert ppc.barrel == ppc.bbl

    def test_imperial_volume(self):
        assert ppc.gallon_imp == 4.54609e-3
        assert ppc.fluid_ounce_imp == ppc.gallon_imp / 160.0
        # The imperial gallon is the larger of the two.
        assert ppc.gallon_imp > ppc.gallon


class TestSpeed:
    def test_definitions(self):
        assert ppc.kmh == 1e3 / ppc.hour
        assert ppc.mph == ppc.mile / ppc.hour
        assert ppc.knot == ppc.nautical_mile / ppc.hour
        assert ppc.speed_of_sound == ppc.mach

    def test_mach_value(self):
        # scipy's convention: approx. speed of sound at 15 C, 1 atm.
        assert ppc.mach == 340.5
        # A knot is one nautical mile per hour, i.e. 1.852 km/h exactly.
        assert abs(ppc.knot * ppc.hour / 1e3 - 1.852) < 1e-12

    def test_known_conversions(self):
        # 100 km/h is about 62.14 mph.
        assert abs(100.0 * ppc.kmh / ppc.mph - 62.137) < 1e-2


class TestEnergyPowerForce:
    def test_ev_is_elementary_charge(self):
        assert ppc.eV == ppc.e
        assert ppc.electron_volt == ppc.eV

    def test_erg(self):
        # The CGS unit of energy: 1 dyne-centimetre = 1e-5 N * 1e-2 m.
        assert ppc.erg == 1e-7
        assert abs(ppc.erg - ppc.dyn * ppc.centi) < 1e-22

    def test_calories(self):
        assert ppc.calorie == 4.184
        assert ppc.calorie_th == 4.184
        assert ppc.calorie_IT == 4.1868
        assert ppc.ton_TNT == 1e9 * ppc.calorie_th

    def test_btu(self):
        assert ppc.Btu == ppc.Btu_IT
        assert ppc.Btu_th < ppc.Btu_IT
        assert abs(ppc.Btu_IT - 1055.05585262) < 1e-8

    def test_force_family(self):
        assert ppc.dyn == 1e-5
        assert ppc.dyne == ppc.dyn
        assert ppc.lbf == ppc.pound * ppc.g
        assert ppc.pound_force == ppc.lbf
        assert ppc.kgf == ppc.g
        assert ppc.kilogram_force == ppc.kgf

    def test_horsepower(self):
        assert ppc.hp == 550.0 * ppc.foot * ppc.pound * ppc.g
        assert ppc.horsepower == ppc.hp
        assert abs(ppc.hp - 745.6998715822701) < 1e-9


class TestTemperatureConstants:
    def test_zero_celsius(self):
        assert ppc.zero_Celsius == 273.15

    def test_degree_fahrenheit_is_a_difference(self):
        assert ppc.degree_Fahrenheit == 1.0 / 1.8
