# Post-Investment Value-Add Agents

This service provides a suite of AI-powered agents that help portfolio companies with various post-investment needs:

1. **RecruitBot** - AI-powered recruiting assistant that helps portfolio companies hire top talent
2. **GrowthBot** - AI-powered growth strategist that generates A/B testing plans and growth strategies
3. **IntroBot** - AI-powered networking assistant that facilitates introductions to key contacts

## Architecture

Each agent follows an event-driven microservice architecture:

- Subscribes to a dedicated Kafka topic
- Processes requests asynchronously
- Responds via outbound email (stubbed in this implementation)
- Stores outputs in appropriate formats (e.g., JSON files for AB test plans)

![Agent Architecture](https://mermaid.ink/img/pako:eNp1ksFuwjAMhl_F8qlI0NJSCAzYhbHDLjvsMh1QlLpZRdJoiaudqu5hiTTxFrMjK2VdO4mGTrH9-bfj_05BVLVAEmQN1YLLIscchZbqIeeqJdUYUl-r0ug2Vw31wqiZVVRqSWZwl-1Qz5raSO7-7uE3MZ7fJ0xzQi5PbeBkGb4o5zDr9Sx8FKp6NMh1O44gK1DWyGUF9YxpBOzgKhDY-CXqvMSO9xK1sW72Hs_PydJPnKVP5oPLErdQotYUzGy-M8oaqGw7Ixx-YFa5t_WT1rwmaMY3V_fXdMJ9Wdv1vHjOWIZFWWWYFdofTOvA1-H0djRm49vR_f4X2q9aJemQJ7-PmKcHzp0Tn5_1LDQ5ZeEq6bITB6-r0SQoSxbzNXLhHH5EZdKRtTCn9Oyvh7tzcYAk3CsdCcZWQ84hUSgLrRXuRF0Ypw_WiVSxwDYoY3YHF3zX-tU?type=png)

## Value-Add Capabilities

### RecruitBot
- Generates customized job descriptions based on role requirements
- Creates recruiting strategies with timelines and platform recommendations
- Provides interview process guidance tailored to the company's needs

### GrowthBot
- Generates A/B testing plans with detailed variations and implementation details
- Creates growth strategies focused on specific business metrics
- Provides actionable timelines for growth initiatives
- Stores A/B test plans as JSON in the `/growth_plans` directory

### IntroBot
- Facilitates introductions to relevant industry contacts
- Generates personalized introduction emails
- Manages the introduction process with both parties

## Usage

### Prerequisites

- Python 3.11+
- aiokafka
- confluent-kafka
- pytest-asyncio

### Installation

```bash
# Install required packages
pip install aiokafka confluent-kafka pytest-asyncio
```

### Running the Agents

To run all agents:

```bash
cd services/value_add_agents
python main.py
```

To run specific agents:

```bash
python main.py --agents recruit_bot growth_bot
```

### Simulating Events

For testing without a Kafka environment:

```bash
cd services/value_add_agents
python simulate.py
```

To simulate a specific agent:

```bash
python simulate.py --agents growth_bot
```

### Testing

```bash
cd services/value_add_agents
pytest
```

## API

### Kafka Topics

- **new_hire_req** - Requests for recruiting assistance
- **growth_goal** - Requests for growth strategies and A/B testing plans
- **intro_req** - Requests for introductions to relevant contacts

### Message Formats

#### RecruitBot (new_hire_req)
```json
{
  "company_name": "TechStartup Inc.",
  "company_email": "hr@techstartup.example.com",
  "role": "Full Stack Engineer",
  "role_type": "engineering",
  "level": "Senior",
  "requirements": {
    "experience": "5+",
    "technologies": "Python, React, TypeScript, PostgreSQL",
    "additional_skills": "Docker, Kubernetes, AWS"
  },
  "company_description": "A fast-growing startup building AI-powered analytics tools.",
  "location": "San Francisco, CA",
  "remote": true
}
```

#### GrowthBot (growth_goal)
```json
{
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "DataInsights AI",
  "company_email": "growth@datainsightsai.example.com",
  "business_type": "saas",
  "growth_goal": "increase MRR by 30%",
  "current_metrics": {
    "mrr": 100000,
    "customers": 50,
    "avg_deal_size": 2000,
    "cac": 1500,
    "churn_rate": 2
  },
  "target_metrics": {
    "mrr": 130000,
    "customers": 65,
    "churn_rate": 1.5
  },
  "timeframe": "3 months",
  "focus_area": "acquisition"
}
```

#### IntroBot (intro_req)
```json
{
  "company_name": "HealthTech Solutions",
  "company_email": "founders@healthtech.example.com",
  "company_description": "is developing AI-powered diagnostic tools for remote healthcare providers.",
  "industry": "healthcare",
  "introduction_type": "investor",
  "founder_name": "Dr. Sarah Chen",
  "founder_title": "CEO",
  "founder_background": "Medical Director at Regional Hospital",
  "specific_request": "Looking for investors with digital health experience for our Series A round",
  "funding_round": "Series A",
  "pain_point_area": "remote diagnostics"
}
```

## Output Examples

### AB Test Plan (from GrowthBot)

```json
{
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "DataInsights AI",
  "test_id": "789e0123-e45b-67d8-a901-234567890000",
  "test_name": "Product-Led Growth Call-to-action Optimization",
  "created_at": "2025-04-20T12:00:00.000Z",
  "business_type": "saas",
  "focus_area": "acquisition",
  "growth_goal": "increase MRR by 30%",
  "hypothesis": "By optimizing our call-to-action buttons, we can increase Conversion Rate by 15.8%",
  "primary_metric": "Conversion Rate",
  "secondary_metrics": ["Click-Through Rate", "Sign-Up Rate"],
  "expected_improvement": "15.8%",
  "duration": "14 days",
  "traffic_allocation": {
    "control": 50,
    "variations": 50
  },
  "variations": [
    {
      "id": "A",
      "name": "Control",
      "description": "Current implementation without changes"
    },
    {
      "id": "B",
      "name": "Variation B",
      "description": "Test call-to-action buttons with optimized design"
    },
    {
      "id": "C",
      "name": "Variation C",
      "description": "Test call-to-action buttons with simplified messaging"
    }
  ],
  "implementation_details": {
    "test_pages": ["Homepage", "Product Page", "Checkout Flow"],
    "user_segments": ["All Users", "New Visitors", "Returning Visitors"],
    "technical_requirements": [
      "Implement tracking for all variations",
      "Ensure proper A/B test bucketing",
      "Set up analytics dashboard for monitoring"
    ]
  },
  "success_criteria": {
    "statistical_significance": "95% confidence level",
    "minimum_sample_size": "Calculated based on expected improvement",
    "decision_framework": "Winner determined by primary metric improvement with statistical significance"
  }
}
```