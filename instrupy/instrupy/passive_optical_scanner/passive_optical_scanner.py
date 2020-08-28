""" 
.. module:: passive_optical_scanner

:synopsis: *Module to handle passive_optical_scanner type of instrument.*
        
"""

import json
import numpy
import copy
import pandas, csv
import random
from instrupy.util import Entity, Orientation, FieldOfView, MathUtilityFunctions, Constants, FileUtilityFunctions, EnumEntity
from instrupy.passive_optical_scanner.passive_optical_scanner_mode1 import PassiveOpticalScannerMode1

class ModeTypePassiveOpticalScanner(EnumEntity):
    """Enumeration of recognized passive optical scanner mode types"""
    MODE1 = "MODE1"

class PassiveOpticalScanner(Entity):
    """A synthetic aperture radar class. Instrument may support multiple operating modes and operating points which are 
       stored in a variable length list.

       :ivar instru_id: Instrument identifier
       :vartype instru_id: str
        
       :ivar ssen_id: List of the Subsensor identifiers in the instrument
       :vartype ssen_id: list, int

       :ivar subsensor: List of the subsensors
       :vartype subsensor: list, :class:`instrupy.synthetic_aperture_radar.synthetic_aperture_radar_mode1`

    """

    def __init__(self, specs = dict()):
        """ Parses an instrument from a normalized JSON dictionary.

        """
        if("@id" in specs):
            instru_id = specs["@id"]
        else:
            instru_id = "pay" + str(random.randint(1,1000000)) # assign a random id. TODO: Improve this to avoid possible conflict in ids (small chance).
            specs.update({"@id":instru_id})

        self.instru_id = instru_id

        if(specs.get("mode", None)):
            mode_data = specs["mode"]
            ssen_id = []
            subsensor = []
            for _data in mode_data: # iterate over list of modes
                
                # create subsensor specifications dict with the data specific to the mode and common data
                _ssen = {key:val for key, val in specs.items() if key != 'mode'} # copy all common items to new dict 
                
                if(_data.get("@id", None) is not None): # check if mode id is specified by user
                    _ssen_id = str(self.instru_id) + str(_data["@id"])
                    
                else: # assign random mode id
                   _ssen_id = str(self.instru_id) +  "mode" + str(random.randint(1,1000000)) #TODO: Improve this to avoid possible conflict in ids (small chance).
                
                _ssen.update({"@id":_ssen_id})
                
                # update and copy the mode specific specifications to the subsensor dict
                try:
                    del _data['@id']
                except:
                    pass
                    
                try:
                    mode_type = ModeTypePassiveOpticalScanner.get(_data.get("@type", None))
                    del _data['@type']
                except:
                    mode_type = ModeTypePassiveOpticalScanner.MODE1 # default to Mode1

                _ssen.update(_data)

                if(mode_type == ModeTypePassiveOpticalScanner.MODE1):
                    ssen_id.append(_ssen_id)
                    subsensor.append(PassiveOpticalScannerMode1.from_dict(_ssen))

        else:
            # no mode definition => default single mode of operation (mode1 = Mode1) is to be considered
            subsensor = [PassiveOpticalScannerMode1.from_dict(specs)]
            ssen_id = [specs["@id"]]
        
        self.ssen_id = ssen_id
        self.subsensor = subsensor

    @staticmethod
    def from_dict(d):
        return PassiveOpticalScanner(d)


    def calc_typ_data_metrics(self, SpacecraftOrbitState = None, TargetCoords = None, ssen_id = None):
        
        if ssen_id is not None:
            _ssen_id_indx = self.ssen_id.index(ssen_id)
            _ssen = self.subsensor[_ssen_id_indx]
        else:
            _ssen = self.subsensor[0]
        
        obsv_metrics = _ssen.calc_typ_data_metrics(SpacecraftOrbitState = SpacecraftOrbitState, TargetCoords = TargetCoords)
        return obsv_metrics