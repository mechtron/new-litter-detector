import os

import boto3


SNS_CLIENT = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def subscribe_user_sms_number_to_sns_topic(sms_number, sns_topic):
    print("Subscribing {} to SNS topic..".format(sms_number))
    response = SNS_CLIENT.subscribe(
        TopicArn=sns_topic,
        Protocol='sms',
        Endpoint=str(sms_number),
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_subscribed_sms_numbers(sns_topic_arn):
    response = SNS_CLIENT.list_subscriptions_by_topic(
        TopicArn=sns_topic_arn,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    subscribed_sms_numbers = []
    for subscription in response["Subscriptions"]:
        subscribed_sms_numbers.append(subscription["Endpoint"])
    return subscribed_sms_numbers


def send_sms_notification(sms_number, message):
    verified_sms_numbers = get_subscribed_sms_numbers(SNS_TOPIC_ARN)
    if sms_number not in verified_sms_numbers:
        subscribe_user_sms_number_to_sns_topic(sms_number, SNS_TOPIC_ARN)
    print("Sending SMS notification to {}..".format(sms_number))
    response = SNS_CLIENT.publish(
        PhoneNumber=str(sms_number),
        Message=message,
    )
    assert "MessageId" in response
