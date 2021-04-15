import time, boto3, logging, random, sys, requests, json
from botocore.exceptions import ClientError

# Initialize Global Variables
AWS_SERVER_PUBLIC_KEY = ""
AWS_SERVER_SECRET_KEY = ""

s3 = boto3.resource('s3',aws_access_key_id=AWS_SERVER_PUBLIC_KEY,aws_secret_access_key=AWS_SERVER_SECRET_KEY)
textract = boto3.client('textract', region_name='us-east-1', aws_access_key_id=AWS_SERVER_PUBLIC_KEY,aws_secret_access_key=AWS_SERVER_SECRET_KEY)
bucketName = "mganainy-aws-textract"
bucketName2 = "mganainy-processed"
JobIdQueue = []
JobResponseQueue = []

# Initialize Functions
def clear_bucket():
    try:
        bucket = s3.Bucket(bucketName)
        bucket.objects.all().delete()
    except ClientError as error:
        return error
        
def uploadS3Object(file_path, file_name):
    try:
        file_path = file_path + "/" + file_name
        s3.meta.client.upload_file(file_path, bucketName, file_name)
        return "Success"
    except ClientError as error:
        return error

def s3_bucket_file_names():
    filenames = []
    bucket = s3.Bucket(bucketName)
    for bucket_object in bucket.objects.all():
        filenames.append(bucket_object.key)
    return filenames

def startJobForAll():
    filenames = s3_bucket_file_names()
    for file_name in filenames:
        startJob(file_name)

def startJob(file_name):
    try:
        response = textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': bucketName, 'Name': file_name}}, FeatureTypes=["TABLES"])
        JobIdQueue.append(response["JobId"])
        # return "Job Started"
    except ClientError as error:
        return error
    
def isJobComplete(jobId):
    try:
        response = textract.get_document_analysis(JobId=jobId)
        return response["JobStatus"]
    except ClientError as error:
        return error
    
def isJobQComplete():
    while len(JobIdQueue) != 0:
        print(len(JobIdQueue))
        for jobId in JobIdQueue:
            status = isJobComplete(jobId)
            if status == 'SUCCEEDED':
                getJobResults(jobId)
                JobIdQueue.remove(jobId)
                r = requests.post("http://parserlayer:5000/submit", json=json.dumps(JobResponseQueue))
                JobResponseQueue.clear()
                print(r)
        print(status)
        time.sleep(5)
    
def getJobResults(jobId):
    response = textract.get_document_analysis(JobId=jobId)
    JobResponseQueue.append(response)
    return "Job Response Added"

def compareCount():
    bucket1 = s3.Bucket(bucketName)
    bucket2 = s3.Bucket(bucketName2)
    
    b1c = 0
    b2c = 0
    
    for _ in bucket1.objects.all():
        b1c = b1c + 1
    
    for _ in bucket2.objects.all():
        b2c = b2c + 1
    return b1c == b2c
    
    