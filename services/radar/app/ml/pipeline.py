"""
Training and evaluation pipeline for the Deal-Flow Radar model.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

import numpy as np
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
from sqlalchemy.orm import Session

from ..database import (
    Company, InvestmentOpportunity, CompanyOutcome, ModelVersion, LPFeedback, FeedbackType,
    get_db, SessionLocal
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MLflow configuration
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db")
EXPERIMENT_NAME = "radar-model"

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'catboost_radar_model.cbm')
MODEL_METADATA_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')


def setup_mlflow():
    """
    Set up MLflow tracking.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Check if experiment exists, create if not
    try:
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            mlflow.create_experiment(EXPERIMENT_NAME)
        logger.info(f"MLflow experiment '{EXPERIMENT_NAME}' is set up")
    except Exception as e:
        logger.error(f"Error setting up MLflow experiment: {str(e)}")
        raise


def nightly_outcome_update() -> int:
    """
    Update company outcome labels nightly from external sources.
    This function would typically pull data from an API or data warehouse
    with the latest company outcomes information.
    
    Returns:
        int: Number of records updated
    """
    with SessionLocal() as db:
        # In a real environment, this would pull from real data sources
        # For this example, we'll simulate adding random outcomes
        # to companies that don't have them yet
        
        # Get companies without outcome records
        companies_query = db.query(Company).outerjoin(
            CompanyOutcome, Company.id == CompanyOutcome.company_id
        ).filter(CompanyOutcome.id == None)
        
        companies = companies_query.all()
        logger.info(f"Found {len(companies)} companies without outcome records")
        
        if not companies:
            logger.info("No new companies to update outcomes for")
            return 0
        
        # In a real scenario, we would fetch actual outcomes from a data source
        # For this example, we'll use random outcomes
        updates = 0
        for company in companies:
            # Simulate exit or up-round with some probability
            # In a real scenario, this would be based on actual data
            has_exit = np.random.random() < 0.05  # 5% chance of exit
            has_up_round = np.random.random() < 0.20  # 20% chance of up-round
            
            # Create outcome record
            outcome = CompanyOutcome(
                company_id=company.id,
                exit_event=has_exit,
                up_round=has_up_round
            )
            
            if has_exit:
                # Simulate exit details
                outcome.exit_date = datetime.now()
                outcome.exit_amount = company.funding_amount * np.random.uniform(5, 15)
            
            if has_up_round:
                # Simulate up-round details
                outcome.up_round_date = datetime.now()
                outcome.previous_valuation = company.funding_amount * 4  # Assumed 4x funding = valuation
                outcome.up_round_valuation = outcome.previous_valuation * np.random.uniform(1.3, 2.5)
            
            db.add(outcome)
            updates += 1
        
        # Commit changes
        db.commit()
        logger.info(f"Updated outcomes for {updates} companies")
        return updates


def get_lp_feedback(db: Session) -> Tuple[List[str], List[int]]:
    """
    Get LP feedback data for active learning.
    
    Args:
        db: Database session
        
    Returns:
        Tuple containing:
        - List of company IDs with feedback
        - List of feedback labels (1 for UP, 0 for DOWN)
    """
    # Query feedback data that hasn't been used in training yet
    feedback_query = db.query(LPFeedback).filter(
        LPFeedback.used_in_training == False
    )
    
    feedback_entries = feedback_query.all()
    logger.info(f"Found {len(feedback_entries)} unused LP feedback entries")
    
    company_ids = []
    feedback_labels = []
    
    for entry in feedback_entries:
        company_ids.append(entry.company_id)
        # Convert feedback type to binary label (UP=1, DOWN=0)
        label = 1 if entry.feedback_type == FeedbackType.UP else 0
        feedback_labels.append(label)
        
        # Mark as used in training
        entry.used_in_training = True
    
    # Commit updates to mark feedback as used
    if feedback_entries:
        db.commit()
        logger.info(f"Marked {len(feedback_entries)} feedback entries as used in training")
    
    return company_ids, feedback_labels


