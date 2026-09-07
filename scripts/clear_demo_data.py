"""
Script to remove all demo existing data from the database and storage for SIH26100.
Keeps clean User accounts (admin and procurement_officer) so users can immediately log in and create fresh data.
"""

import os
import sys
import shutil

# Ensure backend modules are on PYTHONPATH
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import Base, engine, SessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import User
from app.core.logging_config import logger

def clear_all_demo_data():
    logger.info("Dropping all existing database tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Re-creating clean database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Creating initial administrative & procurement officer accounts...")
        admin_user = User(
            name="Sunil Verma, Chief Procurement Officer",
            email="admin@gem.gov.in",
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="ADMIN",
            department="Ministry of Petroleum & Natural Gas - Policy Division, New Delhi"
        )
        db.add(admin_user)

        officer_user = User(
            name="Rajesh Sharma, Senior Procurement Officer",
            email="officer@gem.gov.in",
            username="procurement_officer",
            password_hash=get_password_hash("officer123"),
            role="PROCUREMENT_OFFICER",
            department="GAIL / MoPNG Pipeline Tender Evaluation Cell, New Delhi"
        )
        db.add(officer_user)
        db.commit()
        logger.info("User accounts created successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding user accounts: {e}")
        raise
    finally:
        db.close()

    # Clean up uploads directories
    upload_dirs = [
        settings.UPLOAD_DIR,
        os.path.join(backend_dir, "uploads"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    ]

    for u_dir in set(upload_dirs):
        if os.path.exists(u_dir):
            logger.info(f"Cleaning upload directory: {u_dir}")
            for filename in os.listdir(u_dir):
                file_path = os.path.join(u_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete {file_path}: {e}")

    logger.info("All demo data has been completely cleared. System is in clean fresh state!")

if __name__ == "__main__":
    clear_all_demo_data()
