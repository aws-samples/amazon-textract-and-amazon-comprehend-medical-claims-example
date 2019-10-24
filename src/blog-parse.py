import boto3
import json
import csv
from io import StringIO

TEMP_FILE = '/tmp/cmresult.csv'

s3 = boto3.resource('s3')
comprehend = boto3.client(service_name='comprehendmedical')

def lambda_handler(event, context):

    # This gets triggered from when CSV obj file is add to S3 bucket.
    # It extracts the value for the key "PROCEDURE" and analyzes through
    # comprehend medical to extract various enties. Then it writes these
    # results to S3 as CSV file
    
    obj=event['Records'][0]['s3']['object']['key']
    bucket=event['Records'][0]['s3']['bucket']['name']
    try:
        obj = s3.Object(bucket, obj)
        data = obj.get()['Body'].read().decode('utf-8')
        f = StringIO(data)
        reader = csv.DictReader(f)
        row1=next(reader)
        data = row1["PROCEDURE"]
        
        json_data = comprehend.detect_entities(Text=data)
        entities = json_data['Entities']
        with open(TEMP_FILE, 'w') as csvfile: # 'w' will truncate the file
            filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['ID NUMBER', 'Category', 'Type', 'Text'])
            for entity in entities:
                filewriter.writerow([row1['ID NUMBER '], entity['Category'], entity['Type'], entity['Text']])

        filename = "procedureresult/" + (str(row1["ID NUMBER "])).strip() + ".csv"

        s3.Bucket(bucket).upload_file(TEMP_FILE, filename)
        print("successfully parsed:" + filename)
    except Exception as e:
        print("Failed to get Procedure results")
        print(e.message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }
