"""
Cloud Storage Database Sync
===========================

This module handles syncing SQLite database and attachments with Google Cloud Storage
to provide persistence for Cloud Run deployments.
"""

import os
import logging
import shutil
from pathlib import Path
from google.cloud import storage
from google.api_core import exceptions
import time

logger = logging.getLogger(__name__)

class DatabaseSync:
    def __init__(self, bucket_name="tweener-portfolio-data", db_filename="tracker.db", attachments_dir="attachments"):
        self.bucket_name = bucket_name
        self.db_filename = db_filename
        self.attachments_dir = attachments_dir
        self.local_db_path = db_filename
        self.cloud_db_path = f"database/{db_filename}"
        self.cloud_attachments_path = "attachments/"
        
        # Initialize Cloud Storage client
        try:
            self.client = storage.Client()
            self.bucket = None
            logger.info("Cloud Storage client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage client: {e}")
            self.client = None
            self.bucket = None
    
    def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        if not self.client:
            return False
            
        try:
            self.bucket = self.client.get_bucket(self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
            return True
        except exceptions.NotFound:
            try:
                # Create bucket in us-central1 to match Cloud Run region
                self.bucket = self.client.create_bucket(self.bucket_name, location="us-central1")
                logger.info(f"Created new bucket: {self.bucket_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Error checking bucket {self.bucket_name}: {e}")
            return False
    
    def download_database(self):
        """Download database from Cloud Storage if it exists"""
        if not self.client or not self.ensure_bucket_exists():
            logger.warning("Cloud Storage not available, using local database")
            return False
        
        try:
            blob = self.bucket.blob(self.cloud_db_path)
            if blob.exists():
                blob.download_to_filename(self.local_db_path)
                logger.info(f"Downloaded database from Cloud Storage: {self.cloud_db_path}")
                return True
            else:
                logger.info("No database found in Cloud Storage, will create new one")
                return False
        except Exception as e:
            logger.error(f"Failed to download database from Cloud Storage: {e}")
            return False
    
    def upload_database(self):
        """Upload database to Cloud Storage"""
        if not self.client or not self.ensure_bucket_exists():
            logger.warning("Cloud Storage not available, cannot backup database")
            return False
        
        if not os.path.exists(self.local_db_path):
            logger.warning(f"Local database file {self.local_db_path} does not exist")
            return False
        
        try:
            blob = self.bucket.blob(self.cloud_db_path)
            blob.upload_from_filename(self.local_db_path)
            logger.info(f"Uploaded database to Cloud Storage: {self.cloud_db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload database to Cloud Storage: {e}")
            return False
    
    def download_attachments(self):
        """Download all attachments from Cloud Storage"""
        if not self.client or not self.ensure_bucket_exists():
            logger.warning("Cloud Storage not available, cannot download attachments")
            return False
        
        try:
            # Create local attachments directory if it doesn't exist
            os.makedirs(self.attachments_dir, exist_ok=True)
            
            # List all blobs in the attachments folder
            blobs = self.client.list_blobs(self.bucket, prefix=self.cloud_attachments_path)
            
            downloaded_count = 0
            for blob in blobs:
                if blob.name.endswith('/'):  # Skip directory entries
                    continue
                
                # Create local path
                relative_path = blob.name.replace(self.cloud_attachments_path, '')
                local_path = os.path.join(self.attachments_dir, relative_path)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Download file
                blob.download_to_filename(local_path)
                downloaded_count += 1
            
            logger.info(f"Downloaded {downloaded_count} attachment files from Cloud Storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download attachments from Cloud Storage: {e}")
            return False
    
    def upload_attachments(self):
        """Upload all attachments to Cloud Storage"""
        if not self.client or not self.ensure_bucket_exists():
            logger.warning("Cloud Storage not available, cannot backup attachments")
            return False
        
        if not os.path.exists(self.attachments_dir):
            logger.info("No attachments directory found, skipping upload")
            return True
        
        try:
            uploaded_count = 0
            for root, dirs, files in os.walk(self.attachments_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    
                    # Create cloud path
                    relative_path = os.path.relpath(local_path, self.attachments_dir)
                    cloud_path = f"{self.cloud_attachments_path}{relative_path}".replace('\\', '/')
                    
                    # Upload file
                    blob = self.bucket.blob(cloud_path)
                    blob.upload_from_filename(local_path)
                    uploaded_count += 1
            
            logger.info(f"Uploaded {uploaded_count} attachment files to Cloud Storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload attachments to Cloud Storage: {e}")
            return False
    
    def sync_on_startup(self):
        """Sync database and attachments on application startup"""
        logger.info("Starting full data sync from Cloud Storage...")
        
        # Download database
        db_downloaded = self.download_database()
        
        # Download attachments
        attachments_downloaded = self.download_attachments()
        
        if db_downloaded or attachments_downloaded:
            logger.info("Data sync completed successfully")
        else:
            logger.info("No existing data in cloud, will use local/create new")
        
        return db_downloaded, attachments_downloaded
    
    def sync_on_changes(self, sync_attachments=True):
        """Upload database and optionally attachments after changes"""
        db_success = self.upload_database()
        
        attachments_success = True
        if sync_attachments:
            attachments_success = self.upload_attachments()
        
        return db_success and attachments_success
    
    def backup_database(self):
        """Create a timestamped backup of the database"""
        if not self.client or not self.ensure_bucket_exists():
            return False
        
        timestamp = int(time.time())
        backup_path = f"backups/tracker_backup_{timestamp}.db"
        
        try:
            if os.path.exists(self.local_db_path):
                blob = self.bucket.blob(backup_path)
                blob.upload_from_filename(self.local_db_path)
                logger.info(f"Created database backup: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
        
        return False
    
    def upload_single_attachment(self, local_path):
        """Upload a single attachment file to Cloud Storage"""
        if not self.client or not self.ensure_bucket_exists():
            return False
        
        try:
            # Create cloud path
            relative_path = os.path.relpath(local_path, self.attachments_dir)
            cloud_path = f"{self.cloud_attachments_path}{relative_path}".replace('\\', '/')
            
            # Upload file
            blob = self.bucket.blob(cloud_path)
            blob.upload_from_filename(local_path)
            logger.info(f"Uploaded attachment to Cloud Storage: {cloud_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload attachment {local_path}: {e}")
            return False