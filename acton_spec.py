'''
Created on May 28, 2014

@author: Edward Barnard
'''
from __future__ import absolute_import, print_function

from ScopeFoundry import HardwareComponent
try:
    from ScopeFoundryHW.acton_spec.acton_spec_interface import ActonSpectrometer
except Exception as err:
    print("Cannot load required modules for ActonSpectrometer:", err)



class ActonSpectrometerHW(HardwareComponent):
    
    name = "acton_spectrometer"
    
    def setup(self):
        self.debug = False
        
        # Create logged quantities
        self.settings.New('port', dtype=str, initial='COM5')
        self.settings.New('echo', dtype=bool, initial=True) # if serial port echo is enabled, USB echo should be disabled
        
        self.settings.New(
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

        self.settings.New(
                                name='exit_mirror',
                                dtype=str,  
                                choices = [
                                            ("Front (CCD)", "FRONT"),
                                            ("Side (APD)", "SIDE")],
                            )
        
        self.settings.New('entrance_slit', dtype=int, unit='um', reread_from_hardware_after_write=True)
        self.settings.New('exit_slit', dtype=int, unit='um', reread_from_hardware_after_write=True)
        

    def connect(self):
        if self.debug: self.log.info( "connecting to acton_spectrometer" )

        # Open connection to hardware
        self.acton_spectrometer = ActonSpectrometer(port=self.settings['port'], 
                                                    echo=self.settings['echo'],
                                                    debug=self.settings['debug_mode'], 
                                                    dummy=False)

        self.settings.grating_id.change_choice_list(
            tuple([ ("{}: {}".format(num,name), num) for num, name in self.acton_spectrometer.gratings])
            )

        # connect logged quantities
        self.settings.center_wl.connect_to_hardware(
            read_func=self.acton_spectrometer.read_wl,
            write_func=self.acton_spectrometer.write_wl_fast
            )
            
        self.settings.exit_mirror.connect_to_hardware(
            read_func=self.acton_spectrometer.read_exit_mirror,
            write_func=self.acton_spectrometer.write_exit_mirror
            )    

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
