import json
import boto3
import os


def lambda_handler(event, context):
    session = boto3.Session()
    s3 = session.resource("s3")

    file_name = event["file_name"]
    object = s3.Object(os.getenv("BUCKET_NAME"), file_name)
    file_contents = object.get()["Body"].read().decode("utf-8")

    return {
        "statusCode": 200,
        "body": json.dumps(f"{file_name} read!"),
        "file_contents": file_contents,
    }
