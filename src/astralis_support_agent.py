from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

model = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    max_tokens=150,
)


def get_service_info(service_name: str) -> str:
    """Get detailed information about AstralisOne services."""
    service_name = service_name.lower()
    
    services = {
        "customer support": """24/7 AI Customer Support System - Our intelligent chatbot handles 70% of customer inquiries with seamless handoff to human agents. Features multi-channel support (website, social media, email, SMS), customer satisfaction tracking, and a knowledge base that learns automatically. Pricing starts at $79/month for up to 500 conversations.""",
        
        "marketing automation": """No-Code Marketing Automation Suite - Drag-and-drop campaign builder with AI content generation, automated social media posting, AI-driven email marketing with personalization, and lead scoring workflows. Built-in analytics and ROI tracking. Pricing starts at $49/month for up to 1,000 contacts.""",
        
        "operations automation": """Autonomous Business Operations Agent - AI agents for invoice processing, payment reminders, appointment scheduling, inventory management with predictive ordering, and HR tasks like timesheet processing. Integrates with existing business tools. Pricing starts at $99/month for up to 10 automations.""",
        
        "intelligence platform": """AI-Powered Customer Intelligence Platform - Real-time customer behavior analysis, automated segmentation, dynamic pricing recommendations, and 360-degree customer view dashboard. Help SMBs understand customers like enterprise companies. Custom pricing based on requirements.""",
        
        "smb ai services": """SMB-Specific AI Training & Implementation Service - Industry-specific AI readiness assessment, customized training programs, hands-on workshops, ongoing support, and ROI measurement guidance. Bridge the skills gap with practical training that ranks as top support need.""",
        
        "onboarding": """Our comprehensive 5-step client onboarding wizard guides you through Company setup, Contacts management, Engagement configuration, Access & Environments setup, and final Review & Submit. Designed for seamless project activation with full audit trails.""",
        
        "deployment": """AstralisOne runs on astralis.one and astralisone.com with React/Vite frontend, Node.js/Express backend, PostgreSQL database, and Caddy web server. We use modern tech stack with dark theme glassmorphism design and comprehensive security features."""
    }
    
    # Look for partial matches
    for key, value in services.items():
        if service_name in key or key in service_name:
            logger.info(f"🔍 Retrieved service info for: {key}")
            return value
    
    logger.info(f"❓ No specific service found for: {service_name}")
    return f"I don't have specific information about '{service_name}'. Let me tell you about our main services: Customer Support System, Marketing Automation Suite, Operations Automation, Intelligence Platform, and SMB AI Services. Which one interests you most?"


def get_pricing_info(service_type: str = "general") -> str:
    """Get pricing information for AstralisOne services."""
    service_type = service_type.lower()
    
    if "customer support" in service_type or "support" in service_type:
        return """Customer Support System Pricing:
- Starter: $79/month (up to 500 conversations, 2 agents, basic chatbot)
- Professional: $199/month (up to 2,000 conversations, 5 agents, advanced AI)
- Business: $399/month (up to 5,000 conversations, 15 agents, voice support)
- Enterprise: Custom pricing starting at $999/month (unlimited, white-label)"""
    
    elif "marketing" in service_type:
        return """Marketing Automation Pricing:
- Starter: $49/month (1,000 contacts, 5,000 emails, basic automation)
- Growth: $149/month (5,000 contacts, 25,000 emails, AI content generation)
- Professional: $399/month (15,000 contacts, 100,000 emails, unlimited automation)
- Enterprise: Custom pricing (unlimited contacts, white-label options)"""
    
    elif "operations" in service_type or "automation" in service_type:
        return """Operations Automation Pricing:
- Starter: $99/month (10 automations, 1,000 executions)
- Professional: $299/month (50 automations, 10,000 executions)
- Business: $699/month (200 automations, 50,000 executions)
- Enterprise: Custom pricing starting at $1,999/month (unlimited automations)"""
    
    else:
        return """AstralisOne offers flexible pricing across all our AI services:
- Customer Support: Starting at $79/month
- Marketing Automation: Starting at $49/month  
- Operations Automation: Starting at $99/month
- Intelligence Platform: Custom pricing
- Training & Implementation: Professional services rates
All plans include free trial periods and white-glove onboarding support."""


def get_company_info() -> str:
    """Get general information about AstralisOne."""
    logger.info("ℹ️ Providing company overview")
    return """AstralisOne is a leading provider of AI solutions specifically designed for Small to Medium Businesses (SMBs). We focus on making enterprise-grade AI accessible and affordable for businesses with 5-500 employees. Our comprehensive suite includes:

1. 24/7 AI Customer Support System
2. No-Code Marketing Automation Suite  
3. Autonomous Business Operations Agent
4. AI-Powered Customer Intelligence Platform
5. SMB-Specific AI Training & Implementation Services

We're headquartered with production systems running on astralis.one and astralisone.com. Our mission is to democratize AI for SMBs, helping them achieve 20-30% efficiency gains and $500-2,000 monthly savings through intelligent automation."""


tools = [get_service_info, get_pricing_info, get_company_info]

system_prompt = """You are Sofia, a knowledgeable and friendly sales and support representative for AstralisOne.com.

AstralisOne specializes in AI solutions for Small to Medium Businesses (SMBs). Your role is to help potential and existing customers understand our services, pricing, and how our AI solutions can benefit their business.

Key points about AstralisOne:
- We focus specifically on SMBs (5-500 employees) 
- Our solutions deliver 20-30% efficiency gains and $500-2,000 monthly savings
- We offer 5 main service categories: Customer Support, Marketing Automation, Operations Automation, Intelligence Platform, and Training Services
- All services include free trials and white-glove onboarding
- We have a modern tech stack with dark theme design and comprehensive security

When responding:
- Keep responses under 2-3 sentences and conversational
- Be direct and concise - this is voice conversation
- Use your tools to get specific information when needed
- Focus on key benefits, not detailed explanations
- Ask one simple question at a time
- Avoid lists, bullet points, or complex details in voice responses
- Speak naturally as this will be converted to audio

Always use your available tools when customers ask about specific services, pricing, or company information."""

memory = InMemorySaver()

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=system_prompt,
    checkpointer=memory,
)

agent_config = {"configurable": {"thread_id": "astralis_customer"}}