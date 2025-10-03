import io
import base64
from flask import Flask, request, jsonify, send_file

class RestAPI:
    def __init__(self, vpn_service, port=5000):
        self.vpn_service = vpn_service
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok', 'service': 'amnezia-vpn-admin-bot'})
        
        @self.app.route('/pincode/current', methods=['GET'])
        def get_current_pincode():
            info = self.vpn_service.get_current_pincode_info()
            return jsonify(info)
        
        @self.app.route('/pincode/validate', methods=['POST'])
        def validate_pincode():
            data = request.get_json()
            if not data or 'pincode' not in data:
                return jsonify({'error': 'Missing pincode'}), 400
            
            is_valid = self.vpn_service.validate_pincode(data['pincode'])
            return jsonify({
                'valid': is_valid,
                'pincode': data['pincode']
            })
        
        @self.app.route('/vpn/create', methods=['POST'])
        def create_vpn_client():
            data = request.get_json()
            
            if not data or 'pincode' not in data:
                return jsonify({'error': 'Missing pincode'}), 400
            
            if not self.vpn_service.validate_pincode(data['pincode']):
                current_info = self.vpn_service.get_current_pincode_info()
                return jsonify({
                    'error': 'Invalid pincode',
                    'current_pincode': current_info['pincode']
                }), 403
            
            username = data.get('username', 'TestUser')
            
            try:
                result = self.vpn_service.create_vpn_client(username)
                
                qr_bytes = result['qr_code'].getvalue()
                qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'username': result['username'],
                    'ip': result['ip'],
                    'config': result['config'],
                    'config_filename': result['config_filename'],
                    'qr_code_base64': qr_base64,
                    'server_ip': result['server_ip'],
                    'server_port': result['server_port'],
                    'public_key': result['public_key']
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/vpn/config/<username>', methods=['GET'])
        def download_config():
            return jsonify({'error': 'Not implemented'}), 501
        
        @self.app.route('/vpn/peers', methods=['GET'])
        def get_active_peers():
            try:
                peers = self.vpn_service.get_active_peers()
                return jsonify({
                    'success': True,
                    'peers': peers
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0'):
        print(f"Starting REST API on {host}:{self.port}...")
        self.app.run(host=host, port=self.port)
