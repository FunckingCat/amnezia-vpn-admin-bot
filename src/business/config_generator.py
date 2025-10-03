import qrcode
import io

class ConfigGenerator:
    def __init__(self, server_ip):
        self.server_ip = server_ip
    
    def generate_client_config(self, username, private_key, ip, server_info):
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {ip}/32
DNS = 8.8.8.8
Jc = {server_info.get('jc', '2')}
Jmin = {server_info.get('jmin', '10')}
Jmax = {server_info.get('jmax', '50')}
S1 = {server_info.get('s1', '25')}
S2 = {server_info.get('s2', '87')}
H1 = {server_info.get('h1', '0')}
H2 = {server_info.get('h2', '0')}
H3 = {server_info.get('h3', '0')}
H4 = {server_info.get('h4', '0')}

[Peer]
PublicKey = {server_info['server_public_key']}
PresharedKey = {server_info['preshared_key']}
AllowedIPs = 0.0.0.0/0
Endpoint = {self.server_ip}:{server_info['port']}
PersistentKeepalive = 25
"""
        return config
    
    def create_qr_code(self, config_text):
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(config_text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return buf
    
    def generate_config_filename(self, username):
        return f"{username}.conf"
