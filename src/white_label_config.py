import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class ClientConfig:
    """Configuration for a white-label client."""
    client_id: str
    company_name: str
    brand_name: str
    voice_name: str = "Celeste-PlayAI"
    agent_persona: str = "helpful assistant"
    services: List[str] = None
    pricing_tiers: Dict[str, Dict] = None
    contact_info: Dict[str, str] = None
    custom_responses: Dict[str, str] = None
    knowledge_base: Dict[str, str] = None  # {"type": "file|url|text", "source": "path/url/content"}
    max_tokens: int = 150
    
    def __post_init__(self):
        if self.services is None:
            self.services = []
        if self.pricing_tiers is None:
            self.pricing_tiers = {}
        if self.contact_info is None:
            self.contact_info = {}
        if self.custom_responses is None:
            self.custom_responses = {}
        if self.knowledge_base is None:
            self.knowledge_base = {}


class WhiteLabelManager:
    """Manages white-label client configurations."""
    
    def __init__(self, config_dir: str = "clients"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._clients: Dict[str, ClientConfig] = {}
        self.load_all_clients()
    
    def load_all_clients(self):
        """Load all client configurations from disk."""
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    client_config = ClientConfig(**data)
                    self._clients[client_config.client_id] = client_config
            except Exception as e:
                print(f"Error loading client config {config_file}: {e}")
    
    def get_client_config(self, client_id: str) -> Optional[ClientConfig]:
        """Get configuration for a specific client."""
        return self._clients.get(client_id)
    
    def create_client(self, client_config: ClientConfig) -> bool:
        """Create a new white-label client configuration."""
        try:
            # Save to disk
            config_file = self.config_dir / f"{client_config.client_id}.json"
            with open(config_file, 'w') as f:
                config_dict = {
                    'client_id': client_config.client_id,
                    'company_name': client_config.company_name,
                    'brand_name': client_config.brand_name,
                    'voice_name': client_config.voice_name,
                    'agent_persona': client_config.agent_persona,
                    'services': client_config.services,
                    'pricing_tiers': client_config.pricing_tiers,
                    'contact_info': client_config.contact_info,
                    'custom_responses': client_config.custom_responses,
                    'knowledge_base': client_config.knowledge_base,
                    'max_tokens': client_config.max_tokens,
                }
                json.dump(config_dict, f, indent=2)
            
            # Add to memory
            self._clients[client_config.client_id] = client_config
            return True
        except Exception as e:
            print(f"Error creating client config: {e}")
            return False
    
    def list_clients(self) -> List[str]:
        """List all client IDs."""
        return list(self._clients.keys())
    
    def update_client(self, client_id: str, updates: Dict) -> bool:
        """Update a client's configuration."""
        if client_id not in self._clients:
            return False
        
        try:
            # Update in memory
            config = self._clients[client_id]
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            # Save to disk
            config_file = self.config_dir / f"{client_id}.json"
            with open(config_file, 'w') as f:
                config_dict = {
                    'client_id': config.client_id,
                    'company_name': config.company_name,
                    'brand_name': config.brand_name,
                    'voice_name': config.voice_name,
                    'agent_persona': config.agent_persona,
                    'services': config.services,
                    'pricing_tiers': config.pricing_tiers,
                    'contact_info': config.contact_info,
                    'custom_responses': config.custom_responses,
                    'knowledge_base': config.knowledge_base,
                    'max_tokens': config.max_tokens,
                }
                json.dump(config_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating client config: {e}")
            return False


# Global instance
white_label_manager = WhiteLabelManager()


def get_client_from_request(request_headers: Dict[str, str]) -> Optional[str]:
    """Extract client ID from request headers or domain."""
    # Check for custom header
    client_id = request_headers.get('X-Client-ID')
    if client_id:
        return client_id
    
    # Check for subdomain pattern (e.g., client1.yourdomain.com)
    host = request_headers.get('Host', '')
    if '.' in host:
        subdomain = host.split('.')[0]
        if white_label_manager.get_client_config(subdomain):
            return subdomain
    
    return None