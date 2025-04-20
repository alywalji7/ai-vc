#!/usr/bin/env python3
"""
Test script for the Investment Committee Simulator API.

This script sends test requests to the IC Simulator API to verify
that both the rule-based filtering and LLM-based analysis are working properly.
"""

import json
import requests
import sys


def test_ic_simulation_with_id():
    """Test the IC simulation endpoint with just a company ID."""
    print("\n===== Testing IC Simulation with Company ID =====")
    
    url = "http://localhost:8060/api/ic_sim"
    params = {"company_id": "test123"}
    
    try:
        response = requests.post(url, params=params, timeout=120)  # 2-minute timeout for LLM processing
        
        if response.status_code == 200:
            print(f"✅ Success (Status {response.status_code})")
            result = response.json()
            print("\nSimulation Result:")
            print(f"Company ID: {result.get('company_id')}")
            print(f"Company Name: {result.get('company_name')}")
            print(f"Passed Rule Filter: {result.get('passed_rule_filter')}")
            
            if result.get('passed_rule_filter'):
                print("\nRule Filter Info:")
                for reason in result.get('rule_filter_info', []):
                    print(f"- {reason}")
                
                print("\nLLM Analysis Result:")
                analysis = result.get('result', {})
                print(f"Decision: {analysis.get('decision')}")
                print(f"Confidence: {analysis.get('confidence')}")
                print(f"ROI Expectation: {analysis.get('roi_expectation')}x")
                print(f"Risk Assessment: {analysis.get('risk_assessment')}")
                print(f"\nRationale: {analysis.get('rationale')}")
                
                print("\nReasoning Chain Summary:")
                for step in analysis.get('reasoning_chain', []):
                    print(f"- {step.get('thought')}")
            else:
                print("\nRule Filter Reasons for Rejection:")
                for reason in result.get('reasons', []):
                    print(f"- {reason}")
        else:
            print(f"❌ Error (Status {response.status_code}): {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Failed: {str(e)}")


def test_ic_simulation_with_data():
    """Test the IC simulation endpoint with custom company data."""
    print("\n===== Testing IC Simulation with Custom Company Data =====")
    
    url = "http://localhost:8060/api/ic_sim"
    
    # Example of a company that should pass the rule filter
    company_data = {
        "company_data": {
            "id": "custom001",
            "name": "Quantum Finance AI",
            "sector": "fintech",
            "round": "series_a",
            "region": "north_america",
            "raise_amount": 8000000,
            "valuation": 40000000,
            "revenue": 1500000,
            "growth_rate": 0.9,
            "burn_rate": 200000,
            "runway": 10,
            "team_size": 18,
            "founding_year": 2023,
            "founder_background": "Former VP of Engineering at JPMorgan, PhD in ML",
            "market_size": 8000000000,
            "competitors": ["Square", "Stripe", "Affirm"],
            "description": "Quantum Finance AI develops AI-powered financial forecasting tools for SMBs, helping them predict cash flow and optimize expenses.",
            "business_model": "SaaS subscription with tiered pricing based on company size.",
            "key_metrics": {
                "arr": 1500000,
                "cac": 12000,
                "ltv": 90000,
                "monthly_active_users": 120,
                "nps": 72
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(company_data), headers=headers, timeout=120)
        
        if response.status_code == 200:
            print(f"✅ Success (Status {response.status_code})")
            result = response.json()
            print("\nSimulation Result:")
            print(f"Company ID: {result.get('company_id')}")
            print(f"Company Name: {result.get('company_name')}")
            print(f"Passed Rule Filter: {result.get('passed_rule_filter')}")
            
            if result.get('passed_rule_filter'):
                print("\nRule Filter Info:")
                for reason in result.get('rule_filter_info', []):
                    print(f"- {reason}")
                
                print("\nLLM Analysis Result:")
                analysis = result.get('result', {})
                print(f"Decision: {analysis.get('decision')}")
                print(f"Confidence: {analysis.get('confidence')}")
                print(f"ROI Expectation: {analysis.get('roi_expectation')}x")
                print(f"Risk Assessment: {analysis.get('risk_assessment')}")
                print(f"\nRationale: {analysis.get('rationale')}")
                
                print("\nReasoning Chain Summary:")
                for step in analysis.get('reasoning_chain', []):
                    print(f"- {step.get('thought')}")
            else:
                print("\nRule Filter Reasons for Rejection:")
                for reason in result.get('reasons', []):
                    print(f"- {reason}")
        else:
            print(f"❌ Error (Status {response.status_code}): {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Failed: {str(e)}")


def test_rule_filter_rejection():
    """Test a case that should fail the rule filter (wrong sector and round size)."""
    print("\n===== Testing Rule Filter Rejection =====")
    
    url = "http://localhost:8060/api/ic_sim"
    
    # Example of a company that should fail the rule filter
    company_data = {
        "company_data": {
            "id": "reject001",
            "name": "FashionTech Marketplace",
            "sector": "consumer",  # Not in ALLOWED_SECTORS
            "round": "series_a",
            "region": "north_america",
            "raise_amount": 25000000,  # Exceeds MAX_RAISE_AMOUNT for series_a
            "valuation": 80000000,
            "revenue": 1200000,
            "growth_rate": 0.6,
            "burn_rate": 350000,
            "runway": 8,
            "team_size": 30,
            "founding_year": 2021,
            "founder_background": "Former fashion industry executive",
            "market_size": 5000000000,
            "competitors": ["ASOS", "Zalando", "The RealReal"],
            "description": "FashionTech Marketplace is a B2C platform for sustainable fashion.",
            "business_model": "Marketplace with commission on sales.",
            "key_metrics": {
                "arr": 1200000,
                "cac": 45000,
                "ltv": 55000,
                "monthly_active_users": 50000,
                "nps": 60
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(company_data), headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Success (Status {response.status_code})")
            result = response.json()
            print("\nSimulation Result:")
            print(f"Company ID: {result.get('company_id')}")
            print(f"Company Name: {result.get('company_name')}")
            print(f"Passed Rule Filter: {result.get('passed_rule_filter')}")
            
            if not result.get('passed_rule_filter'):
                print("\nRule Filter Reasons for Rejection (Expected):")
                for reason in result.get('reasons', []):
                    print(f"- {reason}")
            else:
                print("❌ Error: Company passed rule filter when it should have been rejected")
        else:
            print(f"❌ Error (Status {response.status_code}): {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Failed: {str(e)}")


if __name__ == "__main__":
    print("Starting Investment Committee Simulator API Tests")
    print("================================================")
    
    if len(sys.argv) > 1:
        # Run specific test if argument provided
        if sys.argv[1] == "id":
            test_ic_simulation_with_id()
        elif sys.argv[1] == "data":
            test_ic_simulation_with_data()
        elif sys.argv[1] == "reject":
            test_rule_filter_rejection()
        else:
            print(f"Unknown test: {sys.argv[1]}")
    else:
        # Run all tests
        test_ic_simulation_with_id()
        test_ic_simulation_with_data()
        test_rule_filter_rejection()
    
    print("\nTests completed.")