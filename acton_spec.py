'''
Created on May 28, 2014

@author: Edward Barnard

updated 2017-12-06
'''
from __future__ import absolute_import, print_function
import numpy as np

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

        self.settings.New('grating_id', dtype=int, initial=1, choices=(1,2,3,4,5,6))
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
        
        # f (nm), delta (angle), gamma(angle), n0, d_grating(nm), x_pixel(nm),
        # distances stored in nm
        self.settings.New('grating_calibrations', dtype=float, 
                          array=True, initial=[[300e6,0,0,256,0,  (1/150.)*1e6, 16e3,0]]*3)

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

    def get_wl_calibration(self, px_index, binning=1, m_order=1):
        S = self.settings
        grating_id = S['grating_id'] - 1
        grating_calib_array = S['grating_calibrations'][grating_id]
        f, delta, gamma, n0, offset_adjust, d_grating, x_pixel  = grating_calib_array[0:7]
        curvature = 0
        if len(grating_calib_array) > 7:
            curvature = grating_calib_array[7]
        binned_px = binning*px_index + 0.5*(binning-1)
        wl = wl_p_calib(binned_px, n0, offset_adjust, S['center_wl'], m_order, d_grating, x_pixel, f, delta, gamma, curvature)
        
        #print('get_wl_calibration', 'grating#', grating_id, 'grating calib:', S['grating_calibrations'][grating_id], 'center wl:', S['center_wl'], 'output:', wl)
        
        return wl
        
def wl_p_calib(px, n0, offset_adjust, wl_center, m_order, d_grating, x_pixel, f, delta, gamma, curvature=0):
    #print('wl_p_calib:', px, n0, offset_adjust, wl_center, m_order, d_grating, x_pixel, f, delta, gamma, curvature)
    #consts
    #d_grating = 1./150. #mm
    #x_pixel   = 16e-3 # mm
    #m_order   = 1 # diffraction order, unitless
    n = px - (n0+offset_adjust*wl_center)

    #print('psi top', m_order* wl_center)
    #print('psi bottom', (2*d_grating*np.cos(gamma/2)) )

    psi = np.arcsin( m_order* wl_center / (2*d_grating*np.cos(gamma/2)))
    eta = np.arctan(n*x_pixel*np.cos(delta) / (f+n*x_pixel*np.sin(delta)))

    return ((d_grating/m_order)
                    *(np.sin(psi-0.5*gamma)
                      + np.sin(psi+0.5*gamma+eta))) + curvature*n**2