#!/usr/bin/env python3
"""
White-label client setup script.
Creates new client configurations for voice agents.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

from white_label_config import ClientConfig, white_label_manager


def create_sample_client():
    """Create a sample client configuration."""
    sample_config = ClientConfig(
        client_id="demo_client",
        company_name="Demo Company LLC",
        brand_name="Demo Solutions",
        voice_name="Celeste-PlayAI",
        agent_persona="friendly business consultant",
        services=[
            "Business Consulting",
            "Marketing Strategy", 
            "Process Optimization"
        ],
        pricing_tiers={
            "Starter": {
                "price": "$99/month",
                "features": ["Basic consulting", "Email support"]
            },
            "Professional": {
                "price": "$299/month", 
                "features": ["Advanced consulting", "Priority support", "Custom reports"]
            }
        },
        contact_info={
            "phone": "1-800-DEMO-123",
            "email": "contact@democompany.com",
            "website": "democompany.com"
        },
        custom_responses={
            "about us": "Demo Company has been helping businesses succeed for over 10 years with proven strategies and personalized support.",
            "consulting": "Our business consulting helps you identify growth opportunities and streamline operations for maximum efficiency."
        },
        max_tokens=120
    )
    
    if white_label_manager.create_client(sample_config):
        print(f"✅ Created sample client: {sample_config.client_id}")
        return True
    else:
        print("❌ Failed to create sample client")
        return False


def interactive_client_setup():
    """Interactive client setup process."""
    print("\n🏷️  White-label Client Setup")
    print("=" * 40)
    
    # Basic information
    client_id = input("Client ID (lowercase, no spaces): ").strip().lower().replace(" ", "_")
    company_name = input("Company Name: ").strip()
    brand_name = input("Brand Name (for customer-facing): ").strip()
    
    # Voice settings
    print("\nAvailable voices: Celeste-PlayAI, Adam-PlayAI, Sofia-PlayAI")
    voice_name = input("Voice name [Celeste-PlayAI]: ").strip() or "Celeste-PlayAI"
    
    agent_persona = input("Agent persona (e.g., 'friendly sales consultant'): ").strip()
    
    # Services
    print("\nEnter services (one per line, empty line to finish):")
    services = []
    while True:
        service = input("Service: ").strip()
        if not service:
            break
        services.append(service)
    
    # Contact info
    print("\nContact Information (optional, press Enter to skip):")
    contact_info = {}
    phone = input("Phone: ").strip()
    if phone:
        contact_info["phone"] = phone
    
    email = input("Email: ").strip()
    if email:
        contact_info["email"] = email
    
    website = input("Website: ").strip()
    if website:
        contact_info["website"] = website
    
    # Token limit
    try:
        max_tokens = int(input("Max response tokens [150]: ") or "150")
    except ValueError:
        max_tokens = 150
    
    # Create configuration
    client_config = ClientConfig(
        client_id=client_id,
        company_name=company_name,
        brand_name=brand_name,
        voice_name=voice_name,
        agent_persona=agent_persona,
        services=services,
        contact_info=contact_info,
        max_tokens=max_tokens
    )
    
    # Confirm and save
    print(f"\n📋 Configuration Summary:")
    print(f"Client ID: {client_config.client_id}")
    print(f"Company: {client_config.company_name}")
    print(f"Brand: {client_config.brand_name}")
    print(f"Services: {', '.join(client_config.services)}")
    
    if input("\nSave this configuration? (y/N): ").lower() == 'y':
        if white_label_manager.create_client(client_config):
            print(f"✅ Created client configuration: {client_config.client_id}")
            
            # Show usage instructions
            print(f"\n🚀 Usage Instructions:")
            print(f"1. Start the voice agent with client header:")
            print(f"   X-Client-ID: {client_config.client_id}")
            print(f"2. Or use subdomain: {client_config.client_id}.yourdomain.com")
            print(f"3. Client config saved to: clients/{client_config.client_id}.json")
            
            return True
        else:
            print("❌ Failed to create client configuration")
            return False
    else:
        print("❌ Configuration cancelled")
        return False


def list_clients():
    """List all configured clients."""
    clients = white_label_manager.list_clients()
    if not clients:
        print("No clients configured.")
        return
    
    print(f"\n📋 Configured Clients ({len(clients)}):")
    print("=" * 30)
    
    for client_id in clients:
        config = white_label_manager.get_client_config(client_id)
        if config:
            print(f"• {client_id}")
            print(f"  Company: {config.company_name}")
            print(f"  Brand: {config.brand_name}")
            print(f"  Services: {len(config.services)} configured")
            print()


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python white_label_setup.py create     - Interactive client setup")
        print("  python white_label_setup.py sample     - Create sample client")
        print("  python white_label_setup.py list       - List all clients")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        interactive_client_setup()
    elif command == "sample":
        create_sample_client()
    elif command == "list":
        list_clients()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()