import json
import boto3
import uuid
from datetime import datetime, timezone
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
sesiones_table = dynamodb.Table('sesiones')

def lambda_handler(event, context):
    """
    Main Lambda handler for CIE-10 text processing and session management
    """
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('path') or event.get('rawPath', '')
        
        # Route based on path
        if path == '/texto' and http_method == 'POST':
            return handle_texto_request(event, context)
        elif path == '/select' and http_method == 'POST':
            return handle_select_request(event, context)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_texto_request(event, context):
    """
    Handle POST /texto request - process text and generate candidates
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        texto = body.get('texto', '').strip()
        
        if not texto:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Texto is required'})
            }
        
        # Truncate texto to 200 characters as specified
        texto_truncated = texto[:200]
        
        # Generate or extract sessionId
        session_id = body.get('sessionId') or str(uuid.uuid4())
        
        # Extract client IP
        client_ip = extract_client_ip(event)
        
        # Generate GPT candidates (placeholder - replace with actual GPT integration)
        candidatos_gpt = generate_gpt_candidates(texto_truncated)
        
        # Save session data to DynamoDB BEFORE returning response
        save_session_data(session_id, texto_truncated, candidatos_gpt, client_ip)
        
        # Return response to frontend
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'sessionId': session_id,
                'candidatos_gpt': candidatos_gpt,
                'codes': candidatos_gpt,  # Alternative field name for compatibility
                'codigos': candidatos_gpt  # Alternative field name for compatibility
            })
        }
        
    except Exception as e:
        logger.error(f"Error in handle_texto_request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Error processing request'})
        }

def handle_select_request(event, context):
    """
    Handle POST /select request - record user's code selection
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('sessionId')
        codigo = body.get('codigo')
        desc = body.get('desc', '')
        
        if not session_id or not codigo:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'sessionId and codigo are required'})
            }
        
        # Here you could save the selection to another table or update the session
        # For now, just return success
        logger.info(f"User selected code {codigo} for session {session_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'ok': True})
        }
        
    except Exception as e:
        logger.error(f"Error in handle_select_request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Error processing selection'})
        }

def extract_client_ip(event):
    """
    Extract client IP from Lambda event (compatible with HTTP API and REST API Gateway)
    """
    # Try different possible locations for client IP
    
    # HTTP API v2.0 format
    request_context = event.get('requestContext', {})
    http_context = request_context.get('http', {})
    if 'sourceIp' in http_context:
        return http_context['sourceIp']
    
    # REST API Gateway format
    if 'identity' in request_context:
        identity = request_context['identity']
        if 'sourceIp' in identity:
            return identity['sourceIp']
    
    # Check headers for forwarded IP (when behind load balancer/proxy)
    headers = event.get('headers', {})
    
    # X-Forwarded-For header (common with load balancers)
    forwarded_for = headers.get('X-Forwarded-For') or headers.get('x-forwarded-for')
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(',')[0].strip()
    
    # X-Real-IP header
    real_ip = headers.get('X-Real-IP') or headers.get('x-real-ip')
    if real_ip:
        return real_ip
    
    # Fallback to a default if no IP found
    return 'unknown'

def generate_gpt_candidates(texto):
    """
    Generate CIE-10 candidates using GPT (placeholder implementation)
    
    This should be replaced with actual GPT integration.
    For now, returns mock data based on input text.
    """
    # This is a placeholder implementation
    # In a real implementation, you would call OpenAI GPT API or similar
    
    # Mock candidates based on common medical terms
    mock_candidates = []
    
    texto_lower = texto.lower()
    
    if 'dolor' in texto_lower or 'pain' in texto_lower:
        mock_candidates.extend([
            {"codigo": "R52", "desc": "Dolor, no clasificado en otra parte"},
            {"codigo": "M25.5", "desc": "Dolor articular"}
        ])
    
    if 'fiebre' in texto_lower or 'fever' in texto_lower:
        mock_candidates.extend([
            {"codigo": "R50.9", "desc": "Fiebre, no especificada"}
        ])
    
    if 'tos' in texto_lower or 'cough' in texto_lower:
        mock_candidates.extend([
            {"codigo": "R05", "desc": "Tos"}
        ])
    
    if 'diabetes' in texto_lower:
        mock_candidates.extend([
            {"codigo": "E11.9", "desc": "Diabetes mellitus no insulinodependiente, sin complicaciones"},
            {"codigo": "E10.9", "desc": "Diabetes mellitus insulinodependiente, sin complicaciones"}
        ])
    
    # If no specific matches, return some general codes or empty list
    if not mock_candidates:
        # Return empty list as specified in requirements (even if empty, must be saved)
        pass
    
    return mock_candidates

def save_session_data(session_id, texto, candidatos_gpt, client_ip):
    """
    Save session data to DynamoDB 'sesiones' table
    """
    try:
        # Create timestamp in UTC
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Create the item to save
        item = {
            'sessionId': session_id,
            'texto': texto,
            'candidatos_gpt': candidatos_gpt,
            'ip_cliente': client_ip,
            'timestamp': timestamp
        }
        
        # Save to DynamoDB in a single put_item operation
        response = sesiones_table.put_item(Item=item)
        
        logger.info(f"Session data saved successfully for sessionId: {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving session data to DynamoDB: {str(e)}")
        # Don't raise the exception - we don't want to fail the request if logging fails
        # But in production, you might want to handle this differently

def get_cors_headers():
    """
    Get CORS headers for responses
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }