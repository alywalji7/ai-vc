"""
IntroBot implementation.
"""

import json
import os
from typing import Dict, Any, List, Tuple
import logging
import asyncio
import datetime
import random

from ..base_agent import BaseAgent
from ..config import EMAIL_SIGNATURE

# Contact profiles by industry and role
CONTACT_PROFILES = {
    "technology": {
        "investor": [
            {"name": "Sarah Chen", "title": "Partner at Cloud Ventures", "expertise": "Enterprise SaaS, AI/ML, Infrastructure"},
            {"name": "Michael Rodriguez", "title": "General Partner at TechFund Capital", "expertise": "B2B Software, Marketplaces, Developer Tools"},
            {"name": "Jennifer Wu", "title": "Managing Director at Horizon Ventures", "expertise": "Consumer Tech, FinTech, Digital Health"}
        ],
        "customer": [
            {"name": "David Park", "title": "CTO at EnterpriseCore", "expertise": "Cloud Infrastructure, Security, DevOps"},
            {"name": "Aisha Johnson", "title": "VP of Engineering at DataSphere", "expertise": "Data Analytics, ETL, Machine Learning"},
            {"name": "Robert Chen", "title": "CIO at GlobalTech Solutions", "expertise": "Digital Transformation, ERP Integration, IT Strategy"}
        ],
        "advisor": [
            {"name": "Emily Zhang", "title": "Former CTO at TechGiant", "expertise": "Scaling Engineering Teams, Tech Architecture, AI Implementation"},
            {"name": "Carlos Mendez", "title": "Growth Advisor & Former VP at SaaSLeader", "expertise": "PLG, GTM Strategy, Product Marketing"},
            {"name": "Dr. Priya Sharma", "title": "Technical Fellow & AI Specialist", "expertise": "ML/AI Products, Research Commercialization, Data Ethics"}
        ]
    },
    "healthcare": {
        "investor": [
            {"name": "Dr. Thomas Lee", "title": "Partner at BioVentures", "expertise": "Digital Health, Medical Devices, Diagnostics"},
            {"name": "Lisa Montgomery", "title": "Principal at HealthTech Partners", "expertise": "Healthcare SaaS, Telemedicine, Care Coordination"},
            {"name": "Richard Wong", "title": "Managing Director at Life Sciences Fund", "expertise": "Biotech, Pharmaceuticals, Precision Medicine"}
        ],
        "customer": [
            {"name": "Dr. Maria Santos", "title": "Chief Medical Officer at Regional Health System", "expertise": "Clinical Workflows, Quality Metrics, Patient Care"},
            {"name": "James Washington", "title": "VP of Innovation at NationalCare", "expertise": "Digital Transformation, Remote Monitoring, Healthcare Analytics"},
            {"name": "Sarah Peterson", "title": "Director of Technology at MedicalGroup", "expertise": "EHR Systems, Health IT, Compliance"}
        ],
        "advisor": [
            {"name": "Dr. Jonathan Kim", "title": "Former CEO of HealthTech Innovator", "expertise": "Regulatory Strategy, Clinical Validation, Market Access"},
            {"name": "Elizabeth Chen", "title": "Healthcare Policy Expert", "expertise": "Reimbursement Models, Healthcare Economics, Policy Compliance"},
            {"name": "Dr. Michael Thompson", "title": "Clinical Advisor & Practicing Physician", "expertise": "Clinical Workflows, Patient Outcomes, Medical Education"}
        ]
    },
    "finance": {
        "investor": [
            {"name": "Alexander Greene", "title": "Partner at FinTech Ventures", "expertise": "Payments, Banking Tech, Embedded Finance"},
            {"name": "Victoria Nguyen", "title": "Principal at Capital Innovations", "expertise": "WealthTech, InsurTech, Blockchain"},
            {"name": "Robert Blackwell", "title": "Managing Director at Financial Horizons", "expertise": "RegTech, Capital Markets Tech, B2B FinTech"}
        ],
        "customer": [
            {"name": "John Martinez", "title": "CTO at MidSize Bank", "expertise": "Core Banking Systems, Digital Transformation, Security"},
            {"name": "Natalie Wong", "title": "Head of Innovation at Insurance Leader", "expertise": "Claims Automation, Underwriting Tech, Customer Engagement"},
            {"name": "Derek Johnson", "title": "CFO at Enterprise Financial", "expertise": "Financial Operations, Reporting Systems, Compliance"}
        ],
        "advisor": [
            {"name": "Amanda Taylor", "title": "Former COO of Digital Bank", "expertise": "Banking Operations, Customer Experience, Regulatory Strategy"},
            {"name": "Brian Liu", "title": "FinTech Strategist & Former Product Head", "expertise": "Product Strategy, Financial Inclusion, UX Design"},
            {"name": "Sarah Washington", "title": "Financial Compliance Expert", "expertise": "AML/KYC, Regulatory Reporting, Risk Management"}
        ]
    },
    "retail": {
        "investor": [
            {"name": "Rebecca Martinez", "title": "Partner at Consumer Ventures", "expertise": "D2C Brands, Marketplaces, Retail Tech"},
            {"name": "Jason Kim", "title": "Principal at Retail Innovation Fund", "expertise": "Omnichannel Retail, Supply Chain Tech, In-Store Tech"},
            {"name": "Laura Thompson", "title": "Managing Director at Brand Capital", "expertise": "Consumer Products, E-commerce, Subscription Models"}
        ],
        "customer": [
            {"name": "Michael Chen", "title": "CIO at Retail Chain", "expertise": "POS Systems, Inventory Management, Customer Analytics"},
            {"name": "Sophia Rodriguez", "title": "VP of Digital at Fashion Brand", "expertise": "E-commerce Platforms, Mobile Shopping, Personalization"},
            {"name": "David Washington", "title": "Supply Chain Director at Consumer Goods Co", "expertise": "Logistics Technology, Forecasting, Warehouse Management"}
        ],
        "advisor": [
            {"name": "Jennifer Park", "title": "Former CEO of Retail Tech Leader", "expertise": "Retail Transformation, Omnichannel Strategy, Customer Experience"},
            {"name": "Chris Thompson", "title": "D2C Marketing Specialist", "expertise": "Customer Acquisition, Retention Strategies, Brand Building"},
            {"name": "Aisha Williams", "title": "Retail Operations Expert", "expertise": "Store Operations, Staff Productivity, Loss Prevention"}
        ]
    }
}

