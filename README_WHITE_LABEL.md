# White-Label Voice Agent Service

Transform this voice agent into a white-label service for your clients with custom branding, services, and pricing.

## Quick Start

### 1. Create Sample Client
```bash
python src/white_label_setup.py sample
```

### 2. Run with Custom Client
```bash
python src/fastrtc_groq_voice_stream.py --client demo_client
```

### 3. Create Your First Client
```bash
python src/white_label_setup.py create
```

## Features

### 🏷️ Custom Branding
- **Company Name**: Full company name for formal contexts
- **Brand Name**: Customer-facing brand name
- **Agent Persona**: Customize agent personality and role

### 🎤 Voice Customization
- **Voice Selection**: Choose from available PlayAI voices
- **Response Length**: Control verbosity with token limits
- **Tone & Style**: Custom agent personas

### 🛠️ Service Configuration
- **Custom Services**: Define your client's service offerings
- **Pricing Tiers**: Flexible pricing structure
- **Custom Responses**: Pre-defined answers for common questions

### 📞 Contact Integration
- **Phone**: Automatically mention client's phone number
- **Email**: Include email in responses
- **Website**: Reference client's website

## Business Model Options

### Option 1: SaaS Platform
```bash
# Different clients via subdomains
client1.yourvoiceai.com
client2.yourvoiceai.com
client3.yourvoiceai.com
```

### Option 2: Header-Based Routing
```bash
# Single domain with client identification
curl -H "X-Client-ID: client1" https://yourapi.com/voice
```

### Option 3: Dedicated Instances
```bash
# Separate deployments per client
python src/fastrtc_groq_voice_stream.py --client client1 --port 8001
python src/fastrtc_groq_voice_stream.py --client client2 --port 8002
```

## Pricing Structure Ideas

### 🚀 Starter Package: $97/month
- Custom voice agent setup
- Up to 500 conversations/month
- Basic customization (name, services, contact info)
- Email support

### 💼 Professional Package: $297/month
- Up to 2,000 conversations/month
- Full branding customization
- Custom voice selection
- Priority support
- Analytics dashboard

### 🏢 Enterprise Package: $697/month
- Unlimited conversations
- White-label deployment
- Custom domain
- Dedicated support
- API access for integration

## Client Configuration

### Create New Client
```python
from src.white_label_config import ClientConfig, white_label_manager

config = ClientConfig(
    client_id="acme_corp",
    company_name="ACME Corporation",
    brand_name="ACME Solutions",
    voice_name="Sofia-PlayAI",
    agent_persona="professional business consultant",
    services=[
        "Business Consulting",
        "Process Optimization",
        "Digital Transformation"
    ],
    pricing_tiers={
        "Consultation": {
            "price": "$150/hour",
            "features": ["Initial assessment", "Strategy roadmap"]
        },
        "Implementation": {
            "price": "$2500/month",
            "features": ["Full implementation", "Ongoing support"]
        }
    },
    contact_info={
        "phone": "1-800-ACME-BIZ",
        "email": "contact@acmecorp.com",
        "website": "acmecorp.com"
    },
    max_tokens=120
)

white_label_manager.create_client(config)
```

### Usage Examples

#### Command Line
```bash
# Launch for specific client
python src/fastrtc_groq_voice_stream.py --client acme_corp

# With phone interface
python src/fastrtc_groq_voice_stream.py --client acme_corp --phone
```

#### Programmatic Usage
```python
from src.dynamic_agent_factory import create_custom_agent

# Get custom agent for client
agent, config = create_custom_agent("acme_corp")

# Use in your application
response = agent.invoke({
    "messages": [{"role": "user", "content": "Tell me about your services"}]
}, config=config)
```

## File Structure
```
clients/
├── demo_client.json      # Sample client configuration
├── acme_corp.json        # Your client configurations
└── ...

src/
├── white_label_config.py      # Core configuration management
├── dynamic_agent_factory.py   # Agent creation per client
├── white_label_setup.py       # Client setup CLI
└── fastrtc_groq_voice_stream.py  # Modified main application
```

## Integration Patterns

### Web Integration
```javascript
// Client-side JavaScript
const startVoiceCall = (clientId) => {
    const headers = clientId ? {'X-Client-ID': clientId} : {};
    // Initialize voice connection with headers
};
```

### API Gateway
```nginx
# Nginx configuration for subdomain routing
server {
    server_name ~^(?<client>.+)\.yourvoiceai\.com$;
    location / {
        proxy_set_header X-Client-ID $client;
        proxy_pass http://voice_agent_backend;
    }
}
```

### Docker Deployment
```yaml
# docker-compose.yml for multi-client deployment
services:
  voice-agent-client1:
    build: .
    command: python src/fastrtc_groq_voice_stream.py --client client1
    ports:
      - "8001:8000"
  
  voice-agent-client2:
    build: .
    command: python src/fastrtc_groq_voice_stream.py --client client2
    ports:
      - "8002:8000"
```

## Revenue Opportunities

### 💰 Monthly Recurring Revenue
- **Base Service**: $97-697/month per client
- **Setup Fees**: $500-2000 one-time setup
- **Custom Development**: $150-300/hour for special features

### 📈 Scaling Strategies
- **Volume Discounts**: Reduce per-conversation costs at scale
- **Add-on Services**: Analytics, integrations, custom voices
- **Referral Program**: Commission for client referrals

### 🎯 Target Markets
- **Professional Services**: Law firms, consultants, agencies
- **E-commerce**: Customer support, sales assistance
- **Healthcare**: Appointment scheduling, basic triage
- **Real Estate**: Lead qualification, property information

## Management Commands

```bash
# List all clients
python src/white_label_setup.py list

# Create new client interactively  
python src/white_label_setup.py create

# Create sample/demo client
python src/white_label_setup.py sample
```

## Next Steps

1. **Test the sample client**: Run with demo_client to see it in action
2. **Create your first real client**: Use the interactive setup
3. **Deploy multiple instances**: Scale to serve multiple clients
4. **Build a management dashboard**: Web interface for client management
5. **Add billing integration**: Stripe/PayPal for automated billing
6. **Create client portal**: Let clients manage their own settings

This white-label system transforms a single voice agent into a scalable SaaS business serving multiple clients with custom branding and configurations.