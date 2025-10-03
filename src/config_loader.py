def load_config(config_path='config/credentials.properties'):
    config = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
    except FileNotFoundError:
        raise Exception(f"Configuration file not found: {config_path}")
    
    required_keys = ['bot.token', 'server.ip', 'server.user', 'server.password']
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise Exception(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    return config
