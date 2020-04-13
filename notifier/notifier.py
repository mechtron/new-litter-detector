import hashlib
from pathlib import Path
import re

from bs4 import BeautifulSoup
import requests
import yaml

from sns import send_sms_notification
from twilio_call import call_phone_number


def page_hash_differs(page_contents, last_known_text_hash):
    hash_object = hashlib.sha1(page_contents.encode('utf-8'))
    digest = hash_object.hexdigest()
    print("The calculated page hash is {}".format(digest))
    return last_known_text_hash.strip() != digest


def last_updated_date_different(page_text, last_updated_date):
    match = re.search(
        r"([0-9]*\/[0-9]*\/[0-9]*)".format(), page_text,
    )
    if match:
        detected_date = match.group(1).strip()
        if last_updated_date.strip() != detected_date:
            print("Unexpected date {}!".format(detected_date))
            return True
    return False


def keyword_detected(page_text, keywords):
    page_text_lower = page_text.lower()
    for keyword in keywords:
        if keyword.lower() in page_text_lower:
            print("Keyword detected {}!".format(keyword))
            return keyword
    return False


def get_page_text(url):
    r = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(r.content, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text()
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text_no_blanks = '\n'.join(chunk for chunk in chunks if chunk)
    return text_no_blanks


def load_config():
    config_path = "{}/config.yml".format(Path(__file__).parent.absolute())
    with open(config_path, "r") as stream:
        return yaml.safe_load(stream)


def generate_phone_call_message(keyword_detected):
    return (
        "Hello fellow dog seeker! I detected the keyword {keyword_detected}"
        " - do you think there could be a new litter?!"
    ).format(
        keyword_detected=keyword_detected,
    )


def check_for_phone_alerts(config, page_contents):
    if "keywords_phone" in config:
        keyword = keyword_detected(page_contents, config["keywords_phone"])
        if keyword:
            print("Page updated! A phone keyword was detected.")
            for alert_number in config["phone_numbers"]:
                call_phone_number(
                    alert_number,
                    generate_phone_call_message(keyword),
                    "https://www.redringtones.com/wp-content/uploads/2018/03/who-let-the-dogs-out-ringtone.mp3",
                )
    else:
        print("No phone-priority page changes detected")


def generate_sms_message(reason, page_url):
    return (
        "A change was detected ({reason})! Check it out: {page_url}".format(
            reason=reason, page_url=page_url
        )
    )


def check_for_sms_alerts(config, page_contents):
    reason = None
    if (
        "keywords_sms" in config and
        keyword_detected(page_contents, config["keywords_sms"])
    ):
        print("Page updated! A keyword was detected.")
        if not reason:
            reason = "keyword detected"
    if (
        "last_updated" in config and
        last_updated_date_different(page_contents, config["last_updated"])
    ):
        print("Page updated! Last modified date differs.")
        if not reason:
            reason = "last updated date different"
    if (
        "last_known_text_hash" in config and
        page_hash_differs(page_contents, config["last_known_text_hash"])
    ):
        print("Page hash differs! An unkown change was detected.")
        if not reason:
            reason = "unknown change detected"
    if reason:
        for alert_number in config["sms_numbers"]:
            send_sms_notification(
                alert_number,
                generate_sms_message(
                    reason, config["page_url"]
                ),
            )
    else:
        print("No page changes detected")


def main():
    config = load_config()
    page_contents = get_page_text(config["page_url"])
    check_for_phone_alerts(config, page_contents)
    check_for_sms_alerts(config, page_contents)


def handler(_event, _context):
    main()


if __name__ == "__main__":
    main()
