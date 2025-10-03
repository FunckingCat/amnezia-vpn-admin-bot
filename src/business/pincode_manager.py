from datetime import datetime

class PincodeManager:
    @staticmethod
    def generate_pincode():
        now = datetime.now()
        day = str(now.day).zfill(2)
        month = str(now.month).zfill(2)
        hour = str(now.hour).zfill(2)
        
        digits = day + month + hour
        
        pincode = ''
        for d in digits:
            digit = int(d)
            pincode += str(digit + 1 if digit < 9 else digit)
        
        return pincode
    
    @staticmethod
    def validate_pincode(pincode):
        if not pincode or len(pincode) != 6 or not pincode.isdigit():
            return False
        
        correct_pincode = PincodeManager.generate_pincode()
        return pincode == correct_pincode
    
    @staticmethod
    def get_current_info():
        now = datetime.now()
        return {
            'timestamp': now.strftime("%Y-%m-%d %H:%M:%S"),
            'day': now.day,
            'month': now.month,
            'hour': now.hour,
            'pincode': PincodeManager.generate_pincode()
        }
