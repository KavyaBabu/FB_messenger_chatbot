import os,sys
from flask import Flask, request
from pymessenger import Bot

app = Flask(__name__)

page_access_token = 'EAAStLXY8Gj8BO182U0eyG5wsjOj1j0t9kxV66aSS91PDbWZCaDtuLcDRb9t1BVd61QOjdG2SOy4k9gQnh9E1AAbFyc6FUhwFNn70WPzDt5pR5coGweEVNSP9j84kEogKqz9MgOZB2Y9JcNSvTjaGyJnjo1hCi4pqLdfBA8tg0x40fCTsFFC7mSb9x4ySa2'

bot = Bot(page_access_token)

@app.route('/',methods=['GET'])
def verify():
     if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

     return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    print(data) 
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  
                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]
				    
                    if "text" in messaging_event['message']:                          
                        message_text = messaging_event["message"]["text"]
                    else:
                        message_text = 'no text'
                    
                    response = message_text
                    bot.send_text_message(sender_id,response)
                    
    return "ok", 200

if __name__ == "__main__":
    app.run()