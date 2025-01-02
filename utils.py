from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "no user logged in"}), 401
        return f(*args, **kwargs)
    return decorated_function



################################
# SEND LOGS VIA DISCORD WEBHOOK#
################################
import requests
import threading

# Mapping of severity levels to Discord embed colors
SEVERITY_COLORS = {
    "info": 3447003,    # Blue
    "warning": 16776960, # Yellow
    "error": 15158332,   # Red
    "success": 3066993,  # Green
    "debug": 10197915    # Purple
}

HOOKS = {
    "backendLog"    : "https://discord.com/api/webhooks/1314545485222117446/TqlWoYuaQj0znUMXLy2uyY2JxelAuTLxTPrdzM6alLprsWrN18bOSgoJV4aHOsKwdoly",
    "project"       : "https://discord.com/api/webhooks/1300515818399858780/-gn8HVjVh1h7c6h1X_lHC5g0CNzFxoah7htfcC9R7GnXbz4ObhGgd6BpzdortaAjsmWG",
    "user"          : "https://discord.com/api/webhooks/1298363498828664918/lb-HObNM5pptjnRRXr_LCe2GfeeBAGrrJdA-Kgam9VAfW_lVBqBTszQ3xRbvqJ7R7ZEM"
}

def sendLog(severity="debug", message="NoMessageAsArg", webhookLink="backendLog"):
    """
    Sends a Discord webhook with an embed, styled by severity level.

    Args:
        severity (str): 
            - "info": Blue
            - "warning": Yellow
            - "error": Red
            - "success": Green
            - "debug": Purple

        message (str | dict | list): 
            - If `str`: A plain description for the embed.
            - If `dict`:Creates detailed embed fields.
            - If `list`: Creates embed fields.

    Example Usage:
        send_webhook("error", "Conversion failed")
        send_webhook("info", {"Title 1": "Content 1", "Title 2": "Content 2"})
        send_webhook("info", ["Item 1", "Item 2", "Item 3"])
    """
    
    # Define your webhook URL here
    webhook_url = HOOKS[webhookLink]
    
    
    def process_webhook():
        # Get color based on severity, default to black (0) if unknown
        color = SEVERITY_COLORS.get(severity.lower(), 0)  
        embed = {
            "color": color,
            "fields": [],
        }
        
        # If message is a string, add it as a description
        if isinstance(message, str):
            embed["description"] = message
        
        # If message is a dictionary, add fields to embed
        elif isinstance(message, dict):
            embed["fields"] = [{"name": k, "value": v, "inline": True} for k, v in message.items()]
        
        # If message is a list, format it as a description or fields
        elif isinstance(message, list):
            # Join list items as lines in the description
            embed["fields"] = [{"name": f"Value {i+1}", "value": item, "inline": True} for i, item in enumerate(message)]
            # Optionally, you can also split them into individual fields
        
        else:
            return  # Invalid message format, skip sending webhook
            

        # Send the webhook request with the embed
        payload = {"embeds": [embed]}
        requests.post(webhook_url, json=payload)

    # Start the webhook request in a separate thread so it doesn't block
    threading.Thread(target=process_webhook).start()