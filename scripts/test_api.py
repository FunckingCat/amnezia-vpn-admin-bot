#!/usr/bin/env python3

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.business.pincode_manager import PincodeManager

def test_api(base_url):
    print(f"Testing API at {base_url}")
    print("=" * 60)
    
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print("\n2. Getting current pincode...")
    try:
        response = requests.get(f"{base_url}/pincode/current", timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Current pincode: {data['pincode']}")
        print(f"   Timestamp: {data['timestamp']}")
        current_pincode = data['pincode']
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print("\n3. Validating incorrect pincode...")
    try:
        response = requests.post(
            f"{base_url}/pincode/validate",
            json={'pincode': '000000'},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n4. Validating correct pincode...")
    try:
        response = requests.post(
            f"{base_url}/pincode/validate",
            json={'pincode': current_pincode},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n5. Creating VPN client...")
    try:
        response = requests.post(
            f"{base_url}/vpn/create",
            json={'pincode': current_pincode, 'username': 'TestUser'},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Username: {data['username']}")
            print(f"   IP: {data['ip']}")
            print(f"   Server: {data['server_ip']}:{data['server_port']}")
            print(f"   Config length: {len(data['config'])} chars")
            print(f"   QR code: {len(data['qr_code_base64'])} bytes (base64)")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n6. Getting active peers...")
    try:
        response = requests.get(f"{base_url}/vpn/peers", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Peers info length: {len(data['peers'])} chars")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API testing complete!")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"Current pincode: {PincodeManager.generate_pincode()}")
    print()
    
    test_api(base_url)
