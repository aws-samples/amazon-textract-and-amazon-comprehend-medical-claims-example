import boto3
import json
import csv
import os

TEMP_FILE = '/tmp/mycsvfile.csv'

sns = boto3.client('sns') 
s3 = boto3.resource('s3')
sqs_client = boto3.client('sqs')

def convert_to_csv(body):
    json_acceptable_string = body.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    with open(TEMP_FILE, 'w') as f: 
        w = csv.DictWriter(f, d.keys())
        w.writeheader()
        w.writerow(d)


def validate(body):
    json_acceptable_string = body.replace("'", "\"")
    json_data = json.loads(json_acceptable_string)
    print(json_data)
    zip = json_data['ZIP CODE ']
    id = json_data['ID NUMBER ']

    if(not zip.strip().isdigit()):
        return False, id, "Zip code invalid"
    length = len(id.strip())
    if(length != 12):
        return False, id, "Invalid claim Id"
    return True, id, "Ok"


def lambda_handler(event, context):
    
    # SQS queue triggers this function. This reads the key-value from queue
    # validate the form elements and for successful validation it creates k-v CSV
    # file and uploads to S3 bucket. For invalid case it sends a SNS notification

    body = event['Records'][0]['body']

    try:    
        # Validate 
        res, formid, result = validate(body)
        print(result)
        filename = "result/" + (str(formid)).strip() + ".csv"
        if(res):
            # Convert to CSV and upload to S3 bucket
            convert_to_csv(body)
            resultbucket = os.environ['resultbucket']
            s3res = s3.Bucket(resultbucket).upload_file(TEMP_FILE, filename) 
            print(s3res)
        else :
            # Add to invalid queue and send message
            invalidqueue = os.environ['invalidqueue']
            msg = sqs_client.send_message(QueueUrl=invalidqueue,
                                      MessageBody=str(body)+result)
            print(msg)
            snsbody = "Content:" + str(body) + "Reason:" + str(result)
            # Notify
            invalidtopic = os.environ['invalidsns']
            response = sns.publish(
                TopicArn=invalidtopic,
                Message=str(snsbody))
    except Exception as e:
        print("Failed while doing validation")
        print(e.message)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }
