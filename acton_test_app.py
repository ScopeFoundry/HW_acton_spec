from __future__ import division, print_function
from ScopeFoundry import BaseMicroscopeApp
#from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

import logging
logging.basicConfig(level=logging.DEBUG)

class SpecTestApp(BaseMicroscopeApp):

    name = 'spec_test_app'
    
    def setup(self):
        
#         from ScopeFoundryHW.andor_camera import AndorCCDHW
#         self.add_hardware(AndorCCDHW(self))

        from ScopeFoundryHW.acton_spec import ActonSpectrometerHW
        self.add_hardware(ActonSpectrometerHW)

#         from ScopeFoundryHW.andor_camera import AndorCCDReadoutMeasure
#         self.add_measurement(AndorCCDReadoutMeasure)
#         
        

if __name__ == '__main__':
    import sys
    app = SpecTestApp(sys.argv)
    sys.exit(app.exec_())