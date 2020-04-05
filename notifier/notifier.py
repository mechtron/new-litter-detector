import hashlib
from pathlib import Path
import re

from bs4 import BeautifulSoup
import requests
import yaml

from sns import send_sms_notification


def generate_sms_message(reason, page_url):
    return (
        "A change was detected ({reason})! Check it out: {page_url}".format(
            reason=reason, page_url=page_url
        )
    )


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
        detected_date = match.group(1)
        if last_updated_date.strip() != detected_date.strip():
            return True
    return False


def keyword_detected(page_text, keywords):
    page_text_lower = page_text.lower()
    for keyword in keywords:
        if keyword.lower() in page_text_lower:
            return True
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


def main():
    config = load_config()
    page_contents = get_page_text(config["page_url"])
    reason = None
    if keyword_detected(page_contents, config["keywords"]):
        print("Page updated! A keyword was detected.")
        reason = "keyword detected"
    elif last_updated_date_different(page_contents, config["last_updated"]):
        print("Page updated! Last modified date differs.")
        reason = "last updated date different"
    elif page_hash_differs(page_contents, config["last_known_text_hash"]):
        print("Page hash differs! An unkown change was detected.")
        reason = "unknown change detected"
    else:
        print("No page changes detected")
    if reason:
        for alert_number in config["alert_numbers"]:
            send_sms_notification(
                alert_number,
                generate_sms_message(
                    reason, config["page_url"]
                ),
            )


def handler(_event, _context):
    main()


if __name__ == "__main__":
    main()
