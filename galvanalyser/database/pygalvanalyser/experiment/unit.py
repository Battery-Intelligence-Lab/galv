from .timeseries_data_row import (
    UNIT_UNITLESS,
    UNIT_SECONDS,
    UNIT_VOLTS,
    UNIT_AMPS,
    UNIT_WATT_HOURS,
    UNIT_AMP_HOURS,
    UNIT_CENTIGRADE,
    UNIT_WATTS,
    UNIT_OHMS,
    UNIT_DEGREES,
    UNIT_HERTZ,
)

class Unit:
    conversions = {
        'A': {
            'multiplier': 1,
            'standard_unit': UNIT_AMPS,
        },
        'V': {
            'multiplier': 1,
            'standard_unit': UNIT_VOLTS,
        },
        's': {
            'multiplier': 1,
            'standard_unit': UNIT_SECONDS,
        },
        'W.h': {
            'multiplier': 1,
            'standard_unit': UNIT_WATT_HOURS,
        },
        'A.h': {
            'multiplier': 1,
            'standard_unit': UNIT_AMP_HOURS,
        },
        'mA': {
            'multiplier': 1e-3,
            'standard_unit': UNIT_VOLTS,
        },
        'mA.h': {
            'multiplier': 1e-3,
            'standard_unit': UNIT_AMP_HOURS,
        },
    }
    @classmethod
    def get_all_units(cls):
        return cls.conversions.keys()

    @classmethod
    def convert(cls, symbol, value):
        if symbol not in cls.conversions:
            raise RuntimeError('Unknown Unit {}'.format(symbol))
        return cls.conversions[symbol]['multiplier'] * value




