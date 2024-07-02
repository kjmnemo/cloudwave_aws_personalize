import boto3
from config import a
from config import b
s3_client = boto3.client('s3')

#we can upload the pythonscript
file_name = 'user_recommendation.csv'
bucket_name = "ap-northeast-2-cloudladder-personalize"
object_name = f'recommend_{a}.csv'

with open(file_name, 'rb') as f:
    s3_client.upload_fileobj(f, bucket_name, object_name)