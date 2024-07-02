# Imports
import boto3
import json
import numpy as np
import pandas as pd
import time
import datetime

# Configure the SDK to Personalize:
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')

#create and wait for datasetgroup(isolate your data, event trackers, solutions, Recommenders, and campaigns)
response = personalize.create_dataset_group(
    name='personalize_ecomemerce_ds_group_prac1',
    domain='ECOMMERCE'
)

dataset_group_arn = response['datasetGroupArn']
#print(json.dumps(response, indent=2))

#Create Interactions Schema
interactions_schema = schema = {
    "type": "record",
    "name": "Interactions",
    "namespace": "com.amazonaws.personalize.schema",
    "fields": [
        {
            "name": "USER_ID",
            "type": "string"
        },
        {
            "name": "ITEM_ID",
            "type": "string"
        },
        {
            "name": "TIMESTAMP",
            "type": "long"
        },
        {
            "name": "EVENT_TYPE",
            "type": "string"
            
        }
    ],
    "version": "1.0"
}

create_schema_response = personalize.create_schema(
    name = "personalize-ecommerce-interatn_group_prac1",
    domain = "ECOMMERCE",
    schema = json.dumps(interactions_schema)
)

interaction_schema_arn = create_schema_response['schemaArn']
#print(json.dumps(create_schema_response, indent=2))

#Create Interactions Dataset
dataset_type = "INTERACTIONS"

create_dataset_response = personalize.create_dataset(
    name = "personalize_ecommerce_demo_interactions",
    datasetType = dataset_type,
    datasetGroupArn = dataset_group_arn,
    schemaArn = interaction_schema_arn
)

interactions_dataset_arn = create_dataset_response['datasetArn']
print(json.dumps(create_dataset_response, indent=2))

#Create Personalize Role
iam = boto3.client("iam")

role_name = "PersonalizeRoleEcommerceDemoRecommender2"
assume_role_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "personalize.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
    ]
}

create_role_response = iam.create_role(
    RoleName = role_name,
    AssumeRolePolicyDocument = json.dumps(assume_role_policy_document)
)

# AmazonPersonalizeFullAccess provides access to any S3 bucket with a name that includes "personalize" or "Personalize" 
# if you would like to use a bucket with a different name, please consider creating and attaching a new policy
# that provides read access to your bucket or attaching the AmazonS3ReadOnlyAccess policy to the role
policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonPersonalizeFullAccess"
iam.attach_role_policy(
    RoleName = role_name,
    PolicyArn = policy_arn
)

# Now add S3 support
iam.attach_role_policy(
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess',
    RoleName=role_name
)
time.sleep(10) # wait for a minute to allow IAM role policy attachment to propagate

role_arn = create_role_response["Role"]["Arn"]
#print(role_arn)

# Import the data
#Create Interactions Dataset Import Job
create_interactions_dataset_import_job_response = personalize.create_dataset_import_job(
    jobName = "personalize_ecommerce_demo_interactions_import1",
    datasetArn = interactions_dataset_arn,
    dataSource = {
        "dataLocation": "s3://{}/{}".format(bucket_name, interactions_file_path)
    },
    roleArn = role_arn
)

dataset_interactions_import_job_arn = create_interactions_dataset_import_job_response['datasetImportJobArn']
#print(json.dumps(create_interactions_dataset_import_job_response, indent=2))

#viewd x also viewd (for cold start)
create_recommender_response = personalize.create_recommender(
  name = 'viewed_x_also_viewed_prac2',
  recipeArn = 'arn:aws:personalize:::recipe/aws-ecomm-customers-who-viewed-x-also-viewed',
  datasetGroupArn = dataset_group_arn
)
viewed_x_also_viewed_arn = create_recommender_response["recommenderArn"]
#print (json.dumps(create_recommender_response))

#recommended for you (used user)
create_recommender_response = personalize.create_recommender(
  name = 'recommended_for_you_demo',
  recipeArn = 'arn:aws:personalize:::recipe/aws-ecomm-recommended-for-you',
  datasetGroupArn = dataset_group_arn
)
recommended_for_you_arn = create_recommender_response["recommenderArn"]
#print (json.dumps(create_recommender_response))



# First pick a user
test_user_id = "777"

# Select a random item
test_item_id = "8fbe091c-f73c-4727-8fe7-d27eabd17bea" # a random item: 8fbe091c-f73c-4727-8fe7-d27eabd17bea

# Get recommendations for the user for this item
get_recommendations_response = personalize_runtime.get_recommendations(
    recommenderArn = "arn:aws:personalize:ap-northeast-2:443974114200:recommender/viewed_x_also_viewed_prac1",
    itemId = test_item_id,
    userId = test_user_id,
    numResults = 10
)

# Build a new dataframe for the recommendations
item_list = get_recommendations_response['itemList']
recommendation_list = []

for item in item_list:
    item = get_item_by_id(item['itemId'], items_df)
    recommendation_list.append(item)

user_recommendations_df = pd.DataFrame(recommendation_list, columns = [get_item_by_id(test_item_id, items_df)])

pd.options.display.max_rows =10
#display(user_recommendations_df)