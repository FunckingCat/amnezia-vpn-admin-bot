import requests
from requests.auth import HTTPBasicAuth
import io

class AmneziaAPIClient:
    def __init__(self, base_url, password):
        self.base_url = base_url.rstrip('/')
        self.password = password
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth('admin', password)
    
    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    def get_clients(self):
        response = self._request('GET', '/api/wireguard/client')
        return response.json()
    
    def create_client(self, name):
        response = self._request('POST', '/api/wireguard/client', json={'name': name})
        return response.json()
    
    def get_client_config(self, client_id):
        response = self._request('GET', f'/api/wireguard/client/{client_id}/configuration')
        return response.text
    
    def get_client_qr(self, client_id):
        response = self._request('GET', f'/api/wireguard/client/{client_id}/qrcode.svg')
        return io.BytesIO(response.content)
    
    def delete_client(self, client_id):
        self._request('DELETE', f'/api/wireguard/client/{client_id}')
        return True
    
    def enable_client(self, client_id):
        self._request('POST', f'/api/wireguard/client/{client_id}/enable')
        return True
    
    def disable_client(self, client_id):
        self._request('POST', f'/api/wireguard/client/{client_id}/disable')
        return True
    
    def get_session(self):
        response = self._request('GET', '/api/session')
        return response.json()
