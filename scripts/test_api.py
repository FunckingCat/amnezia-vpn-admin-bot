#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config_loader import load_config
from src.business.amnezia_api_client import AmneziaAPIClient

def test_api_connection():
    try:
        print("Loading configuration...")
        config = load_config()
        
        api_url = config.get('api.url')
        api_password = config.get('api.password')
        
        print(f"API URL: {api_url}")
        print(f"Password: {'*' * len(api_password)}")
        print()
        
        print("Testing API connection...")
        client = AmneziaAPIClient(api_url, api_password)
        
        print("Fetching session info...")
        session = client.get_session()
        print(f"✅ Session: {session}")
        print()
        
        print("Fetching clients...")
        clients = client.get_clients()
        print(f"✅ Found {len(clients)} clients")
        
        if clients:
            print("\nExisting clients:")
            for idx, c in enumerate(clients, 1):
                print(f"  {idx}. {c.get('name')} - {c.get('address')} - {'Enabled' if c.get('enabled') else 'Disabled'}")
        
        print("\n✅ API connection test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ API connection test failed:")
        print(f"   {str(e)}")
        return False

if __name__ == '__main__':
    success = test_api_connection()
    sys.exit(0 if success else 1)
