#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.business.pincode_manager import PincodeManager

if __name__ == '__main__':
    info = PincodeManager.get_current_info()
    
    print(f"Current Time: {info['timestamp']}")
    print(f"Day: {info['day']:02d}, Month: {info['month']:02d}, Hour: {info['hour']:02d}")
    print(f"Current Pincode: {info['pincode']}")
