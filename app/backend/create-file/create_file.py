import json
import boto3
import os


def lambda_handler(event, context):
    session = boto3.Session()
    s3 = session.resource("s3")

    file_name = event["file_name"]
    file_contents = event["file_contents"]
    object = s3.Object(os.getenv("BUCKET_NAME"), file_name)
    result = object.put(Body=file_contents)

    return {"statusCode": 200, "body": json.dumps(f"{file_name} saved!")}