def prepare_training_data(db: Session) -> Tuple[pd.DataFrame, np.ndarray, Dict[str, Any]]:
    """
    Prepare training data from database with active learning from LP feedback.
    
    Args:
        db: Database session
        
    Returns:
        Tuple containing:
        - DataFrame with feature data
        - Array with target labels (1 for successful outcomes, 0 otherwise)
        - Dictionary with active learning metadata
    """
    # Get all companies with outcome data
    query = db.query(
        Company, 
        CompanyOutcome
    ).join(
        CompanyOutcome, 
        Company.id == CompanyOutcome.company_id
    )
    
    results = query.all()
    logger.info(f"Found {len(results)} companies with outcome data for training")
    
    if len(results) < 10:
        logger.warning("Insufficient data for training, need at least 10 samples")
        raise ValueError("Insufficient training data")
    
    # Prepare feature data
    data = []
    company_id_map = {}  # Map company_id to index in data
    
    for i, (company, outcome) in enumerate(results):
        # Calculate derived features
        founding_date = company.founding_date or datetime.now()
        company_age = (datetime.now() - founding_date).days / 365.25
        
        stars_to_age_ratio = company.github_stars / max(company_age, 0.1)
        
        investor_count = max(company.investor_count, 1)
        funding_per_investor = company.funding_amount / investor_count
        
        social_engagement_ratio = company.social_traction / max(company_age, 0.1)
        
        # Target variable: success is defined as either exit or up-round
        success = 1 if (outcome.exit_event or outcome.up_round) else 0
        
        data.append({
            'company_id': company.id,
            'company_age': company_age,
            'github_stars': company.github_stars,
            'commit_velocity': company.commit_velocity,
            'investor_count': company.investor_count,
            'founder_exit_count': company.founder_exit_count,
            'social_traction': company.social_traction,
            'funding_amount': company.funding_amount,
            'stars_to_age_ratio': stars_to_age_ratio,
            'funding_per_investor': funding_per_investor,
            'social_engagement_ratio': social_engagement_ratio,
            'success': success
        })
        
        # Store index mapping
        company_id_map[company.id] = i
    
    # Get LP feedback for active learning
    feedback_company_ids, feedback_labels = get_lp_feedback(db)
    
    # Prepare sample weights (default weight = 1.0)
    sample_weights = np.ones(len(data))
    
    # Apply LP feedback to sample weights
    feedback_weight = 10.0  # Feedback samples are 10x more important
    feedback_count = 0
    
    for company_id, label in zip(feedback_company_ids, feedback_labels):
        if company_id in company_id_map:
            idx = company_id_map[company_id]
            current_label = data[idx]['success']
            
            # If feedback contradicts outcome data, apply stronger weight
            if label != current_label:
                sample_weights[idx] = feedback_weight * 2
                # Optionally override the label (uncomment to enable)
                # data[idx]['success'] = label
            else:
                # Feedback confirms outcome data, apply standard feedback weight
                sample_weights[idx] = feedback_weight
                
            feedback_count += 1
    
    # Calculate feedback weight percentage
    total_weight = sample_weights.sum()
    feedback_weight_percent = 0.0
    if total_weight > 0 and feedback_count > 0:
        feedback_weight_percent = (sample_weights.sum() - len(data)) / total_weight * 100
    
    # Log active learning stats
    logger.info(f"Using {feedback_count} LP feedback signals in active learning")
    logger.info(f"Feedback weight percentage: {feedback_weight_percent:.2f}%")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Extract features and target
    X = df.drop(['company_id', 'success'], axis=1)
    y = df['success'].values
    
    # Metadata for tracking
    active_learning_meta = {
        "feedback_count": feedback_count,
        "total_samples": len(data),
        "feedback_weight_percent": feedback_weight_percent
    }
    
    return X, y, sample_weights, active_learning_meta


