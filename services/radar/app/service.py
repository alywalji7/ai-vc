"""
Service layer for the Deal-Flow Radar - handles model loading and prediction.
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sqlalchemy.orm import Session

from .database import Company, InvestmentOpportunity
from .models import ShortlistItem, FeatureVector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'catboost_radar_model.cbm')
MODEL_METADATA_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')

# Global variables
model = None
model_metadata = None


def load_model() -> CatBoostClassifier:
    """
    Load the CatBoost model from file.
    
    Returns:
        CatBoostClassifier: Loaded model
    """
    global model, model_metadata
    
    try:
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model file not found at {MODEL_PATH}")
            # Create a simple model for testing
            model = CatBoostClassifier(iterations=10)
            return model
            
        # Load the trained model
        model = CatBoostClassifier()
        model.load_model(MODEL_PATH)
        logger.info(f"Model loaded from {MODEL_PATH}")
        
        # Load model metadata
        if os.path.exists(MODEL_METADATA_PATH):
            with open(MODEL_METADATA_PATH, 'r') as f:
                model_metadata = json.load(f)
            logger.info(f"Model metadata loaded from {MODEL_METADATA_PATH}")
        else:
            logger.warning(f"Model metadata file not found at {MODEL_METADATA_PATH}")
            model_metadata = {
                'features': [
                    'company_age', 'github_stars', 'commit_velocity', 'investor_count',
                    'founder_exit_count', 'social_traction', 'funding_amount',
                    'stars_to_age_ratio', 'funding_per_investor', 'social_engagement_ratio'
                ],
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'model_version': '0.1.0',
            }
        
        return model
    
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def create_feature_vector(company: Dict[str, Any]) -> FeatureVector:
    """
    Create a feature vector from a company record.
    
    Args:
        company: Company data from database
        
    Returns:
        FeatureVector: Feature vector ready for prediction
    """
    # Convert founding_date to age in years
    founding_date = company.get('founding_date') or datetime.now()
    if isinstance(founding_date, str):
        founding_date = datetime.fromisoformat(founding_date.replace('Z', '+00:00'))
    
    company_age = (datetime.now() - founding_date).days / 365.25
    
    # Create derived features
    stars_to_age_ratio = company.get('github_stars', 0) / max(company_age, 0.1)  # Avoid division by zero
    
    investor_count = max(company.get('investor_count', 0), 1)  # Avoid division by zero
    funding_per_investor = company.get('funding_amount', 0) / investor_count
    
    social_engagement_ratio = company.get('social_traction', 0) / max(company_age, 0.1)
    
    return FeatureVector(
        company_age=company_age,
        github_stars=company.get('github_stars', 0),
        commit_velocity=company.get('commit_velocity', 0),
        investor_count=company.get('investor_count', 0),
        founder_exit_count=company.get('founder_exit_count', 0),
        social_traction=company.get('social_traction', 0),
        funding_amount=company.get('funding_amount', 0),
        stars_to_age_ratio=stars_to_age_ratio,
        funding_per_investor=funding_per_investor,
        social_engagement_ratio=social_engagement_ratio
    )


def predict_company_score(feature_vector: FeatureVector) -> float:
    """
    Predict the investment opportunity score for a company using the trained model.
    
    Args:
        feature_vector: Feature vector for the company
        
    Returns:
        float: Predicted score (0-1)
    """
    global model
    
    # Ensure model is loaded
    if model is None:
        load_model()
    
    # Convert feature vector to DataFrame
    features_dict = feature_vector.dict()
    df = pd.DataFrame([features_dict])
    
    # Ensure the columns are in the correct order as expected by the model
    required_features = model_metadata.get('features', list(features_dict.keys()))
    df = df[required_features]
    
    # Make prediction
    try:
        # Get probability of positive class
        probability = model.predict_proba(df)[0, 1]
        return float(probability)
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return 0.0
        
        
def enqueue_dataroom_task(company_id: str, score: float) -> bool:
    """
    Enqueue a task to build a data room for a company that has been green-lit by the radar.
    A company is considered green-lit if its score is above 0.7.
    
    Args:
        company_id: ID of the company
        score: Radar score (0-1)
        
    Returns:
        bool: True if task was enqueued, False otherwise
    """
    # Check if score is high enough to trigger data room build
    if score < 0.7:
        logger.info(f"Company {company_id} score {score:.2f} is below threshold, not enqueueing data room task")
        return False
    
    try:
        # In a production environment, we would use a proper task queue like Celery
        # For now, we'll use a direct HTTP request to the scheduler service
        scheduler_url = os.environ.get("SCHEDULER_URL", "http://localhost:8085")
        task_endpoint = f"{scheduler_url}/tasks/run"
        
        logger.info(f"Enqueueing data room build for company {company_id} with score {score:.2f}")
        
        # Prepare the task data
        task_data = {
            "task_name": "build_dataroom",
            "args": [company_id],
            "kwargs": {"score": score}
        }
        
        # Send the request to the scheduler
        import httpx
        with httpx.Client(timeout=10.0) as client:
            response = client.post(task_endpoint, json=task_data)
            
            if response.status_code == 200:
                logger.info(f"Successfully enqueued data room task for company {company_id}")
                return True
            else:
                logger.error(f"Failed to enqueue task: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error enqueueing data room task for company {company_id}: {str(e)}")
        return False


def get_company_data_from_db(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get company data from database.
    
    Args:
        db: Database session
        limit: Maximum number of companies to retrieve
        
    Returns:
        List of company records
    """
    companies = db.query(Company).limit(limit).all()
    return [
        {
            'id': company.id,
            'name': company.name,
            'founding_date': company.founding_date,
            'github_stars': company.github_stars,
            'commit_velocity': company.commit_velocity,
            'investor_count': company.investor_count,
            'founder_exit_count': company.founder_exit_count,
            'social_traction': company.social_traction,
            'funding_amount': company.funding_amount
        }
        for company in companies
    ]


