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
    
    name = "acton_spectrometer"
    
    def setup(self):
        self.debug = False
        
        # Create logged quantities
        self.settings.New('port', dtype=str, initial='COM5')
        
        self.center_wl = self.add_logged_quantity(
                                name="center_wl",
                                dtype=float, 
                                fmt="%1.3f",
                                ro=False,
                                unit = "nm",
                                si=False,
                                vmin=-100, vmax=2000,
                                spinbox_decimals = 3,
                                reread_from_hardware_after_write = True
                                )

        self.settings.New('grating_id', dtype=int, choices=(1,2,3,4,5,6))
        self.settings.New('grating_name', dtype=str, ro=True)

        self.exit_mirror = self.add_logged_quantity(
                                                    name='exit_mirror',
                                                    dtype=str,  
                                                    choices = [
                                                                ("Front (CCD)", "FRONT"),
                                                                ("Side (APD)", "SIDE")],
                                                )
        
        self.settings.New('entrance_slit', dtype=int, unit='um', reread_from_hardware_after_write=True)
        self.settings.New('exit_slit', dtype=int, unit='um', reread_from_hardware_after_write=True)
        

        # connect to gui
        try:
            self.center_wl.connect_bidir_to_widget(self.app.ui.acton_spec_center_wl_doubleSpinBox)
            self.exit_mirror.connect_bidir_to_widget(self.app.ui.acton_spec_exitmirror_comboBox)
        except Exception as err:
            self.log.warning("Could not connect to app ui: {}".format( err ))

    def connect(self):
        if self.debug: self.log.info( "connecting to acton_spectrometer" )

        # Open connection to hardware
        self.acton_spectrometer = ActonSpectrometer(port=self.settings['port'], debug=True, dummy=False)

        self.settings.grating_id.change_choice_list(
            tuple([ ("{}: {}".format(num,name), num) for num, name in self.acton_spectrometer.gratings])
            )

        # connect logged quantities
        self.center_wl.hardware_read_func = \
                self.acton_spectrometer.read_wl
        self.center_wl.hardware_set_func = \
                self.acton_spectrometer.write_wl_fast
        
        self.exit_mirror.hardware_read_func = \
                self.acton_spectrometer.read_exit_mirror
        self.exit_mirror.hardware_set_func = \
                self.acton_spectrometer.write_exit_mirror
                

        self.settings.grating_name.connect_to_hardware(
            read_func=self.acton_spectrometer.read_grating_name)
        
        self.settings.grating_id.connect_to_hardware(
            read_func=self.acton_spectrometer.read_grating,
            write_func=self.acton_spectrometer.write_grating
            )

        
        self.settings.entrance_slit.connect_to_hardware(
            read_func=self.acton_spectrometer.read_entrance_slit,
            write_func=self.acton_spectrometer.write_entrance_slit,            
            )

        self.settings.exit_slit.connect_to_hardware(
            read_func=self.acton_spectrometer.read_exit_slit,
            write_func=self.acton_spectrometer.write_exit_slit,            
            )
        

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
