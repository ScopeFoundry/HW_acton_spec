'''
Created on May 28, 2014

@author: Edward Barnard
'''
from __future__ import absolute_import, print_function

from ScopeFoundry import HardwareComponent
try:
    from .acton_spec_interface import ActonSpectrometer
except Exception as err:
    print("Cannot load required modules for ActonSpectrometer:", err)



class ActonSpectrometerHW(HardwareComponent):
    
    ACTON_SPEC_PORT = "COM13"

    
    def setup(self):
        self.name = "acton_spectrometer"
        self.debug = False
        
        # Create logged quantities
        self.center_wl = self.add_logged_quantity(
                                name="center_wl",
                                dtype=float, 
                                fmt="%1.3f",
                                ro=False,
                                unit = "nm",
                                si=False,
                                vmin=-100, vmax=2000,
                                )
        
        self.center_wl.reread_from_hardware_after_write = True
        self.center_wl.spinbox_decimals = 3

        self.grating = self.add_logged_quantity(
                                name="spec_grating",
                                dtype=str,
                                fmt="%s",
                                ro=True,
                                )

        self.exit_mirror = self.add_logged_quantity(
                                                    name='exit_mirror',
                                                    dtype=str,  
                                                    choices = [
                                                                ("Front (CCD)", "FRONT"),
                                                                ("Side (APD)", "SIDE")],
                                                )

        # connect to gui
        try:
            self.center_wl.connect_bidir_to_widget(self.app.ui.acton_spec_center_wl_doubleSpinBox)
            self.exit_mirror.connect_bidir_to_widget(self.app.ui.acton_spec_exitmirror_comboBox)
        except Exception as err:
            self.log.warning("Could not connect to app ui: {}".format( err ))

    def connect(self):
        if self.debug: self.log.info( "connecting to acton_spectrometer" )

        # Open connection to hardware
        self.acton_spectrometer = ActonSpectrometer(port=self.ACTON_SPEC_PORT, debug=True, dummy=False)

        # connect logged quantities
        self.center_wl.hardware_read_func = \
                self.acton_spectrometer.read_wl
        self.center_wl.hardware_set_func = \
                self.acton_spectrometer.write_wl_fast
        self.grating.hardware_read_func =  \
                self.acton_spectrometer.read_grating_name
        
        self.exit_mirror.hardware_read_func = \
                self.acton_spectrometer.read_exit_mirror
        self.exit_mirror.hardware_set_func = \
                self.acton_spectrometer.write_exit_mirror

        # connect GUI
        try:
            self.center_wl.updated_value[float].connect(
                        self.gui.ui.acton_spec_center_wl_doubleSpinBox.setValue)
            self.grating.updated_value[str].connect(
                        self.gui.ui.acton_spec_grating_lineEdit.setText)
        except Exception as err:
            self.log.warning( "could not connect to custom gui" )

        self.read_from_hardware()


    def disconnect(self):
        self.log.info( "disconnect " + self.name )
        
        #disconnect logged quantities from hardware
        self.settings.disconnect_all_from_hardware()
        
        
        if hasattr(self, 'acton_spectrometer'):
            #disconnect hardware
            self.acton_spectrometer.close()
            
            # clean up hardware object
            del self.acton_spectrometer
