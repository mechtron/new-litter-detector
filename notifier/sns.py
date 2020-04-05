import os

import boto3


SNS_CLIENT = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def subscribe_user_sms_number_to_sns_topic(user, sns_topic):
    print("Subscribing {} to SNS topic..".format(user["sms_number"]))
    response = SNS_CLIENT.subscribe(
        TopicArn=sns_topic,
        Protocol='sms',
        Endpoint=user["sms_number"],
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def send_sms_notification(user, message):
    # if not user["sms_number_subscribed"]:
    #     subscribe_user_sms_number_to_sns_topic(user, SNS_TOPIC_ARN)
    print("Sending SMS notification to {}..".format(user["sms_number"]))
    response = SNS_CLIENT.publish(
        PhoneNumber=user["sms_number"],
        Message=message,
    )
    assert "MessageId" in response
