from __future__ import absolute_import
try:
    from .acton_spec_interface import ActonSpectrometer
except Exception as err:
    print("failed to load requirements for acton_spec", err)
from .acton_spec import ActonSpectrometerHW