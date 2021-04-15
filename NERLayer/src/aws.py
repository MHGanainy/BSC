import time, boto3, logging, random, sys, requests, json
from botocore.exceptions import ClientError

# Initialize Global Variables
AWS_SERVER_PUBLIC_KEY = "AKIAYCCJD3RHCRNOZ6E6"
AWS_SERVER_SECRET_KEY = "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"

s3 = boto3.resource('s3',aws_access_key_id=AWS_SERVER_PUBLIC_KEY,aws_secret_access_key=AWS_SERVER_SECRET_KEY)

bucketName = "mganainy-processed"

def uploadS3Object(file_path, file_name):
    try:
        file_path = file_path + "/" + file_name
        s3.meta.client.upload_file(file_path, bucketName, file_name)
        return "Success"
    except ClientError as error:
        return error

def clear_bucket():
    try:
        bucket = s3.Bucket(bucketName)
        bucket.objects.all().delete()
    except ClientError as error:
        return error