# Introduction email templates
INTRO_EMAIL_TEMPLATES = {
    "customer": """
Dear {contact_name},

I hope this email finds you well. I'm writing to introduce you to {company_name}, a promising company in our portfolio that I believe could add significant value to {contact_company}.

{company_name} has developed {company_description} Their solution has already helped companies like yours {value_proposition}

{company_founder}, the {founder_title} of {company_name}, would welcome the opportunity to give you a brief demonstration of their platform and discuss how it might address some of the challenges you're facing in {pain_point_area}.

Would you be open to a 30-minute introductory call in the next couple of weeks? I'm happy to join to facilitate the conversation.

Best regards,
""",
    "investor": """
Dear {contact_name},

I hope you're doing well. I wanted to introduce you to an exciting company in our portfolio, {company_name}, which aligns well with your investment focus on {expertise}.

{company_name} {company_description} The company has shown impressive {traction_metric} over the past {time_period}, and they're now preparing for their {funding_round} round.

Their founder, {company_founder} (former {founder_background}), has built a talented team and has a compelling vision for the market. Given your experience with {related_company}, I thought you might find their approach particularly interesting.

Would you be interested in meeting {company_founder} to learn more about what they're building? I'm happy to make a direct introduction if you're interested.

Best regards,
""",
    "advisor": """
Dear {contact_name},

I hope this message finds you well. I'm reaching out because I believe your expertise in {expertise} could be invaluable to one of our portfolio companies.

{company_name} is {company_description} They've made significant progress, including {recent_achievement}, but are now facing challenges related to {challenge_area} as they scale.

The founder, {company_founder}, is specifically looking for guidance on {specific_need} and your background at {contact_company} seems like an ideal fit for these challenges.

Would you be open to an initial conversation with {company_founder} to explore if there might be a mutual fit for an advisory relationship? I'm happy to join the initial call to make the connection.

Best regards,
"""
}

