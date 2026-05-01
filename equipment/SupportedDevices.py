from typing import Dict
from equipment.HP34410A import HP34401A 
from equipment.K195 import K195
from equipment.K2000 import K2000
from equipment.K2400 import K2400
from equipment.NIDAQ import NIDAQ_chassis

SUPPORTED_DEVICES = {
    'HP34410A': HP34401A,
    'K195': K195,
    'K2000': K2000,
    'K2400' : K2400,
    'NIDAQ': NIDAQ_chassis
}