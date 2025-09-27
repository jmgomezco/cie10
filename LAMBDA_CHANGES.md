# Lambda Function Changes

## Added `ip_cliente` field to DynamoDB items

This implementation adds the `ip_cliente` field to items saved in DynamoDB and includes it in the Lambda response.

### Key Changes:

1. **IP Extraction**: The client IP is extracted using:
   ```python
   ip_cliente = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "")
   ```

2. **DynamoDB Storage**: The `ip_cliente` field is included in the item saved to DynamoDB:
   ```python
   item = {
       'id': str(uuid.uuid4()),
       'timestamp': datetime.utcnow().isoformat(),
       'ip_cliente': ip_cliente,
       **body
   }
   ```

3. **Response**: The `ip_cliente` is returned in both success and error responses:
   ```python
   response_body = {
       'message': 'Item saved successfully',
       'id': item['id'],
       'ip_cliente': ip_cliente,
       'timestamp': item['timestamp']
   }
   ```

### Behavior:
- If `event["requestContext"]["identity"]["sourceIp"]` exists, it uses that IP address
- If not available, defaults to empty string `""`
- IP is included in both successful and error responses
- IP is saved in DynamoDB alongside other item data