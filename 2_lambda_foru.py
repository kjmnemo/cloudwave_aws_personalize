# Imports
import boto3
import json
import numpy as np
import pandas as pd
import time
import datetime
from config import a
from config import b

personalize = boto3.client('personalize', region_name='ap-northeast-2')
personalize_runtime = boto3.client('personalize-runtime', region_name='ap-northeast-2')

#lets get recommendation

items_df = pd.read_csv('./items.csv')

def get_item_by_id(item_id, item_df):
    try:
        return items_df.loc[items_df["ITEM_ID"]==str(item_id)]['PRODUCT_NAME'].values[0]
    except:
        print (item_id)
        return "Error obtaining item description"


#get this information from config.py & config.py is written by lambda's argument
# First pick a user
test_user_id = a
# Select a random item
test_item_id = b # a random item: 8fbe091c-f73c-4727-8fe7-d27eabd17bea

# Get recommendations for the user for this item
get_recommendations_response = personalize_runtime.get_recommendations(
    recommenderArn = "arn:aws:personalize:ap-northeast-2:611155787285:recommender/recommended_for_you_cl",
    itemId = test_item_id,
    userId = test_user_id,
    numResults = 10
)

#bring recommend information
time.sleep(2)

# Build a new dataframe for the recommendations
item_list = get_recommendations_response['itemList']
recommendation_list = []

for item in item_list:
    item = get_item_by_id(item['itemId'], items_df)
    recommendation_list.append(item)
print(recommendation_list)

recommendation_df = pd.DataFrame(recommendation_list, columns=['Recommended_Product'])

# Merging the recommendation DataFrame with the items_df DataFrame on the 'PRODUCT_NAME' column
merged_df = pd.merge(recommendation_df, items_df, left_on='Recommended_Product', right_on='PRODUCT_NAME', how='left')
file_name = 'user_recommendation.csv'
merged_df.to_csv(file_name, index=False)

#lambda2.py end
time.sleep(1)
print(a)
print(b)