def get_daily_shortlist(db: Session, limit: int = 10) -> List[ShortlistItem]:
    """
    Generate a daily shortlist of investment opportunities.
    
    Args:
        db: Database session
        limit: Maximum number of companies to include in the shortlist
        
    Returns:
        List of shortlist items
    """
    # Ensure model is loaded
    if model is None:
        load_model()
    
    # Get company data from database
    companies = get_company_data_from_db(db, limit=100)  # Get more than needed for ranking
    
    results = []
    for company in companies:
        try:
            # Create feature vector for this company
            feature_vector = create_feature_vector(company)
            
            # Predict score
            score = predict_company_score(feature_vector)
            
            # Add to results
            results.append({
                'company_id': company['id'],
                'name': company['name'],
                'score': score
            })
            
            # Store prediction in database
            investment_opportunity = InvestmentOpportunity(
                company_id=company['id'],
                score=score,
                features_used=json.dumps(feature_vector.dict())
            )
            db.add(investment_opportunity)
            
        except Exception as e:
            logger.error(f"Error processing company {company.get('id')}: {str(e)}")
    
    # Commit changes to database
    db.commit()
    
    # Sort by score and take top N
    results.sort(key=lambda x: x['score'], reverse=True)
    shortlist = results[:limit]
    
    # Convert to ShortlistItem objects
    return [
        ShortlistItem(
            company_id=item['company_id'],
            name=item['name'],
            clos=item['score']
        )
        for item in shortlist
    ]


def handle_mock_data(limit: int = 10) -> List[ShortlistItem]:
    """
    Generate a shortlist using mock data when database is not available.
    Used primarily for development and testing.
    
    Args:
        limit: Maximum number of items in the shortlist
        
    Returns:
        List of shortlist items
    """
    # Check if model is loaded
    if model is None:
        load_model()
    
    # Try to load mock data
    mock_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mock_company_data.csv')
    
    try:
        mock_data = pd.read_csv(mock_data_path)
        logger.info(f"Loaded mock data from {mock_data_path}")
        
        # Convert data to format needed for predictions
        mock_data['founding_date'] = pd.to_datetime(mock_data['founding_date'])
        
        # Calculate features
        today = datetime.now()
        mock_data['company_age'] = (today - mock_data['founding_date']).dt.days / 365.25
        mock_data['stars_to_age_ratio'] = mock_data['github_stars'] / mock_data['company_age']
        mock_data['funding_per_investor'] = mock_data['funding_amount'] / mock_data['investor_count'].replace(0, 1)
        mock_data['social_engagement_ratio'] = mock_data['social_traction'] / mock_data['company_age']
        
        # Extract features used by the model
        required_features = model_metadata.get('features', [
            'company_age', 'github_stars', 'commit_velocity', 'investor_count',
            'founder_exit_count', 'social_traction', 'funding_amount',
            'stars_to_age_ratio', 'funding_per_investor', 'social_engagement_ratio'
        ])
        
        X = mock_data[required_features]
        
        # Generate predictions
        mock_data['score'] = model.predict_proba(X)[:, 1]
        
        # Sort by score and take top N
        shortlist_data = mock_data.sort_values('score', ascending=False).head(limit)
        
        # Create shortlist items
        shortlist = [
            ShortlistItem(
                company_id=row['company_id'],
                name=row['name'],
                clos=float(row['score'])
            )
            for _, row in shortlist_data.iterrows()
        ]
        
        return shortlist
        
    except Exception as e:
        logger.error(f"Error generating mock shortlist: {str(e)}")
        
        # Return hardcoded data as a fallback
        return [
            ShortlistItem(company_id="c003", name="CloudNative", clos=0.92),
            ShortlistItem(company_id="c023", name="AIChips", clos=0.89),
            ShortlistItem(company_id="c013", name="FinTechSolutions", clos=0.87),
            ShortlistItem(company_id="c027", name="QuantumComputing", clos=0.85),
            ShortlistItem(company_id="c044", name="CyberSecurity", clos=0.83),
        ][:limit]