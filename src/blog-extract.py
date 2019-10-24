import json
import os
import boto3
import sys
import re
import json
import csv

client = boto3.client('textract')
sqs_client = boto3.client('sqs')

def get_kv_map(obj, bucket):

    # process using image bytes
    try:
        response = client.analyze_document(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': obj
            },
        },
        FeatureTypes=['FORMS']
        )

        # Get the text blocks
        blocks=response['Blocks']

        # get key and value maps
        key_map = {}
        value_map = {}
        block_map = {}
        curr_pos = 0
        line_val = ""
        for block in blocks:
            curr_pos=curr_pos + 1
            block_id = block['Id']
            block_map[block_id] = block
            if block['BlockType'] == "KEY_VALUE_SET":
                if 'KEY' in block['EntityTypes']:
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block
            if block['BlockType'] == "LINE":
                if block['Text'] == "PROCEDURE":
                    block = blocks[curr_pos]
                    line_val = block['Text']
                    
        return key_map, value_map, block_map, line_val
    except:
        print("Failed while parsing the document")
        raise 
    
    
def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key] = val
    print(kvs)
    return kvs


def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '


    return text


def print_kvs(kvs):
    for key, value in kvs.items():
        print(key, ":", value)


def search_value(kvs, search_key):
    for key, value in kvs.items():
        if re.search(search_key, key, re.IGNORECASE):
            return value


def lambda_handler(event, context):
    
    # This code gets triggered by a object upload in S3 Bucket.
    # It sends object from S3 bucket to textract for key-value extracttion.
    # In successful extraction it stores key-value pairs in S3 as CSV file.
    # In case of failures it prompts message.
    
    print(event)
    obj=event['Records'][0]['s3']['object']['key']
    print(obj)
    bucket=event['Records'][0]['s3']['bucket']['name']
    
    try:
        key_map, value_map, block_map, line_val = get_kv_map(obj, bucket)

        # Get Key Value relationship
        kvs = get_kv_relationship(key_map, value_map, block_map)
        kvs['PROCEDURE'] = line_val
        print("\n\n== FOUND KEY : VALUE pairs ===\n")
        print_kvs(kvs)
    
        # Add to Queue for validation
        queue = os.environ['allqueue']
        print(queue)
        msg = sqs_client.send_message(QueueUrl=queue,
                                      MessageBody=str(kvs))

        print(msg)
    except Exception as e:
        print("Failed in processing file")
        print(e.message)

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }
