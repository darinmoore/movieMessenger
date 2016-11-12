import send_message as send

def usage_message(recipient_id):  # prints usage message for the user
    send.send_message(recipient_id, "Welcome to Movie_Messenger, here is a list of some commands:\n\n" +
        "'!movie <movie name>' will return information about the movie passed in")
