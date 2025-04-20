# Term Sheet Generator & Negotiator Bot

This service provides:
1. Generation of NVCA model documents using docxtpl templates
2. WebSocket API for real-time term sheet negotiations using GPT-4o
3. Lane guards with Slack escalation for extreme counter-offers

## Features

### Document Generation
- Fills NVCA model documents using docxtpl
- Currently supports Series Seed SAFE template
- Customizable fields via API

### Negotiation Chat
- Real-time negotiation via WebSocket API
- GPT-4o powered negotiation assistant
- Tree-of-thought reasoning for term sheet positions

### Lane Guards & Escalation
- Analyzes counter-offers for deviations from original terms
- Escalates extreme counter-offers (>2σ deviation) to Slack
- Fallback to log files when Slack is unavailable

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /api/generate` - Generate term sheet document
- `GET /api/download/{document_path}` - Download generated document
- `POST /api/negotiate/session` - Create negotiation session
- `GET /api/negotiate/session/{session_id}` - Get session details
- `WebSocket /api/negotiate/chat/{session_id}` - Real-time negotiation chat

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for GPT-4o
- `SLACK_BOT_TOKEN` - Slack bot token for notifications (optional)
- `SLACK_CHANNEL_ID` - Slack channel for escalations (optional)
- `PORT` - Port to run the service on (default: 8070)
- `HOST` - Host to bind to (default: 0.0.0.0)

## Usage Example

```python
# Generate a SAFE document
response = requests.post(
    "http://localhost:8070/api/generate",
    json={
        "document_type": "series_seed_safe",
        "safe_details": {
            "investment_amount": 500000,
            "valuation_cap": 8000000,
            "discount_rate": 20,
            "company_name": "TechStartup Inc.",
            "investor_name": "Venture Capital Partners LLC",
            "effective_date": "2025-04-20",
            "company_signatory_name": "John Smith",
            "company_signatory_title": "CEO",
            "investor_signatory_name": "Jane Doe",
            "investor_signatory_title": "Managing Partner"
        }
    }
)
document_path = response.json()["document_path"]

# Download the document
with open("safe_document.docx", "wb") as f:
    f.write(requests.get(f"http://localhost:8070/api/download/{document_path}").content)
```

## Negotiation Chat Example

```javascript
// Create a negotiation session
const session = await fetch('http://localhost:8070/api/negotiate/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document_type: 'series_seed_safe',
    company_id: 'company123',
    investor_id: 'investor456',
    original_terms: {
      investment_amount: 500000,
      valuation_cap: 8000000,
      discount_rate: 20
    }
  })
}).then(res => res.json());

// Connect to the negotiation WebSocket
const socket = new WebSocket(`ws://localhost:8070/api/negotiate/chat/${session.session_id}`);

// Send message
socket.send('I would like to propose a $16M valuation cap instead of $8M.');

// Receive response
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'escalation') {
    console.log('Negotiation escalated to human review!');
  } else if (data.type === 'message') {
    console.log(`Bot: ${data.message.content}`);
  }
};
```