"""Google Cloud Storage client utilities for document retrieval."""

import os
from typing import Optional, Tuple

from google.cloud import storage

from config.settings import settings
from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)


class GCSClient:
    """Client for interacting with Google Cloud Storage."""

    def __init__(self):
        """Initialize GCS client with credentials from settings."""
        self._client: Optional[storage.Client] = None
        self._bucket: Optional[storage.Bucket] = None

    def _get_client(self) -> storage.Client:
        """Get or create storage client."""
        if self._client is None:
            try:
                # Set credentials path from settings
                credentials_path = settings.google_application_credentials
                
                # Make path absolute if it's relative
                if not os.path.isabs(credentials_path):
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    credentials_path = os.path.join(base_dir, credentials_path)
                
                # Check if credentials file exists
                if not os.path.exists(credentials_path):
                    logger.warning(
                        f"GCS credentials file not found at {credentials_path}. "
                        "Document retrieval will fail."
                    )
                    raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
                
                # Set environment variable for google-cloud-storage
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                self._client = storage.Client(project=settings.gcp_project_id)
                logger.info(f"GCS client initialized for project: {settings.gcp_project_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize GCS client: {e}")
                raise
        
        return self._client

    def _get_bucket(self) -> storage.Bucket:
        """Get or create bucket reference."""
        if self._bucket is None:
            client = self._get_client()
            self._bucket = client.bucket(settings.gcs_bucket_name)
            logger.info(f"Connected to GCS bucket: {settings.gcs_bucket_name}")
        
        return self._bucket

    @staticmethod
    def parse_gs_url(gs_url: str) -> Tuple[str, str]:
        """
        Parse a gs:// URL into bucket name and blob path.
        
        Args:
            gs_url: GCS URL in format gs://bucket-name/path/to/file
            
        Returns:
            Tuple of (bucket_name, blob_path)
            
        Raises:
            ValueError: If URL format is invalid
        """
        if not gs_url.startswith("gs://"):
            raise ValueError(f"Invalid GCS URL format: {gs_url}. Must start with 'gs://'")
        
        # Remove gs:// prefix
        path = gs_url[5:]
        
        # Split into bucket and blob path
        parts = path.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URL format: {gs_url}. Expected gs://bucket/path")
        
        bucket_name, blob_path = parts
        logger.debug(f"Parsed GCS URL - Bucket: {bucket_name}, Path: {blob_path}")
        
        return bucket_name, blob_path

    def download_file(self, gs_url: str) -> bytes:
        """
        Download file from GCS.
        
        Args:
            gs_url: GCS URL in format gs://bucket-name/path/to/file
            
        Returns:
            File content as bytes
            
        Raises:
            ValueError: If URL format is invalid
            Exception: If download fails
        """
        try:
            # Parse the GCS URL
            bucket_name, blob_path = self.parse_gs_url(gs_url)
            
            # Verify bucket name matches configured bucket
            if bucket_name != settings.gcs_bucket_name:
                logger.warning(
                    f"URL bucket '{bucket_name}' differs from configured bucket "
                    f"'{settings.gcs_bucket_name}'. Proceeding with URL bucket."
                )
            
            # Get bucket and blob
            client = self._get_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            # Check if blob exists
            if not blob.exists():
                raise FileNotFoundError(f"File not found in GCS: {gs_url}")
            
            # Download the file
            logger.info(f"Downloading file from GCS: {blob_path}")
            content = blob.download_as_bytes()
            logger.info(f"Successfully downloaded {len(content)} bytes from {gs_url}")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to download file from GCS {gs_url}: {e}")
            raise

    def download_to_file(self, gs_url: str, destination_path: str) -> str:
        """
        Download file from GCS to local path.
        
        Args:
            gs_url: GCS URL in format gs://bucket-name/path/to/file
            destination_path: Local file path to save the downloaded file
            
        Returns:
            Path to downloaded file
            
        Raises:
            ValueError: If URL format is invalid
            Exception: If download fails
        """
        try:
            # Parse the GCS URL
            bucket_name, blob_path = self.parse_gs_url(gs_url)
            
            # Get bucket and blob
            client = self._get_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            # Check if blob exists
            if not blob.exists():
                raise FileNotFoundError(f"File not found in GCS: {gs_url}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Download to file
            logger.info(f"Downloading file from GCS to {destination_path}")
            blob.download_to_filename(destination_path)
            logger.info(f"Successfully downloaded file to {destination_path}")
            
            return destination_path
            
        except Exception as e:
            logger.error(f"Failed to download file from GCS {gs_url}: {e}")
            raise

    def file_exists(self, gs_url: str) -> bool:
        """
        Check if file exists in GCS.
        
        Args:
            gs_url: GCS URL in format gs://bucket-name/path/to/file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            bucket_name, blob_path = self.parse_gs_url(gs_url)
            client = self._get_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            exists = blob.exists()
            logger.debug(f"File exists check for {gs_url}: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking file existence for {gs_url}: {e}")
            return False


# Global GCS client instance
_gcs_client: Optional[GCSClient] = None


def get_gcs_client() -> GCSClient:
    """Get or create global GCS client instance."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSClient()
    return _gcs_client
