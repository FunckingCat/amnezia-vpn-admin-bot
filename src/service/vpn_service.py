from datetime import datetime
from ..business.pincode_manager import PincodeManager
from ..business.wireguard_api_manager import WireGuardAPIManager
from ..business.qr_generator import QRCodeGenerator

class VPNService:
    def __init__(self, config):
        self.config = config
        self.pincode_manager = PincodeManager()
        self.wireguard_manager = WireGuardAPIManager(
            config['api.url'],
            config['api.password']
        )
        self.qr_generator = QRCodeGenerator()
    
    def validate_pincode(self, pincode):
        return self.pincode_manager.validate_pincode(pincode)
    
    def get_current_pincode_info(self):
        return self.pincode_manager.get_current_info()
    
    def create_vpn_client(self, user_first_name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = f"{user_first_name}_{timestamp}"
        
        client_result = self.wireguard_manager.create_client(username)
        client_id = client_result['id']
        
        config = self.wireguard_manager.get_client_config(client_id)
        
        qr_code = self.qr_generator.create_qr_from_text(config)
        
        config_filename = f"{username}.conf"
        
        return {
            'username': username,
            'client_id': client_id,
            'ip': client_result.get('address', 'N/A'),
            'config': config,
            'config_filename': config_filename,
            'qr_code': qr_code,
            'public_key': client_result.get('publicKey', 'N/A'),
            'enabled': client_result.get('enabled', True)
        }
    
    def get_active_clients(self):
        return self.wireguard_manager.get_all_clients()
    
    def remove_client(self, client_id):
        return self.wireguard_manager.delete_client(client_id)
    
    def enable_client(self, client_id):
        return self.wireguard_manager.enable_client(client_id)
    
    def disable_client(self, client_id):
        return self.wireguard_manager.disable_client(client_id)
