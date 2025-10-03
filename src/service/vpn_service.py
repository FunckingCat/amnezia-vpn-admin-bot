from datetime import datetime
from ..business.pincode_manager import PincodeManager
from ..business.wireguard_manager import WireGuardManager
from ..business.config_generator import ConfigGenerator

class VPNService:
    def __init__(self, config):
        self.config = config
        self.pincode_manager = PincodeManager()
        self.wireguard_manager = WireGuardManager(use_docker_direct=True)
        self.config_generator = ConfigGenerator(config['server.ip'])
    
    def validate_pincode(self, pincode):
        return self.pincode_manager.validate_pincode(pincode)
    
    def get_current_pincode_info(self):
        return self.pincode_manager.get_current_info()
    
    def create_vpn_client(self, user_first_name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = f"{user_first_name}_{timestamp}"
        
        ip = self.wireguard_manager.get_next_available_ip()
        
        private_key, public_key = self.wireguard_manager.generate_keypair()
        
        server_info = self.wireguard_manager.get_server_info()
        
        self.wireguard_manager.add_peer(
            public_key,
            ip,
            server_info['preshared_key']
        )
        
        config = self.config_generator.generate_client_config(
            username,
            private_key,
            ip,
            server_info
        )
        
        qr_code = self.config_generator.create_qr_code(config)
        
        config_filename = self.config_generator.generate_config_filename(username)
        
        return {
            'username': username,
            'ip': ip,
            'config': config,
            'config_filename': config_filename,
            'qr_code': qr_code,
            'server_ip': self.config['server.ip'],
            'server_port': server_info['port'],
            'public_key': public_key
        }
    
    def get_active_peers(self):
        return self.wireguard_manager.get_active_peers()
