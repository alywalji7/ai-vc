"""
Command-line interface for radar model management.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
import pandas as pd
import mlflow
from typing import List, Dict, Any

from ..database import SessionLocal
from .pipeline import run_training_pipeline, nightly_outcome_update
from .mlflow_server import start_mlflow_server, stop_mlflow_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def train_command(args):
    """
    Run the training pipeline.
    
    Args:
        args: Command-line arguments
    """
    logger.info("Starting manual training pipeline")
    run_training_pipeline()
    logger.info("Training pipeline completed")


def update_outcomes_command(args):
    """
    Run the nightly outcome update process.
    
    Args:
        args: Command-line arguments
    """
    logger.info("Starting manual outcome update")
    with SessionLocal() as db:
        updated = nightly_outcome_update()
    logger.info(f"Outcome update completed. Updated {updated} records.")


def serve_command(args):
    """
    Start the MLflow server.
    
    Args:
        args: Command-line arguments
    """
    logger.info("Starting MLflow server")
    try:
        start_mlflow_server(use_thread=False)
        logger.info("MLflow server started. Press Ctrl+C to stop.")
        try:
            # Keep the script running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping MLflow server")
            stop_mlflow_server()
    except Exception as e:
        logger.error(f"Error starting MLflow server: {str(e)}")
        sys.exit(1)


def list_models_command(args):
    """
    List all models in MLflow.
    
    Args:
        args: Command-line arguments
    """
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        client = MlflowClient()
        
        # Get experiment
        experiment = mlflow.get_experiment_by_name("radar-model")
        if experiment is None:
            logger.error("No 'radar-model' experiment found")
            return
        
        # List runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if len(runs) == 0:
            logger.info("No models found")
            return
        
        # Print models
        print("\nRadar models:")
        print(f"{'Run ID':<36} {'Start Time':<20} {'Status':<10} {'AUC':<10} {'Deployed':<8}")
        print("-" * 90)
        
        for _, run in runs.iterrows():
            run_id = run.run_id
            status = run.status
            start_time = datetime.fromtimestamp(run.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
            
            # Get metrics
            auc = run.get("metrics.cv_auc_mean", "N/A")
            deployed = run.get("params.deployed", "False")
            
            print(f"{run_id:<36} {start_time:<20} {status:<10} {auc:<10.4f} {deployed:<8}")
        
        # Print current production model
        with SessionLocal() as db:
            from ..database import ModelVersion
            production_model = db.query(ModelVersion).filter(
                ModelVersion.in_production == True
            ).first()
            
            if production_model:
                print(f"\nCurrent production model: {production_model.model_version}")
                print(f"AUC score: {production_model.auc_score:.4f}")
                print(f"Training date: {production_model.training_date}")
                print(f"MLflow run ID: {production_model.mlflow_run_id}")
            else:
                print("\nNo production model found")
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        sys.exit(1)


def promote_command(args):
    """
    Promote a model to production.
    
    Args:
        args: Command-line arguments
    """
    run_id = args.run_id
    force = args.force
    
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        client = MlflowClient()
        
        # Check if run exists
        try:
            run = client.get_run(run_id)
        except:
            logger.error(f"Run ID {run_id} not found")
            return
        
        # Get metrics
        auc = run.data.metrics.get("cv_auc_mean", 0.0)
        
        # Promote model
        with SessionLocal() as db:
            from ..database import ModelVersion
            from .pipeline import deploy_model
            
            if not force:
                # Check for improvement
                from .pipeline import evaluate_model_improvement
                is_better, improvement = evaluate_model_improvement(auc, db)
                
                if not is_better:
                    logger.warning(f"Model {run_id} is not better than the current production model")
                    logger.warning(f"Current AUC: {auc:.4f}, Improvement: {improvement:.2f}%")
                    logger.warning("Use --force to promote anyway")
                    return
            
            # Deploy model
            deploy_model(
                run_id[:8],
                auc,
                run_id,
                {
                    "auc": auc,
                    "cv_auc_mean": auc,
                    "cv_auc_std": run.data.metrics.get("cv_auc_std", 0.0),
                    "forced_promotion": force
                },
                db
            )
            
            logger.info(f"Model {run_id} promoted to production")
    
    except Exception as e:
        logger.error(f"Error promoting model: {str(e)}")
        sys.exit(1)


def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="Radar Model Management CLI"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to run",
        required=True
    )
    
    # Train command
    train_parser = subparsers.add_parser(
        "train",
        help="Run the training pipeline"
    )
    train_parser.set_defaults(func=train_command)
    
    # Update outcomes command
    update_parser = subparsers.add_parser(
        "update-outcomes",
        help="Update company outcomes from external sources"
    )
    update_parser.set_defaults(func=update_outcomes_command)
    
    # Serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the MLflow server"
    )
    serve_parser.set_defaults(func=serve_command)
    
    # List models command
    list_parser = subparsers.add_parser(
        "list",
        help="List all models in MLflow"
    )
    list_parser.set_defaults(func=list_models_command)
    
    # Promote command
    promote_parser = subparsers.add_parser(
        "promote",
        help="Promote a model to production"
    )
    promote_parser.add_argument(
        "run_id",
        help="MLflow run ID of the model to promote"
    )
    promote_parser.add_argument(
        "--force",
        action="store_true",
        help="Force promotion even if the model is not better"
    )
    promote_parser.set_defaults(func=promote_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()