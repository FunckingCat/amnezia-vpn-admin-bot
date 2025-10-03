import sys
from src.config_loader import load_config
from src.service.vpn_service import VPNService
from src.presentation.telegram_bot import TelegramBot

def main():
    try:
        print("Loading configuration...")
        config = load_config()
        
        print("Initializing VPN service...")
        vpn_service = VPNService(config)
        
        print("Setting up Telegram bot...")
        bot = TelegramBot(config['bot.token'], vpn_service)
        bot.setup_handlers()
        
        print("Starting bot...")
        bot.run()
        
    except Exception as e:
        print(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
