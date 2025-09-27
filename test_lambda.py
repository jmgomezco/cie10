#!/usr/bin/env python3
"""
Test script for lambda_function.py
Tests the core functionality without requiring AWS services
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add current directory to path so we can import lambda_function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock AWS services before importing lambda_function
with patch('boto3.resource') as mock_boto_resource:
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    
    # Import after mocking AWS
    import lambda_function

def test_extract_client_ip():
    """Test the extract_client_ip function with different event formats"""
    
    # Test HTTP API v2.0 format
    event_http_api = {
        'requestContext': {
            'http': {
                'sourceIp': '192.168.1.100'
            }
        }
    }
    assert lambda_function.extract_client_ip(event_http_api) == '192.168.1.100'
    
    # Test REST API Gateway format
    event_rest_api = {
        'requestContext': {
            'identity': {
                'sourceIp': '10.0.0.1'
            }
        }
    }
    assert lambda_function.extract_client_ip(event_rest_api) == '10.0.0.1'
    
    # Test X-Forwarded-For header
    event_forwarded = {
        'headers': {
            'X-Forwarded-For': '203.0.113.1, 192.168.1.1'
        }
    }
    assert lambda_function.extract_client_ip(event_forwarded) == '203.0.113.1'
    
    # Test unknown case
    event_unknown = {}
    assert lambda_function.extract_client_ip(event_unknown) == 'unknown'
    
    print("✓ extract_client_ip tests passed")

def test_generate_gpt_candidates():
    """Test the GPT candidate generation"""
    
    # Test with dolor
    candidates = lambda_function.generate_gpt_candidates("dolor de cabeza")
    assert len(candidates) > 0
    assert any('dolor' in c['desc'].lower() for c in candidates)
    
    # Test with diabetes
    candidates = lambda_function.generate_gpt_candidates("diabetes tipo 2")
    assert len(candidates) > 0
    assert any('diabetes' in c['desc'].lower() for c in candidates)
    
    # Test with unknown text
    candidates = lambda_function.generate_gpt_candidates("texto desconocido sin palabras clave")
    # Should return empty list for unknown text
    assert isinstance(candidates, list)
    
    print("✓ generate_gpt_candidates tests passed")

def test_texto_request_structure():
    """Test the texto request handling structure"""    
    # Mock the DynamoDB table
    with patch('lambda_function.save_session_data') as mock_save:
        # Test valid request
        event = {
            'body': json.dumps({'texto': 'dolor de cabeza'}),
            'requestContext': {
                'http': {
                    'sourceIp': '192.168.1.1'
                }
            }
        }
        
        response = lambda_function.handle_texto_request(event, {})
        
        # Check response structure
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'sessionId' in body
        assert 'candidatos_gpt' in body
        assert isinstance(body['candidatos_gpt'], list)
        
        # Check that save_session_data was called
        mock_save.assert_called_once()
        call_args = mock_save.call_args[0]
        assert len(call_args) == 4  # session_id, texto, candidatos_gpt, client_ip
        assert call_args[1] == 'dolor de cabeza'  # texto
        assert call_args[3] == '192.168.1.1'  # client_ip
        
        print("✓ texto request structure tests passed")

def test_text_truncation():
    """Test that text is properly truncated to 200 characters"""
    # Create a text longer than 200 characters
    long_text = "a" * 250
    
    with patch('lambda_function.save_session_data') as mock_save:
        event = {
            'body': json.dumps({'texto': long_text}),
            'requestContext': {
                'http': {
                    'sourceIp': '192.168.1.1'
                }
            }
        }
        
        response = lambda_function.handle_texto_request(event, {})
        
        # Check that text was truncated
        call_args = mock_save.call_args[0]
        saved_text = call_args[1]
        assert len(saved_text) == 200
        assert saved_text == "a" * 200
        
        print("✓ text truncation tests passed")

def run_tests():
    """Run all tests"""
    try:
        test_extract_client_ip()
        test_generate_gpt_candidates()
        test_texto_request_structure()
        test_text_truncation()
        print("\n✅ All tests passed!")
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)