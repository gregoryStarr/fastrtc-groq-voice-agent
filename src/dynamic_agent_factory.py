from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

from white_label_config import ClientConfig, white_label_manager


def create_service_info_tool(client_config: ClientConfig):
    """Create a service info tool customized for the client."""
    
    def get_service_info(service_name: str) -> str:
        """Get information about client's services."""
        service_name = service_name.lower()
        
        # Check for custom responses first
        for key, value in client_config.custom_responses.items():
            if service_name in key.lower() or key.lower() in service_name:
                return value
        
        # Default response pattern
        if service_name in " ".join(client_config.services).lower():
            return f"{client_config.brand_name} offers {service_name}. Contact us for more details."
        
        return f"I don't have specific information about '{service_name}'. {client_config.brand_name} specializes in {', '.join(client_config.services)}. How can I help you with these services?"
    
    return get_service_info


def create_pricing_info_tool(client_config: ClientConfig):
    """Create a pricing info tool customized for the client."""
    
    def get_pricing_info(service_type: str = "general") -> str:
        """Get pricing information for client's services."""
        service_type = service_type.lower()
        
        # Check for specific pricing tiers
        for tier_name, tier_info in client_config.pricing_tiers.items():
            if service_type in tier_name.lower():
                price = tier_info.get('price', 'Contact for pricing')
                features = tier_info.get('features', [])
                feature_text = f" - includes {', '.join(features)}" if features else ""
                return f"{tier_name}: {price}{feature_text}"
        
        # General pricing response
        if client_config.pricing_tiers:
            tiers = list(client_config.pricing_tiers.keys())
            return f"{client_config.brand_name} offers flexible pricing with plans: {', '.join(tiers)}. Contact us for detailed pricing."
        
        return f"Contact {client_config.brand_name} for pricing information on our {', '.join(client_config.services)} services."
    
    return get_pricing_info


def create_company_info_tool(client_config: ClientConfig):
    """Create a company info tool customized for the client."""
    
    def get_company_info() -> str:
        """Get information about the client's company."""
        contact_text = ""
        if client_config.contact_info:
            contact_parts = []
            if 'phone' in client_config.contact_info:
                contact_parts.append(f"Call us at {client_config.contact_info['phone']}")
            if 'email' in client_config.contact_info:
                contact_parts.append(f"email {client_config.contact_info['email']}")
            if 'website' in client_config.contact_info:
                contact_parts.append(f"visit {client_config.contact_info['website']}")
            
            if contact_parts:
                contact_text = f" {' or '.join(contact_parts)}."
        
        services_text = f"We specialize in {', '.join(client_config.services)}." if client_config.services else ""
        
        return f"{client_config.company_name} is your trusted partner for business solutions. {services_text} {contact_text}".strip()
    
    return get_company_info


def create_custom_agent(client_id: str) -> tuple[Any, Dict[str, Any]]:
    """Create a customized agent for a specific client."""
    client_config = white_label_manager.get_client_config(client_id)
    
    if not client_config:
        logger.error(f"No configuration found for client: {client_id}")
        # Return default agent
        from astralis_support_agent import agent, agent_config
        return agent, agent_config
    
    logger.info(f"Creating custom agent for {client_config.brand_name}")
    
    # Create customized model
    model = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        max_tokens=client_config.max_tokens,
    )
    
    # Create customized tools
    tools = [
        create_service_info_tool(client_config),
        create_pricing_info_tool(client_config),
        create_company_info_tool(client_config),
    ]
    
    # Create customized system prompt
    system_prompt = f"""You are {client_config.agent_persona} for {client_config.brand_name}.

{client_config.company_name} provides professional services to help businesses grow and succeed.

Our main services include: {', '.join(client_config.services) if client_config.services else 'various business solutions'}.

When responding:
- Keep responses under 2-3 sentences and conversational
- Be direct and concise - this is voice conversation  
- Use your tools to get specific information when needed
- Focus on key benefits, not detailed explanations
- Ask one simple question at a time
- Avoid lists, bullet points, or complex details in voice responses
- Speak naturally as this will be converted to audio
- Always represent {client_config.brand_name} professionally

Always use your available tools when customers ask about specific services, pricing, or company information."""
    
    # Create agent with custom configuration
    memory = InMemorySaver()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
        checkpointer=memory,
    )
    
    agent_config = {"configurable": {"thread_id": f"{client_id}_customer"}}
    
    return agent, agent_config


def get_voice_settings(client_id: str) -> Dict[str, str]:
    """Get TTS voice settings for a client."""
    client_config = white_label_manager.get_client_config(client_id)
    
    if not client_config:
        return {
            "model": "playai-tts",
            "voice": "Celeste-PlayAI",
            "response_format": "wav"
        }
    
    return {
        "model": "playai-tts",
        "voice": client_config.voice_name,
        "response_format": "wav"
    }