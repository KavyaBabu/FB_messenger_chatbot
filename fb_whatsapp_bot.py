import os,sys
from flask import Flask, request
from pymessenger import Bot
from keras.models import load_model
from keras.utils import pad_sequences
import pickle
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

page_access_token = 'EAAStLXY8Gj8BO182U0eyG5wsjOj1j0t9kxV66aSS91PDbWZCaDtuLcDRb9t1BVd61QOjdG2SOy4k9gQnh9E1AAbFyc6FUhwFNn70WPzDt5pR5coGweEVNSP9j84kEogKqz9MgOZB2Y9JcNSvTjaGyJnjo1hCi4pqLdfBA8tg0x40fCTsFFC7mSb9x4ySa2'

bot = Bot(page_access_token)

model = load_model('news_ChatBot.h5')

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
    message_text = ''
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
                        message_text = 'Message entered is not valid! Bot accepts only Text Articles!'
                    
                    # response = message_text
                    response = test_news([message_text])
                    bot.send_text_message(sender_id,response)
                    
    return "ok", 200

@app.route('/whatsapp/bot',methods=['POST'])
def sms():
        
        from_number = request.form['From']
        to_number = request.form['To']
        body = request.form['Body']
        resp = MessagingResponse()
        if body:            
            message = test_news([body])
            resp.message(message)
        else:
            resp.message("Attachment received! Bot accepts only Text Articles!")
        # print(reply)
        return str(resp)

def test_news(str):

    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    str = tokenizer.texts_to_sequences(str);
    str = pad_sequences(str, maxlen=1000);
    result = (model.predict(str) >=0.5).astype(int);

    value = result[0][0]

    if value == 1:
        return "This is True"
    else:
        return "This is Fake"
    
if __name__ == "__main__":
    app.run(debug=True)