def train_model(
    X: pd.DataFrame, 
    y: np.ndarray,
    sample_weights: Optional[np.ndarray] = None,
    active_learning_meta: Optional[Dict[str, Any]] = None,
    model_params: Optional[Dict[str, Any]] = None
) -> Tuple[CatBoostClassifier, Dict[str, Any]]:
    """
    Train CatBoost model with cross-validation and active learning.
    
    Args:
        X: Feature DataFrame
        y: Target array
        sample_weights: Optional sample weights for training
        active_learning_meta: Optional metadata about active learning
        model_params: Optional model parameters
        
    Returns:
        Tuple containing:
        - Trained CatBoost model
        - Dictionary of metrics
    """
    # Default parameters if not provided
    if model_params is None:
        model_params = {
            'iterations': 1000,
            'learning_rate': 0.03,
            'depth': 6,
            'loss_function': 'Logloss',
            'eval_metric': 'AUC',
            'random_seed': 42,
            'early_stopping_rounds': 50,
            'verbose': 50
        }
    
    # Setup cross-validation
    n_splits = 5
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    # Initialize metrics
    cv_scores = []
    feature_importances = []
    
    # Handle active learning metadata
    if active_learning_meta is None:
        active_learning_meta = {
            "feedback_count": 0,
            "total_samples": len(X),
            "feedback_weight_percent": 0.0
        }
    
    # Start MLflow run
    setup_mlflow()
    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params(model_params)
        mlflow.log_param("feedback_count", active_learning_meta["feedback_count"])
        mlflow.log_param("total_samples", active_learning_meta["total_samples"])
        mlflow.log_param("feedback_weight_percent", active_learning_meta["feedback_weight_percent"])
        
        # Cross-validation
        for fold, (train_idx, val_idx) in enumerate(cv.split(X, y)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Extract sample weights for this fold if provided
            train_weights = None
            if sample_weights is not None:
                train_weights = sample_weights[train_idx]
            
            # Train model with sample weights if available
            model = CatBoostClassifier(**model_params)
            model.fit(
                X_train, y_train,
                sample_weight=train_weights,  # Apply sample weights for active learning
                eval_set=[(X_val, y_val)],
                use_best_model=True
            )
            
            # Evaluate
            y_pred = model.predict_proba(X_val)[:, 1]
            auc = roc_auc_score(y_val, y_pred)
            cv_scores.append(auc)
            
            # Log feature importance
            feature_importances.append(model.get_feature_importance())
            
            logger.info(f"Fold {fold+1}/{n_splits} - AUC: {auc:.4f}")
            
            # Log metrics for this fold
            mlflow.log_metric(f"auc_fold_{fold+1}", auc)
        
        # Calculate average metrics
        mean_auc = np.mean(cv_scores)
        std_auc = np.std(cv_scores)
        logger.info(f"Cross-validation AUC: {mean_auc:.4f} ± {std_auc:.4f}")
        
        # Log average metrics
        mlflow.log_metric("cv_auc_mean", mean_auc)
        mlflow.log_metric("cv_auc_std", std_auc)
        
        # Train final model on all data with sample weights
        final_model = CatBoostClassifier(**model_params)
        final_model.fit(X, y, sample_weight=sample_weights, verbose=100)
        
        # Calculate feature importance
        avg_importance = np.mean(np.array(feature_importances), axis=0)
        feature_importance_dict = dict(zip(X.columns, avg_importance))
        sorted_features = sorted(
            feature_importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        top_features = [f[0] for f in sorted_features[:5]]
        logger.info(f"Top features: {top_features}")
        
        # Log feature importance
        for feature, importance in feature_importance_dict.items():
            mlflow.log_metric(f"importance_{feature}", importance)
        
        # Log model
        mlflow.catboost.log_model(final_model, "model")
        
        # Save metrics
        metrics = {
            "auc_cv_mean": float(mean_auc),
            "auc_cv_std": float(std_auc),
            "feature_importance": feature_importance_dict,
            "top_features": top_features,
            "feedback_count": active_learning_meta["feedback_count"],
            "feedback_weight_percent": active_learning_meta["feedback_weight_percent"]
        }
        
        # Update model metadata
        model_metadata = {
            "model_version": run.info.run_id[:8],
            "train_date": datetime.now().strftime("%Y-%m-%d"),
            "features": list(X.columns),
            "auc_score": float(mean_auc),
            "cv_auc_mean": float(mean_auc),
            "cv_auc_std": float(std_auc),
            "top_features": top_features,
            "feedback_count": active_learning_meta["feedback_count"],
            "feedback_weight_percent": active_learning_meta["feedback_weight_percent"]
        }
        
        # Return final model and metrics
        return final_model, model_metadata


def save_model(model: CatBoostClassifier, metadata: Dict[str, Any]):
    """
    Save model to disk.
    
    Args:
        model: Trained CatBoost model
        metadata: Model metadata
    """
    try:
        # Save model
        model.save_model(MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")
        
        # Save metadata
        with open(MODEL_METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Model metadata saved to {MODEL_METADATA_PATH}")
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise


def evaluate_model_improvement(
    new_auc: float, 
    db: Session
) -> Tuple[bool, Optional[float]]:
    """
    Evaluate whether the new model is better than the current production model.
    
    Args:
        new_auc: AUC score of the new model
        db: Database session
        
    Returns:
        Tuple containing:
        - Boolean indicating if the new model is better
        - Improvement in AUC as a percentage, or None if no production model exists
    """
    # Get the current production model
    current_model = db.query(ModelVersion).filter(
        ModelVersion.in_production == True
    ).first()
    
    if current_model is None:
        # No production model yet, so this is an improvement
        logger.info("No production model found. New model will be deployed.")
        return True, None
    
    # Calculate improvement
    improvement = new_auc - current_model.auc_score
    improvement_percent = improvement / current_model.auc_score * 100
    
    logger.info(f"Current production model AUC: {current_model.auc_score:.4f}")
    logger.info(f"New model AUC: {new_auc:.4f}")
    logger.info(f"Improvement: {improvement_percent:.2f}%")
    
    # Check if improvement is sufficient (1% or more)
    if improvement_percent >= 1.0:
        logger.info("New model shows significant improvement. Will deploy.")
        return True, improvement_percent
    else:
        logger.info("New model doesn't show significant improvement. No deployment needed.")
        return False, improvement_percent


def deploy_model(
    model_version: str, 
    auc_score: float, 
    run_id: str, 
    metrics: Dict[str, Any],
    db: Session
):
    """
    Deploy the new model to production.
    
    Args:
        model_version: Version identifier for the model
        auc_score: AUC score of the model
        run_id: MLflow run ID
        metrics: Model metrics
        db: Database session
    """
    # Set all existing models to not in production
    db.query(ModelVersion).filter(
        ModelVersion.in_production == True
    ).update({"in_production": False})
    
    # Create new model version record
    new_model_version = ModelVersion(
        model_version=model_version,
        mlflow_run_id=run_id,
        auc_score=auc_score,
        in_production=True,
        metrics=json.dumps(metrics)
    )
    
    db.add(new_model_version)
    db.commit()
    
    logger.info(f"Model version {model_version} deployed to production")


def run_training_pipeline():
    """
    Run the full training pipeline.
    """
    try:
        with SessionLocal() as db:
            # 1. Update outcome labels
            nightly_outcome_update()
            
            # 2. Prepare training data with active learning from LP feedback
            X, y, sample_weights, active_learning_meta = prepare_training_data(db)
            
            # 3. Train model
            setup_mlflow()
            with mlflow.start_run() as run:
                model, metadata = train_model(
                    X, 
                    y, 
                    sample_weights=sample_weights,
                    active_learning_meta=active_learning_meta
                )
                
                # 4. Save model
                save_model(model, metadata)
                
                # 5. Evaluate improvement
                is_better, improvement = evaluate_model_improvement(
                    metadata["auc_score"], 
                    db
                )
                
                # Log improvement information
                mlflow.log_metric("auc_improvement_percent", 
                                 0.0 if improvement is None else improvement)
                mlflow.log_param("deployed", is_better)
                
                # 6. Deploy if better
                if is_better:
                    # Calculate feedback impact on model performance
                    feedback_impact = None
                    if active_learning_meta["feedback_count"] > 0 and improvement is not None:
                        # Estimate the portion of improvement due to feedback (rough heuristic)
                        feedback_impact = improvement * (active_learning_meta["feedback_weight_percent"] / 100.0)
                        
                    deploy_model(
                        metadata["model_version"],
                        metadata["auc_score"],
                        run.info.run_id,
                        {
                            "auc": metadata["auc_score"],
                            "cv_auc_mean": metadata["cv_auc_mean"],
                            "cv_auc_std": metadata["cv_auc_std"],
                            "improvement": improvement,
                            "feedback_count": active_learning_meta["feedback_count"],
                            "feedback_weight_percent": active_learning_meta["feedback_weight_percent"],
                            "feedback_improvement": feedback_impact
                        },
                        db
                    )
                
                logger.info("Training pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    run_training_pipeline()