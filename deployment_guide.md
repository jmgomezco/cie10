# Lambda Function Deployment Guide

This guide explains how to deploy the CIE-10 Lambda function that implements session logging to DynamoDB.

## Files Overview

- `lambda_function.py` - Main Lambda function handler
- `requirements.txt` - Python dependencies
- `test_lambda.py` - Unit tests for the Lambda function
- `example_session_data.py` - Shows the session data structure

## Requirements

### DynamoDB Table

Create a DynamoDB table named `sesiones` with the following configuration:

- **Table name**: `sesiones`
- **Partition key**: `sessionId` (String)
- **No sort key needed**
- **Read/Write capacity**: Configure based on expected usage

### Lambda Function Configuration

1. **Runtime**: Python 3.9 or later
2. **Handler**: `lambda_function.lambda_handler`
3. **Memory**: 256 MB (adjust based on GPT API usage)
4. **Timeout**: 30 seconds (adjust based on GPT API response time)

### IAM Permissions

The Lambda execution role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:REGION:ACCOUNT:table/sesiones"
        }
    ]
}
```

### API Gateway Configuration

Configure API Gateway to route:
- `POST /texto` → Lambda function
- `POST /select` → Lambda function

Ensure CORS is enabled for the frontend domain.

## Deployment Steps

1. **Package the Lambda function**:
   ```bash
   pip install -r requirements.txt -t .
   zip -r lambda-function.zip lambda_function.py boto3/ botocore/ other-dependencies/
   ```

2. **Deploy to AWS Lambda**:
   - Upload the zip file to AWS Lambda
   - Set the handler to `lambda_function.lambda_handler`
   - Configure environment variables if needed

3. **Configure API Gateway**:
   - Create or update API Gateway routes
   - Deploy the API to get the endpoint URL
   - Update the frontend's `API_BASE` URL if needed

## Session Data Structure

The Lambda function saves the following data to DynamoDB for each text query:

```json
{
  "sessionId": "uuid-string",
  "texto": "user input truncated to 200 chars",
  "candidatos_gpt": [
    {"codigo": "A01", "desc": "Example diagnosis"},
    ...
  ],
  "ip_cliente": "client.ip.address",
  "timestamp": "2025-09-27T03:35:51Z"
}
```

Key points:
- Data is saved **before** user selection occurs
- Empty `candidatos_gpt` arrays are still saved
- Text is always truncated to 200 characters
- Uses single `put_item` operation
- Compatible with both HTTP API and REST API Gateway IP extraction

## Testing

Run the test suite:

```bash
python3 test_lambda.py
```

## Integration with GPT

The current implementation includes a placeholder `generate_gpt_candidates()` function. Replace this with actual GPT API integration:

1. Add OpenAI or AWS Bedrock client
2. Implement proper prompt engineering for CIE-10 code generation
3. Handle API errors and rate limiting
4. Update dependencies in `requirements.txt`

## Monitoring

Monitor the following:
- Lambda function errors and duration
- DynamoDB write capacity consumption
- API Gateway 4xx/5xx errors
- GPT API call success rates and latency

## Cost Considerations

- DynamoDB write costs (each session = 1 write unit)
- Lambda execution time (depends on GPT API latency)
- API Gateway request costs
- GPT API usage costs