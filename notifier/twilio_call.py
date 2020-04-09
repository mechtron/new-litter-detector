import json
import os

import requests
from requests.auth import HTTPBasicAuth


TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")


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
    resp = requests.post(
        "https://api.twilio.com/2010-04-01/Accounts/{}/Calls.json".format(
            TWILIO_ACCOUNT_SID
        ),
        data={
            "Twiml": twiml_string,
            "To": phone_number,
            "From": TWILIO_FROM_NUMBER,

        },
        auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    print("Twilio call SID: {}".format(json.loads(resp.content)["sid"]))
