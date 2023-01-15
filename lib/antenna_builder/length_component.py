from abc import ABC, abstractmethod
import warnings
from typing import Tuple
from astropy import units
from astropy.units import Quantity


def convert_quantity(ref_quantity: Quantity, in_quantity: Quantity) -> Quantity:
    if not isinstance(in_quantity, units.Quantity):
        raise TypeError('assignment must be of type %s' % units.Quantity)
    if not in_quantity.unit.is_equivalent(ref_quantity.unit):
        raise ValueError('unrecognized unit: %s. must to equivalent to %s' % (in_quantity.unit, ref_quantity.unit))
    return in_quantity.to(ref_quantity.unit)


class LengthComponentUnit:
    def __init__(self, unit: units.UnitBase, equivalent_unit: units.UnitBase = None):
        if not isinstance(unit, units.UnitBase):
            raise TypeError('unit must be be of type %s' % units.UnitBase)
        self._unit = unit
        self._equivalent_unit = unit
        self._observers = []

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_unit: units.UnitBase):
        if not isinstance(new_unit, units.UnitBase):
            raise TypeError('assignment must be be of type %s' % units.Unit)
        if not new_unit.is_equivalent(self._equivalent_unit):
            raise ValueError('unrecognized unit: %s. must to equivalent to %s' % (new_unit, self._equivalent_unit))
        self._unit = new_unit
        for callback in self._observers:
            callback(self._unit)

    def bind_to(self, callback):
        self._observers.append(callback)


class LengthComponent(ABC):
    def __init__(self, length: Quantity, broadcast: LengthComponentUnit = None):
        if not isinstance(length, Quantity):
            raise TypeError('length must be a quantity')
        if not length.unit.is_equivalent(units.m):
            raise ValueError('length unit %s not recognized' % length.unit)
        self._length = length
        if broadcast:
            self._bind_to_broadcast(broadcast, self._set_length_unit)
        else:
            self._broadcast = None

    def _bind_to_broadcast(self, broadcast: LengthComponentUnit, callback):
            if not isinstance(broadcast, LengthComponentUnit):
                raise ValueError('broadcast=%s is not of type %s' % (broadcast, LengthComponentUnit))
            if not broadcast.unit.is_equivalent(units.m):
                raise ValueError('broadcast unit %s is not a recognized length unit' % broadcast.unit)
            self._broadcast = broadcast
            self._length = self._length.to(self._broadcast.unit)
            self._broadcast.bind_to(callback)

    def _set_length_unit(self, unit: units.Unit):
        self._length = self._length.to(unit)

    def get_length(self, unit: units.Unit = None):
        if unit is None:
            return self._length
        if unit.is_equivalent(self._length.unit):
            raise ValueError('unrecognized length %s')
        return self._length.to(unit)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, new_length: Quantity):
        self._length = convert_quantity(self._length, new_length)


class FixedLengthComponent(LengthComponent):
    def __init__(self, length: Quantity, broadcast: LengthComponentUnit = None):
        super().__init__(length=length, broadcast=broadcast)


class AdjustableLengthComponent(LengthComponent):
    def __init__(self, min_length: Quantity, max_length: Quantity, broadcast: LengthComponentUnit = None):
        if not isinstance(min_length, Quantity) or not isinstance(max_length, Quantity):
            raise TypeError('min_length and max_length must be a Quantity')
        if max_length < min_length:
            raise ValueError('minimum length is greater than the maximum length (%s > %s)' % (min_length, max_length))
        if not min_length.unit.is_equivalent(max_length.unit):
            raise ValueError('min length and max length units are not equivalent')
        if min_length == max_length:
            warnings.warn(UserWarning('min length and max length are the same value'))
        if min_length.unit != max_length.unit:
            warnings.warn(UserWarning('min length and max length units are not the same'))
        super().__init__(length=max_length)
        self._min_length = min_length.to(self._length.unit)
        if broadcast:
            self._bind_to_broadcast(broadcast, self._set_length_unit)
        else:
            self._broadcast = None

    def _bind_to_broadcast(self, broadcast: LengthComponentUnit, callback):
        super()._bind_to_broadcast(broadcast, callback)
        self._min_length = self._min_length.to(self._broadcast.unit)

    def _set_length_unit(self, unit: units.Unit):
        self._length = self._length.to(unit)
        self._min_length = self._min_length.to(unit)

    def get_lims(self, unit: units.Unit = None):
        if unit is None:
            return self._min_length, self._length
        if unit.is_equivalent(self._length.unit):
            raise ValueError('unrecognized length %s')
        return self._min_length.to(unit), self._length.to(unit)

    @property
    def lims(self):
        return self._min_length, self._length

    @lims.setter
    def lims(self, new_lims: Tuple[Quantity, Quantity]):
        if len(new_lims) != 2 or not all([isinstance(x, Quantity) for x in new_lims]):
            raise TypeError('lims must be a tuple containing a pair of quantities')
        if new_lims[1] < new_lims[0]:
            raise ValueError('minimum length is greater than the maximum length (%s > %s)' % new_lims)
        if new_lims[0] == new_lims[1]:
            warnings.warn(UserWarning('min length and max length are the same value'))
        if new_lims[0].unit != new_lims[1].unit:
            warnings.warn(UserWarning('min length and max length units are not the same'))
        self.min_length, self.max_length = new_lims

    @property
    def min_length(self):
        return self._min_length

    @min_length.setter
    def min_length(self, new_min_length: Quantity):
        self._min_length = convert_quantity(self._min_length, new_min_length)

    @property
    def max_length(self):
        return self._length

    @max_length.setter
    def max_length(self, new_max_length: Quantity):
        self._length = convert_quantity(self._length, new_max_length)


    
