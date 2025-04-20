"""
RecruitBot implementation.
"""

import json
from typing import Dict, Any, List
import logging
import asyncio
import datetime
import random

from ..base_agent import BaseAgent
from ..config import EMAIL_SIGNATURE

# JD templates for different roles
JD_TEMPLATES = {
    "engineering": """
Job Title: {level} Software Engineer

About {company_name}:
{company_description}

Job Description:
We are seeking a talented {level} Software Engineer to join our growing team. The ideal candidate will have {experience} years of experience in {technologies}.

Responsibilities:
- Design, develop, and maintain high-quality software
- Collaborate with cross-functional teams to define, design, and ship new features
- Identify and resolve performance bottlenecks
- Participate in code reviews and mentor junior engineers
- Stay up-to-date with emerging trends and technologies

Requirements:
- {experience}+ years of professional software development experience
- Strong proficiency in {technologies}
- Experience with {additional_skills}
- Bachelor's degree in Computer Science or related field (or equivalent experience)
- Excellent problem-solving abilities and attention to detail
- Strong communication and collaboration skills

Location: {location} {remote_option}

Benefits:
- Competitive salary and equity package
- Health, dental, and vision insurance
- Flexible work hours
- Professional development budget
- Team events and activities
""",
    "product": """
Job Title: {level} Product Manager

About {company_name}:
{company_description}

Job Description:
We are looking for a {level} Product Manager to drive the development of innovative products that address our customers' needs. The ideal candidate will have {experience} years of experience in product management.

Responsibilities:
- Own the product roadmap and prioritize features based on business value
- Work closely with engineering, design, and other stakeholders
- Conduct user research and gather customer feedback
- Define success metrics and track product performance
- Present product strategies to executive leadership

Requirements:
- {experience}+ years of product management experience
- Experience in {industry} industry
- Strong analytical and problem-solving skills
- Excellent communication and presentation abilities
- Technical background or experience working with technical teams
- Bachelor's degree in a related field (or equivalent experience)

Location: {location} {remote_option}

Benefits:
- Competitive salary and equity package
- Health, dental, and vision insurance
- Flexible work hours
- Professional development budget
- Team events and activities
""",
    "sales": """
Job Title: {level} Account Executive

About {company_name}:
{company_description}

Job Description:
We are seeking an experienced {level} Account Executive to drive new business and expand our customer base. The ideal candidate will have {experience} years of experience in {industry} sales.

Responsibilities:
- Prospect, qualify, and develop sales opportunities
- Build and maintain relationships with key decision-makers
- Demonstrate product value through presentations and demos
- Negotiate contracts and close deals
- Meet and exceed quarterly sales targets
- Collaborate with marketing, product, and customer success teams

Requirements:
- {experience}+ years of B2B sales experience, preferably in {industry}
- Track record of consistently meeting or exceeding sales quotas
- Experience with {crm_tool} or similar CRM systems
- Strong presentation and negotiation skills
- Bachelor's degree (or equivalent experience)

Location: {location} {remote_option}

Benefits:
- Competitive base salary + commission structure
- Health, dental, and vision insurance
- Flexible work hours
- Professional development budget
- Team events and activities
"""
}

# List of popular recruiting platforms by role
RECRUITING_PLATFORMS = {
    "engineering": ["AngelList", "GitHub Jobs", "Stack Overflow Jobs", "Hired", "Triplebyte"],
    "product": ["LinkedIn", "Product Hunt", "AngelList", "Mind the Product", "Product School"],
    "sales": ["LinkedIn", "SalesJobs.com", "ZipRecruiter", "Indeed", "Bravado"]
}

# Top recruiting agencies by role
RECRUITING_AGENCIES = {
    "engineering": ["Robert Half Technology", "TekSystems", "Hays", "CyberCoders", "Randstad"],
    "product": ["Product Recruitment", "Bamboo Crowd", "VentureLoop", "Creative Circle", "Cogswell"],
    "sales": ["Sales Talent Agency", "Lucas Group", "Betts Recruiting", "Victory Lap", "SalesForce Search"]
}

