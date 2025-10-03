import sys
import argparse
from src.config_loader import load_config
from src.service.vpn_service import VPNService
from src.presentation.telegram_bot import TelegramBot
from src.presentation.rest_api import RestAPI

def main():
    parser = argparse.ArgumentParser(description='Amnezia VPN Admin Bot')
    parser.add_argument('--mode', choices=['bot', 'api', 'both'], default='bot',
                       help='Run mode: bot (Telegram), api (REST API), or both')
    parser.add_argument('--api-port', type=int, default=5000,
                       help='REST API port (default: 5000)')
    
    args = parser.parse_args()
    
    try:
        print("Loading configuration...")
        config = load_config()
        
        print("Initializing VPN service...")
        vpn_service = VPNService(config)
        
        if args.mode == 'api':
            print("Starting REST API only...")
            api = RestAPI(vpn_service, port=args.api_port)
            api.run()
        
        elif args.mode == 'both':
            print("Starting both Telegram bot and REST API...")
            import threading
            
            api = RestAPI(vpn_service, port=args.api_port)
            api_thread = threading.Thread(target=api.run, daemon=True)
            api_thread.start()
            
            print("REST API started in background")
            print("Starting Telegram bot...")
            bot = TelegramBot(config['bot.token'], vpn_service)
            bot.setup_handlers()
            bot.run()
        
        else:
            print("Starting Telegram bot only...")
            bot = TelegramBot(config['bot.token'], vpn_service)
            bot.setup_handlers()
            bot.run()
        
    except Exception as e:
        print(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
