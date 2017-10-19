####################################################################
#   s3-file-check.py
#   Enumerates s3 files for today and sends notifications otherwise
#   MIT License Copyright (c) 2017 @harkamals
#
#   v1.0 30/08/2017 Harkamal Singh
#   engineering-cloud@
####################################################################

import os
import json
import datetime
import boto3
from botocore.errorfactory import ClientError

# Initialize environment
if os.getenv("LAMBDA_TASK_ROOT", None) == None:
    os.environ["https_proxy"] = "https://sg-cbp-lan-prx01:8080"
else:
    os.environ["https_proxy"] = "https://10.192.116.73:8080"

# Type declarations
s3_client = boto3.client('s3')
""" :type : pyboto3.s3 """


# Send SNS Notification
def send_sns_notification(message):
    print("\tError: %s" % message)
    # add existing code that sends the notification
    #
    #


def lambda_handler(event, context):
    print('Debug: Event received:', json.dumps(event, indent=2))
    print('Debug: Context vars:  ', vars(context))

    today_prefix = (datetime.datetime.utcnow().strftime("%Y%m%d"))
    # today_prefix = "20170829"

    print("S3 file check for today: [%s]" % today_prefix)
    for bucket in ["dev-ds-syslogs", "dev-spark-syslogs"]:
        print("Processing bucket: %s" % bucket)

        try:
            response = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=5, Prefix=today_prefix)
            if 'Contents' in response:
                if [x for x in response['Contents']].__len__() > 0:
                    print("\tSystem normal: Bucket [%s] has received files for today" % bucket)
                else:
                    send_sns_notification("Bucket [%s] has no files for today" % bucket)
            else:
                send_sns_notification("Bucket [%s] has no files for specified filter" % bucket)

        except ClientError as ce:
            if ce.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                send_sns_notification("Bucket [%s] not found" % bucket)
            else:
                send_sns_notification("API [%s]" % ce.message)
        except Exception as ex:
            send_sns_notification("Unknown exception [%s]" % ex)
