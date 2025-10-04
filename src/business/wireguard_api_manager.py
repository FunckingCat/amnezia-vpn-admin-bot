from .amnezia_api_client import AmneziaAPIClient

class WireGuardAPIManager:
    def __init__(self, api_url, api_password):
        self.api_client = AmneziaAPIClient(api_url, api_password)
    
    def get_next_available_client_number(self):
        clients = self.api_client.get_clients()
        
        if not clients:
            return 1
        
        used_numbers = set()
        for client in clients:
            name = client.get('name', '')
            if name.startswith('client_'):
                try:
                    num = int(name.split('_')[1])
                    used_numbers.add(num)
                except (IndexError, ValueError):
                    pass
        
        for i in range(1, 10000):
            if i not in used_numbers:
                return i
        
        raise Exception("No available client numbers")
    
    def create_client(self, client_name):
        result = self.api_client.create_client(client_name)
        
        client_id = result.get('id')
        if not client_id:
            raise Exception("Failed to create client: no ID returned")
        
        return {
            'id': client_id,
            'name': result.get('name'),
            'address': result.get('address'),
            'publicKey': result.get('publicKey'),
            'createdAt': result.get('createdAt'),
            'updatedAt': result.get('updatedAt'),
            'enabled': result.get('enabled', True)
        }
    
    def get_client_config(self, client_id):
        return self.api_client.get_client_config(client_id)
    
    def get_client_qr(self, client_id):
        return self.api_client.get_client_qr(client_id)
    
    def get_all_clients(self):
        return self.api_client.get_clients()
    
    def delete_client(self, client_id):
        return self.api_client.delete_client(client_id)
    
    def enable_client(self, client_id):
        return self.api_client.enable_client(client_id)
    
    def disable_client(self, client_id):
        return self.api_client.disable_client(client_id)