class RecruitBot(BaseAgent):
    """AI-powered recruiting assistant for portfolio companies."""
    
    async def process_message(self, message: Dict[str, Any]):
        """
        Process a new hire request message.
        
        Args:
            message: The new hire request message with job details
        """
        self.logger.info(f"Processing new hire request: {json.dumps(message, indent=2)}")
        
        try:
            # Extract job details
            company_name = message.get("company_name", "")
            company_email = message.get("company_email", "")
            role = message.get("role", "")
            role_type = message.get("role_type", "engineering").lower()
            level = message.get("level", "Senior")
            requirements = message.get("requirements", {})
            company_description = message.get("company_description", "")
            location = message.get("location", "San Francisco, CA")
            remote = message.get("remote", False)
            
            # Generate job description
            jd = await self._generate_job_description(
                company_name=company_name,
                company_description=company_description,
                role_type=role_type,
                level=level,
                experience=requirements.get("experience", "3-5"),
                technologies=requirements.get("technologies", ""),
                additional_skills=requirements.get("additional_skills", ""),
                industry=requirements.get("industry", "technology"),
                crm_tool=requirements.get("crm_tool", "Salesforce"),
                location=location,
                remote=remote
            )
            
            # Generate recruitment strategy
            strategy = await self._generate_recruitment_strategy(role_type)
            
            # Send email to company
            subject = f"Recruiting Strategy for {level} {role} Role"
            
            body = f"""Dear {company_name} Team,

Thank you for submitting your hiring request for a {level} {role} position. I've analyzed your requirements and prepared a comprehensive recruitment strategy to help you find the ideal candidate.

## Job Description
{jd}

## Recruitment Strategy
{strategy}

I'm available to discuss this strategy in more detail or make any adjustments to better align with your specific needs.

{EMAIL_SIGNATURE}
"""
            
            await self.send_email(
                to=company_email,
                subject=subject,
                body=body
            )
            
            self.logger.info(f"Recruitment strategy sent to {company_email}")
            
        except Exception as e:
            self.logger.error(f"Error processing new hire request: {e}")
            raise
    
    async def _generate_job_description(self, **kwargs) -> str:
        """
        Generate a job description based on the provided parameters.
        
        Args:
            **kwargs: Job description parameters
            
        Returns:
            Formatted job description
        """
        role_type = kwargs.get("role_type", "engineering")
        remote = kwargs.get("remote", False)
        
        # Get the appropriate template for the role type
        template = JD_TEMPLATES.get(role_type, JD_TEMPLATES["engineering"])
        
        # Format the remote option
        remote_option = "(Remote available)" if remote else ""
        
        # Format the template with the provided parameters
        return template.format(
            **kwargs,
            remote_option=remote_option
        )
    
    async def _generate_recruitment_strategy(self, role_type: str) -> str:
        """
        Generate a recruitment strategy for the given role type.
        
        Args:
            role_type: Type of role (engineering, product, sales, etc.)
            
        Returns:
            Recruitment strategy text
        """
        # Get relevant platforms and agencies for the role type
        platforms = RECRUITING_PLATFORMS.get(role_type, RECRUITING_PLATFORMS["engineering"])
        agencies = RECRUITING_AGENCIES.get(role_type, RECRUITING_AGENCIES["engineering"])
        
        # Select a subset of platforms and agencies
        selected_platforms = random.sample(platforms, min(3, len(platforms)))
        selected_agencies = random.sample(agencies, min(2, len(agencies)))
        
        # Generate timeline
        current_date = datetime.datetime.now()
        posting_date = (current_date + datetime.timedelta(days=2)).strftime("%B %d, %Y")
        first_interviews = (current_date + datetime.timedelta(days=14)).strftime("%B %d, %Y")
        target_hiring = (current_date + datetime.timedelta(days=30)).strftime("%B %d, %Y")
        
        strategy = f"""
### Recommended Job Posting Platforms
{', '.join(selected_platforms)}

### Recommended Recruiting Agencies
{', '.join(selected_agencies)}

### Suggested Timeline
- Job Posting: {posting_date}
- First Round Interviews: {first_interviews}
- Target Hiring Date: {target_hiring}

### Sourcing Strategy
1. Post the job description on the recommended platforms
2. Reach out to passive candidates on LinkedIn who match your requirements
3. Leverage your existing employee network for referrals
4. Engage with the recommended recruiting agencies if needed

### Interview Process Recommendations
1. Initial screening call with HR/Recruiter (30 minutes)
2. Technical/Role-specific assessment or take-home assignment
3. Panel interview with team members and potential collaborators
4. Final interview with leadership/hiring manager
5. Reference checks and offer extension

I can help coordinate and streamline this process, including setting up an applicant tracking system and creating email templates for candidate communication.
"""
        
        return strategy