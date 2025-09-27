import json
import boto3
import uuid
from datetime import datetime

# DynamoDB client will be initialized when needed
dynamodb = None
table = None

def get_dynamodb_table():
    """Initialize DynamoDB client and table when needed"""
    global dynamodb, table
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('cie10-table')  # Replace with your actual table name
    return table

def lambda_handler(event, context):
    """
    AWS Lambda handler function that processes requests and saves items to DynamoDB.
    Extracts client IP address and includes it in the saved item and response.
    """
    
    # Extract client IP address from the event
    ip_cliente = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "")
    
    try:
        # Parse request body if it exists
        body = {}
        if 'body' in event and event['body']:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Create item to save in DynamoDB
        item = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'ip_cliente': ip_cliente,
            # Add other fields from the request body
            **body
        }
        
        # Save item to DynamoDB
        table = get_dynamodb_table()
        table.put_item(Item=item)
        
        # Prepare response
        response_body = {
            'message': 'Item saved successfully',
            'id': item['id'],
            'ip_cliente': ip_cliente,
            'timestamp': item['timestamp']
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        error_response = {
            'error': 'Failed to process request',
            'message': str(e),
            'ip_cliente': ip_cliente
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps(error_response)
        }