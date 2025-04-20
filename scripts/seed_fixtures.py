#!/usr/bin/env python3
"""
Seed fixture data for development and testing.

This script inserts two companies (acme-inc, globex-llc) with dummy KPIs, 
decks, and one open deal each. The script is idempotent and can be run
multiple times without creating duplicate data.
"""

import os
import sys
import json
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database connection settings from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Company fixture data
COMPANIES = [
    {
        "id": "acme-inc",
        "name": "ACME Inc.",
        "description": "ACME Inc. is a leading provider of innovative software solutions.",
        "website": "https://acme-inc.example.com",
        "founded_date": "2020-01-15",
        "hq_location": "San Francisco, CA",
        "sector": "Enterprise Software",
        "stage": "Series A"
    },
    {
        "id": "globex-llc",
        "name": "Globex LLC",
        "description": "Globex LLC develops cutting-edge AI technology for healthcare.",
        "website": "https://globex.example.com",
        "founded_date": "2021-03-22",
        "hq_location": "Boston, MA",
        "sector": "Healthcare Technology",
        "stage": "Seed"
    }
]

# KPI data
KPI_DATA = {
    "acme-inc": [
        {"metric": "MRR", "value": 125000, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "MRR", "value": 150000, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "Customers", "value": 45, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "Customers", "value": 52, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "CAC", "value": 5200, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "CAC", "value": 4800, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "LTV", "value": 28000, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "LTV", "value": 30500, "date": datetime.now().strftime("%Y-%m-%d")},
    ],
    "globex-llc": [
        {"metric": "MRR", "value": 75000, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "MRR", "value": 85000, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "Customers", "value": 28, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "Customers", "value": 32, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "CAC", "value": 6500, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "CAC", "value": 6200, "date": datetime.now().strftime("%Y-%m-%d")},
        {"metric": "LTV", "value": 22000, "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")},
        {"metric": "LTV", "value": 24500, "date": datetime.now().strftime("%Y-%m-%d")},
    ]
}

# Deal data
DEALS = [
    {
        "id": "deal-acme-001",
        "company_id": "acme-inc",
        "status": "open",
        "round_size": 5000000,
        "pre_money_valuation": 25000000,
        "target_close_date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "deal_lead": "alice",
        "investment_committee_decision": "approve",
        "investment_committee_notes": "Strong growth, favorable unit economics, and experienced team.",
        "term_sheet": {
            "document_type": "series_seed_safe",
            "safe_details": {
                "investment_amount": 500000,
                "valuation_cap": 30000000,
                "discount_rate": 20,
                "company_name": "ACME Inc.",
                "investor_name": "AI.VC Partners",
                "effective_date": datetime.now().strftime("%Y-%m-%d"),
                "company_signatory_name": "John Smith",
                "company_signatory_title": "CEO",
                "investor_signatory_name": "Alice Johnson",
                "investor_signatory_title": "Partner"
            }
        }
    },
    {
        "id": "deal-globex-001",
        "company_id": "globex-llc", 
        "status": "open",
        "round_size": 2500000,
        "pre_money_valuation": 12000000,
        "target_close_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "deal_lead": "bob",
        "investment_committee_decision": "approve",
        "investment_committee_notes": "Innovative AI technology with strong IP and promising early traction.",
        "term_sheet": {
            "document_type": "series_seed_safe",
            "safe_details": {
                "investment_amount": 350000,
                "valuation_cap": 15000000,
                "discount_rate": 15,
                "company_name": "Globex LLC",
                "investor_name": "AI.VC Partners",
                "effective_date": datetime.now().strftime("%Y-%m-%d"),
                "company_signatory_name": "Susan Lee",
                "company_signatory_title": "CEO",
                "investor_signatory_name": "Bob Wilson",
                "investor_signatory_title": "Principal"
            }
        }
    }
]

def connect_to_db():
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to the database: {e}")
        sys.exit(1)


def check_tables_exist(conn):
    """Check if the required tables exist in the database."""
    required_tables = ["companies", "kpis", "deals", "term_sheets"]
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            logger.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
            
        return True
    except psycopg2.Error as e:
        logger.error(f"Error checking tables: {e}")
        return False
    finally:
        cursor.close()


