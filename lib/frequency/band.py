from sympy import Interval
from astropy import units as u
from astropy.units import Quantity

class FrequencyBand:
    def __init__(self, low: Quantity, high: Quantity):
        if len(low.shape) != 0 or len(high.shape) != 0:
            raise ValueError('inputs must be scalar')
        self._interval = Interval(start=low.to(u.Hz).value, 
                                  end=high.to(u.Hz).value,
                                  left_open=False,
                                  right_open=False)

    def low(self, unit: u.Unit = u.Hz):
        return (float(self._interval.start) * u.Hz).to(unit)

    def high(self, unit: u.Unit = u.Hz):
        return (float(self._interval.end) * u.Hz).to(unit)

    def tuple(self, unit: u.Unit = u.Hz):
        return self.low(unit), self.high(unit)

    def __str__(self):
        return '(%g Hz, %g Hz)' % (self._interval.start, self._interval.end)

    def intersect(self, x):
        if type(x) != FrequencyBand:
            raise ValueError('input must be of type FrequencyBand')
        new_interval = self._interval.intersect(x._interval)
        if type(new_interval) != Interval:
            return None
        return FrequencyBand.from_interval(x=new_interval, unit=u.Hz)

    def buffer(self, x: Quantity):
        x_hz = x.to(u.Hz)
        new_low = float(self._interval.start) * u.Hz - x_hz
        new_high = float(self._interval.end) * u.Hz + x_hz
        return FrequencyBand(low=new_low, high=new_high)

    def harmonic(self, n: int):
        if n < 1:
            raise ValueError('harmonic input must be positive non-zero integer')
        new_low = float(self._interval.start) * u.Hz * n
        new_high = float(self._interval.end) * u.Hz * n
        return FrequencyBand(low=new_low, high=new_high)

    @staticmethod
    def from_interval(x: Interval, unit: u.Unit):
        return FrequencyBand(low=float(x.start) * unit, high=float(x.end) * unit)

if __name__ == '__main__':
    x = FrequencyBand(low=1.0 * u.MHz, high=5.0 * u.MHz)
    y = FrequencyBand(low=2.5 * u.MHz, high=7.0 * u.MHz)
    z = FrequencyBand(low=5.0 * u.MHz, high=7.5 * u.MHz)

    print(x.intersect(y))
    print(x.intersect(z))
    print(y.intersect(z))

    a = x.buffer(500 * u.kHz)
    print(a)

    b = z.harmonic(2)
    print(b)

    c = x.harmonic(3)
    print(c)