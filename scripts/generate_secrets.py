#!/usr/bin/env python3
"""
Generate secure secret keys for .env file
"""

import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def update_env_file():
    """Update .env file with new secret keys"""
    env_path = Path('.env')
    
    # Read existing .env file
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        # If .env doesn't exist, read from .env.example
        with open('.env.example', 'r') as f:
            lines = f.readlines()
    
    # Generate new secrets
    session_secret = generate_secret_key()
    flask_secret = generate_secret_key()
    
    # Update secrets in the file
    new_lines = []
    for line in lines:
        if line.startswith('SESSION_SECRET='):
            new_lines.append(f'SESSION_SECRET={session_secret}\n')
        elif line.startswith('FLASK_SECRET_KEY='):
            new_lines.append(f'FLASK_SECRET_KEY={flask_secret}\n')
        else:
            new_lines.append(line)
    
    # Write updated content back to .env
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print("Generated new secret keys and updated .env file")
    print("Make sure to restart your application for changes to take effect")

if __name__ == '__main__':
    # Create scripts directory if it doesn't exist
    os.makedirs('scripts', exist_ok=True)
    
    try:
        update_env_file()
    except Exception as e:
        print(f"Error updating .env file: {e}")
        print("Make sure .env or .env.example exists in the project root") 