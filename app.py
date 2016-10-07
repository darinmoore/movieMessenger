import os
import sys
import json
import imdb

import requests
from flask import Flask, request

app = Flask(__name__)

MOVIE_MIN = 1 # Minimum num of arguments for '!movie'

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # log message for testint

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                
                # if some one sent a message
                if messaging_event.get("message"):  
                    
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    
                    # the message's text
                    message_text = messaging_event["message"]["text"]
                    # adds words in message_text to a list
                    text_words = message_text.split()

                    # if prefixed by '!' then it executes appropiate command
                    if (message_text[0] == '!'):

                        # let's the user search for a movie
                        if (text_words[0].lower() == '!movie'):

                            if (len(text_words) > MOVIE_MIN):
                                # allows access to database
                                ia = imdb.IMDb()

                                # finds first result based on search
                                search = ia.search_movie(' '.join(text_words[1:]))
                                result = search[0]

                                # Gets info about the search result
                                ia.update(result)
                                director = result['director'][0]
                                year = result['year']
                                rating = result['rating'][0]
                                runtime = result['runtime'][0]

                                send_message(sender_id, "Movie Title: " + str(result) + 
                                    "\nYear: " + str(year) + "\nDirector: " + str(director) +
                                    "\nRating: " + str(rating) + "\nRuntime: " + str(runtime) 
                                    + " minutes")

                            # prints appropiate error message
                            else:
                                send_message(sender_id, "Incorrect usage, please include a " + 
                                    "movie to search for")

                        else:
                            usage_message(sender_id)

                    # otherwise it prints the correct usage message
                    else:
                        send_message(sender_id, "Usage error")

                # delivery confirmation
                if messaging_event.get("delivery"):  
                    pass

                # optin confirmation
                if messaging_event.get("optin"):  
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):  
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def usage_message(recipient_id):  # prints usage message for the user
    send_message(recipient_id, "Welcome to Movie_Messenger, here is a list of some commands:\n\n" + 
        "'!movie <movie name>' will return information about the movie passed in")



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
