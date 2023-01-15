import pytest
from astropy import units
from lib.antenna_builder.length_component import LengthComponentUnit, LengthComponent, AdjustableLengthComponent

def test_component_unit_assignment():
    x = LengthComponentUnit(unit=units.m)

    assert id(x.unit) == id(x.unit)
    x.unit = units.km

    assert id(x.unit) == id(units.km)
    with pytest.raises(ValueError):
        x.unit = units.second

    y = x.unit
    y = units.AU
    assert id(x.unit) != id(y)


def test_length_component_assignment():
    x = LengthComponent(length=1.0 * units.m)
    assert x.length == 1.0 * units.m

    with pytest.raises(ValueError):
        LengthComponent(length=1.0 * units.second)

    x.length = 3.0 * units.AU
    assert x.length == 3.0 * units.AU


def test_length_component_broadcast():
    x = LengthComponentUnit(unit=units.m)
    y = LengthComponent(length=1.0 * units.km, broadcast=x)
    assert y.length.unit == units.m
    x.unit = units.AU
    assert y.length.unit == units.AU


@pytest.mark.parametrize("error_makers", [
    (1.0 * units.m,),
    None,
])
def test_length_component_type_errors(error_makers):
    print(error_makers)
    with pytest.raises(TypeError):
        LengthComponent(error_makers)
    with pytest.raises(TypeError):
        x = LengthComponent(length= 1.0 * units.m)
        x.length = error_makers


@pytest.mark.parametrize("error_makers", [
    1.0 * units.second,
    1.0 * units.W,
])
def test_length_component_value_errors(error_makers):
    print(error_makers)
    with pytest.raises(ValueError):
        LengthComponent(error_makers)
    with pytest.raises(ValueError):
        x = LengthComponent(length= 1.0 * units.m)
        x.length = error_makers

def test_adjustable_component_assignment():
    x = AdjustableLengthComponent(min_length= 0.0 * units.m, max_length=1.0 * units.m)
    assert x.min_length == 0.0 * units.m
    assert x.max_length == 1.0 * units.m
    assert x.lims == (0.0 * units.m, 1.0 * units.m)

    x.lims = (0.0 * units.m, 10.0 * units.m)
    assert x.lims == (0.0 * units.m, 10.0 * units.m)


@pytest.mark.parametrize("warn_makers", [
    (1.0 * units.m, 1.0 * units.m),
    (1.0 * units.m, 1.0 * units.km),
    (1.0 * units.m, 1.0 * units.AU),
])
def test_adjustable_component_lims_warnings(warn_makers):
    with pytest.warns(UserWarning):
        AdjustableLengthComponent(*warn_makers)
    with pytest.warns(UserWarning):
        x = AdjustableLengthComponent(min_length= 1.0 * units.m, max_length=10.0 * units.m)
        x.lims = warn_makers


@pytest.mark.parametrize("error_makers", [
    (100.0 * units.m, 1.0 * units.m),
    (1.0 * units.km, 1.0 * units.m),
    (1.0 * units.m, 1.0 * units.second),
    (1.0 * units.second, 1.0 * units.m),
    (1.0 * units.second, 2.0 * units.second),
])
def test_adjustable_component_lims_value_errors(error_makers):
    with pytest.raises(ValueError):
        AdjustableLengthComponent(*error_makers)
    with pytest.raises(ValueError):
        x = AdjustableLengthComponent(min_length= 1.0 * units.m, max_length=10.0 * units.m)
        x.lims = error_makers


@pytest.mark.parametrize("error_makers", [
    (100.0, 1.0),
    (1.0, 2.0),
    (1.0 * units.m),
    None,
    (None, None),
])
def test_adjustable_component_lims_type_errors(error_makers):
    with pytest.raises(TypeError):
        AdjustableLengthComponent(*error_makers)
    with pytest.raises(TypeError):
        x = AdjustableLengthComponent(min_length= 1.0 * units.m, max_length=10.0 * units.m)
        x.lims = error_makers
