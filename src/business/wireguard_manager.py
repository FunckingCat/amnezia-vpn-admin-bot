import subprocess
import re

class WireGuardManager:
    def __init__(self, server_ip, server_user, server_password):
        self.server_ip = server_ip
        self.server_user = server_user
        self.server_password = server_password
        self.container_name = "amnezia-awg"
        self.config_path = "/opt/amnezia/awg/wg0.conf"
    
    def ssh_exec(self, command):
        full_cmd = f"sshpass -p '{self.server_password}' ssh -o StrictHostKeyChecking=no {self.server_user}@{self.server_ip} \"{command}\""
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    
    def get_next_available_ip(self):
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} cat {self.config_path}")
        
        used_ips = set()
        for line in stdout.split('\n'):
            if 'AllowedIPs' in line:
                match = re.search(r'10\.8\.1\.(\d+)', line)
                if match:
                    used_ips.add(int(match.group(1)))
        
        for i in range(1, 255):
            if i not in used_ips:
                return f"10.8.1.{i}"
        
        raise Exception("No available IPs in range 10.8.1.1-254")
    
    def generate_keypair(self):
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} wg genkey")
        private_key = stdout.strip()
        
        stdout, _, _ = self.ssh_exec(f"echo '{private_key}' | docker exec -i {self.container_name} wg pubkey")
        public_key = stdout.strip()
        
        return private_key, public_key
    
    def get_server_info(self):
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} cat {self.config_path}")
        
        info = {}
        
        for line in stdout.split('\n'):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'ListenPort':
                    info['port'] = value
                elif key in ['Jc', 'Jmin', 'Jmax', 'S1', 'S2', 'H1', 'H2', 'H3', 'H4']:
                    info[key.lower()] = value
        
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} cat /opt/amnezia/awg/wireguard_server_public_key.key")
        info['server_public_key'] = stdout.strip()
        
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} cat /opt/amnezia/awg/wireguard_psk.key")
        info['preshared_key'] = stdout.strip()
        
        return info
    
    def add_peer(self, public_key, ip, preshared_key):
        peer_config = f"""
[Peer]
PublicKey = {public_key}
PresharedKey = {preshared_key}
AllowedIPs = {ip}/32
"""
        
        escaped_config = peer_config.replace("'", "'\\''")
        self.ssh_exec(f"docker exec {self.container_name} sh -c 'echo \"{escaped_config}\" >> {self.config_path}'")
        
        self.ssh_exec(f"docker exec {self.container_name} sh -c 'echo {preshared_key} | wg set wg0 peer {public_key} preshared-key /dev/stdin allowed-ips {ip}/32'")
    
    def get_active_peers(self):
        stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} wg show")
        return stdout
