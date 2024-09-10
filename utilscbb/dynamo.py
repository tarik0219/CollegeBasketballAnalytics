import boto3
from config.config import AWS_ACCESS_KEY, AWS_SECRET_KEY



def get_all_team_data():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    table = dynamodb.Table('cbb-ai')
    response = table.scan()
    data = response['Items']
    return data