def check_company_exists(conn, company_id):
    """Check if a company with the given ID already exists."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM companies WHERE id = %s", (company_id,))
        return cursor.fetchone() is not None
    except psycopg2.Error as e:
        logger.error(f"Error checking if company exists: {e}")
        return False
    finally:
        cursor.close()


def check_deal_exists(conn, deal_id):
    """Check if a deal with the given ID already exists."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM deals WHERE id = %s", (deal_id,))
        return cursor.fetchone() is not None
    except psycopg2.Error as e:
        logger.error(f"Error checking if deal exists: {e}")
        return False
    finally:
        cursor.close()


def insert_companies(conn):
    """Insert company data into the database."""
    cursor = conn.cursor()
    companies_inserted = 0
    
    try:
        for company in COMPANIES:
            if not check_company_exists(conn, company["id"]):
                cursor.execute("""
                    INSERT INTO companies (
                        id, name, description, website, founded_date, 
                        hq_location, sector, stage, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    company["id"], company["name"], company["description"],
                    company["website"], company["founded_date"],
                    company["hq_location"], company["sector"], company["stage"],
                    datetime.now(), datetime.now()
                ))
                companies_inserted += 1
                logger.info(f"Inserted company: {company['name']}")
            else:
                logger.info(f"Company already exists: {company['name']}")
        
        return companies_inserted
    except psycopg2.Error as e:
        logger.error(f"Error inserting companies: {e}")
        return 0
    finally:
        cursor.close()


def insert_kpis(conn):
    """Insert KPI data into the database."""
    cursor = conn.cursor()
    kpis_inserted = 0
    
    try:
        for company_id, kpis in KPI_DATA.items():
            for kpi in kpis:
                cursor.execute("""
                    INSERT INTO kpis (
                        company_id, metric, value, date, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (company_id, metric, date) 
                    DO UPDATE SET value = EXCLUDED.value, updated_at = %s
                """, (
                    company_id, kpi["metric"], kpi["value"], kpi["date"],
                    datetime.now(), datetime.now(), datetime.now()
                ))
                kpis_inserted += 1
        
        logger.info(f"Inserted or updated {kpis_inserted} KPI records")
        return kpis_inserted
    except psycopg2.Error as e:
        logger.error(f"Error inserting KPIs: {e}")
        return 0
    finally:
        cursor.close()


def insert_deals(conn):
    """Insert deal data into the database."""
    cursor = conn.cursor()
    deals_inserted = 0
    
    try:
        for deal in DEALS:
            if not check_deal_exists(conn, deal["id"]):
                # Insert the deal
                cursor.execute("""
                    INSERT INTO deals (
                        id, company_id, status, round_size, pre_money_valuation,
                        target_close_date, created_date, deal_lead,
                        investment_committee_decision, investment_committee_notes,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    deal["id"], deal["company_id"], deal["status"],
                    deal["round_size"], deal["pre_money_valuation"],
                    deal["target_close_date"], deal["created_date"], deal["deal_lead"],
                    deal["investment_committee_decision"], deal["investment_committee_notes"],
                    datetime.now(), datetime.now()
                ))
                
                # Insert the term sheet
                term_sheet = deal["term_sheet"]
                cursor.execute("""
                    INSERT INTO term_sheets (
                        deal_id, document_type, details, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    deal["id"], term_sheet["document_type"], 
                    json.dumps(term_sheet["safe_details"]),
                    datetime.now(), datetime.now()
                ))
                
                deals_inserted += 1
                logger.info(f"Inserted deal: {deal['id']}")
            else:
                logger.info(f"Deal already exists: {deal['id']}")
        
        return deals_inserted
    except psycopg2.Error as e:
        logger.error(f"Error inserting deals: {e}")
        return 0
    finally:
        cursor.close()


def main():
    """Main function to seed fixture data."""
    logger.info("Starting seed_fixtures.py")
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    
    conn = connect_to_db()
    if not conn:
        sys.exit(1)
    
    try:
        if not check_tables_exist(conn):
            logger.error("Required tables do not exist. Please run migrations first.")
            sys.exit(1)
        
        # Insert fixture data
        companies_count = insert_companies(conn)
        if companies_count > 0:
            kpis_count = insert_kpis(conn)
            deals_count = insert_deals(conn)
            
            logger.info(f"Successfully inserted {companies_count} companies, {kpis_count} KPIs, and {deals_count} deals")
        else:
            logger.info("No new companies inserted, skipping KPIs and deals")
        
        logger.info("Seed completed successfully")
    except Exception as e:
        logger.error(f"Error seeding fixture data: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()