#!/usr/bin/env python3
"""
Example demonstrating the session data structure that will be saved to DynamoDB
"""

import json
import uuid
from datetime import datetime

def create_example_session_data():
    """Create example session data as specified in requirements"""
    
    # Example 1: Session with candidates found
    session_with_candidates = {
        "sessionId": str(uuid.uuid4()),
        "texto": "dolor de cabeza intenso con fiebre",
        "candidatos_gpt": [
            {"codigo": "R51", "desc": "Cefalea"},
            {"codigo": "R50.9", "desc": "Fiebre, no especificada"},
            {"codigo": "G44.1", "desc": "Cefalea vascular, no clasificada en otra parte"}
        ],
        "ip_cliente": "203.0.113.1",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    # Example 2: Session with empty candidates (as required by specifications)
    session_empty_candidates = {
        "sessionId": str(uuid.uuid4()),
        "texto": "texto sin palabras clave médicas específicas que no genera candidatos",
        "candidatos_gpt": [],  # Empty list as specified - must still be saved
        "ip_cliente": "192.168.1.100",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    # Example 3: Session with text truncated to 200 characters
    long_text = "dolor abdominal severo que comenzó hace 3 días en el lado derecho del abdomen, se ha intensificado gradualmente y ahora es constante, acompañado de náuseas y vómitos ocasionales, sin fiebre significativa pero con malestar general" + " texto adicional que será truncado"
    session_truncated_text = {
        "sessionId": str(uuid.uuid4()),
        "texto": long_text[:200],  # Truncated to 200 characters as required
        "candidatos_gpt": [
            {"codigo": "K35.9", "desc": "Apendicitis aguda, no especificada"},
            {"codigo": "R10.3", "desc": "Dolor localizado en otras partes inferiores del abdomen"}
        ],
        "ip_cliente": "10.0.0.1",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    return [session_with_candidates, session_empty_candidates, session_truncated_text]

def main():
    """Print example session data structures"""
    examples = create_example_session_data()
    
    print("=== EXAMPLE SESSION DATA STRUCTURES ===")
    print("These are examples of the data that will be saved to DynamoDB 'sesiones' table:")
    print()
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}:")
        print(json.dumps(example, indent=2, ensure_ascii=False))
        print()
        
    print("Key points about the implementation:")
    print("- sessionId: Generated UUID or received from client")
    print("- texto: Always truncated to 200 characters maximum")
    print("- candidatos_gpt: Final GPT candidates list (can be empty)")
    print("- ip_cliente: Extracted from Lambda event (HTTP API/REST API compatible)")
    print("- timestamp: Current UTC time in ISO format")
    print("- Saved BEFORE user selects any code (in /texto endpoint)")
    print("- Uses single put_item operation to DynamoDB")

if __name__ == "__main__":
    main()