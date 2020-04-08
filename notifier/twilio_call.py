import os

from twilio.rest import Client


TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")

TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def call_phone_number(phone_number, message, mp3_link):
    twiml_string = (
        "<Response>"
        "   <Say>{message}</Say>"
        "   <Play>{mp3_link}</Play>"
        "</Response>"
    ).format(
        message=message,
        mp3_link=mp3_link,
    )
    call = TWILIO_CLIENT.calls.create(
        twiml=twiml_string,
        to=phone_number,
        from_=TWILIO_FROM_NUMBER,
    )
    print("Twilio call SID: {}".format(call.sid))
