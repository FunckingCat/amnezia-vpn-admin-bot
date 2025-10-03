import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class TelegramBot:
    def __init__(self, token, vpn_service):
        self.token = token
        self.vpn_service = vpn_service
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Welcome to Amnezia VPN Admin Bot!\n\n"
            "Please enter the 6-digit pincode to create a new VPN configuration."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text.strip()
        
        if len(message) == 6 and message.isdigit():
            await self._handle_pincode(update, message)
        else:
            await update.message.reply_text(
                "Please enter a 6-digit pincode.\n"
                "Use /start to begin."
            )
    
    async def _handle_pincode(self, update: Update, pincode: str):
        if self.vpn_service.validate_pincode(pincode):
            await self._create_vpn_config(update)
        else:
            pincode_info = self.vpn_service.get_current_pincode_info()
            await update.message.reply_text(
                f"Incorrect pincode. Please try again.\n"
                f"(Current valid code: {pincode_info['pincode']} - for debugging)"
            )
    
    async def _create_vpn_config(self, update: Update):
        await update.message.reply_text("Pincode correct! Creating your VPN configuration...")
        
        try:
            user_first_name = update.effective_user.first_name or "User"
            
            await update.message.reply_text("Assigning IP address...")
            
            result = self.vpn_service.create_vpn_client(user_first_name)
            
            await update.message.reply_text(f"✓ Assigned IP: {result['ip']}")
            await update.message.reply_text("✓ Generated keys")
            await update.message.reply_text("✓ Added peer to server")
            
            await update.message.reply_document(
                document=io.BytesIO(result['config'].encode()),
                filename=result['config_filename'],
                caption=f"Configuration for {result['username']}"
            )
            
            await update.message.reply_photo(
                photo=result['qr_code'],
                caption="Scan this QR code with AmneziaWG app"
            )
            
            await update.message.reply_text(
                f"✅ VPN configuration created successfully!\n\n"
                f"Username: {result['username']}\n"
                f"IP: {result['ip']}\n"
                f"Server: {result['server_ip']}:{result['server_port']}\n\n"
                f"Download the .conf file or scan the QR code with AmneziaWG app."
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error creating configuration:\n{str(e)}\n\n"
                f"Please contact the administrator."
            )
    
    def setup_handlers(self):
        self.application = Application.builder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    def run(self):
        if not self.application:
            self.setup_handlers()
        
        print("Bot started and listening...")
        self.application.run_polling()