# Email subject lines
EMAIL_SUBJECTS = {
    "customer": [
        "Introduction: {company_name} - Solution for {pain_point_area}",
        "Connecting you with {company_name}: Innovative solution for {contact_company}",
        "{contact_name}, meet {company_founder} from {company_name}"
    ],
    "investor": [
        "Introduction to {company_name}: Aligned with your {expertise} thesis",
        "Portfolio company introduction: {company_name} ({funding_round} opportunity)",
        "Connecting you with {company_founder}: {company_name} raising {funding_round}"
    ],
    "advisor": [
        "Your expertise in {expertise} could help {company_name}",
        "Seeking your guidance: {company_name} scaling {challenge_area}",
        "Advisory opportunity: {company_name} looking for {expertise} expert"
    ]
}

class IntroBot(BaseAgent):
    """AI-powered networking assistant for portfolio companies."""
    
    async def process_message(self, message: Dict[str, Any]):
        """
        Process an introduction request message.
        
        Args:
            message: The introduction request message with details
        """
        self.logger.info(f"Processing introduction request: {json.dumps(message, indent=2)}")
        
        try:
            # Extract introduction request details
            company_name = message.get("company_name", "")
            company_email = message.get("company_email", "")
            company_description = message.get("company_description", "")
            industry = message.get("industry", "technology").lower()
            introduction_type = message.get("introduction_type", "customer").lower()
            founder_name = message.get("founder_name", "")
            founder_title = message.get("founder_title", "CEO")
            founder_background = message.get("founder_background", "")
            specific_request = message.get("specific_request", "")
            
            # Additional context fields
            recent_achievement = message.get("recent_achievement", "")
            challenge_area = message.get("challenge_area", "")
            specific_need = message.get("specific_need", "")
            funding_round = message.get("funding_round", "Series A")
            traction_metric = message.get("traction_metric", "")
            time_period = message.get("time_period", "6 months")
            value_proposition = message.get("value_proposition", "")
            pain_point_area = message.get("pain_point_area", "")
            
            # Select matching contacts based on industry and introduction type
            contacts = await self._get_matching_contacts(industry, introduction_type)
            
            # Prepare introduction for each contact
            for contact in contacts[:2]:  # Limit to top 2 matching contacts
                # Generate personalized introduction email
                intro_email = await self._generate_introduction_email(
                    contact=contact,
                    introduction_type=introduction_type,
                    company_name=company_name,
                    company_description=company_description,
                    founder_name=founder_name,
                    founder_title=founder_title,
                    founder_background=founder_background,
                    specific_request=specific_request,
                    recent_achievement=recent_achievement,
                    challenge_area=challenge_area,
                    specific_need=specific_need,
                    funding_round=funding_round,
                    traction_metric=traction_metric,
                    time_period=time_period,
                    value_proposition=value_proposition,
                    pain_point_area=pain_point_area
                )
                
                # Select a subject line
                subject_templates = EMAIL_SUBJECTS.get(introduction_type, EMAIL_SUBJECTS["customer"])
                subject_template = random.choice(subject_templates)
                
                subject = subject_template.format(
                    company_name=company_name,
                    company_founder=founder_name,
                    contact_name=contact["name"],
                    contact_company=contact["title"].split(" at ")[-1] if " at " in contact["title"] else "",
                    expertise=contact["expertise"].split(", ")[0],
                    pain_point_area=pain_point_area or challenge_area or "your industry",
                    funding_round=funding_round
                )
                
                # Send email to company with the introduction draft
                company_subject = f"Introduction Draft: {contact['name']} ({contact['title']})"
                
                company_body = f"""Dear {company_name} Team,

Based on your request for introductions to {introduction_type}s in the {industry} industry, I've identified {contact['name']} ({contact['title']}) as a potential match.

Here's a draft introduction email that I can send on your behalf:

---
Subject: {subject}

{intro_email}
---

Please review this draft and let me know if you'd like me to:
1. Send this introduction as-is
2. Make specific modifications to the email
3. Look for different contacts who might be a better fit

Once you approve, I'll send the introduction and facilitate the connection.

{EMAIL_SIGNATURE}
"""
                
                await self.send_email(
                    to=company_email,
                    subject=company_subject,
                    body=company_body
                )
                
                self.logger.info(f"Introduction draft for {contact['name']} sent to {company_email}")
            
        except Exception as e:
            self.logger.error(f"Error processing introduction request: {e}")
            raise
    
    async def _get_matching_contacts(self, industry: str, introduction_type: str) -> List[Dict[str, str]]:
        """
        Get matching contacts based on industry and introduction type.
        
        Args:
            industry: The industry to match
            introduction_type: The type of introduction (customer, investor, advisor)
            
        Returns:
            List of matching contacts
        """
        # Get contacts for the industry
        industry_contacts = CONTACT_PROFILES.get(industry, CONTACT_PROFILES["technology"])
        
        # Get contacts for the introduction type
        type_contacts = industry_contacts.get(introduction_type, [])
        
        # If no contacts found for the specific type, get random contacts from any type
        if not type_contacts:
            all_contacts = []
            for contacts in industry_contacts.values():
                all_contacts.extend(contacts)
            return random.sample(all_contacts, min(3, len(all_contacts)))
        
        # Return shuffled contacts to randomize results
        random.shuffle(type_contacts)
        return type_contacts
    
    async def _generate_introduction_email(self, **kwargs) -> str:
        """
        Generate an introduction email based on the provided parameters.
        
        Args:
            **kwargs: Introduction parameters
            
        Returns:
            Introduction email text
        """
        contact = kwargs.get("contact", {})
        introduction_type = kwargs.get("introduction_type", "customer")
        
        # Get template for introduction type
        template = INTRO_EMAIL_TEMPLATES.get(introduction_type, INTRO_EMAIL_TEMPLATES["customer"])
        
        # Extract contact details
        contact_name = contact.get("name", "")
        contact_title = contact.get("title", "")
        contact_company = contact_title.split(" at ")[-1] if " at " in contact_title else ""
        contact_expertise = contact.get("expertise", "")
        
        # Format template with details
        email = template.format(
            contact_name=contact_name,
            contact_company=contact_company,
            expertise=contact_expertise.split(", ")[0],  # Use the first expertise area
            company_name=kwargs.get("company_name", ""),
            company_description=kwargs.get("company_description", ""),
            company_founder=kwargs.get("founder_name", ""),
            founder_title=kwargs.get("founder_title", "CEO"),
            founder_background=kwargs.get("founder_background", ""),
            recent_achievement=kwargs.get("recent_achievement", ""),
            challenge_area=kwargs.get("challenge_area", ""),
            specific_need=kwargs.get("specific_need", ""),
            funding_round=kwargs.get("funding_round", "Series A"),
            traction_metric=kwargs.get("traction_metric", ""),
            time_period=kwargs.get("time_period", "6 months"),
            value_proposition=kwargs.get("value_proposition", ""),
            pain_point_area=kwargs.get("pain_point_area", ""),
            related_company=random.choice(contact_expertise.split(", "))
        )
        
        return email + EMAIL_SIGNATURE