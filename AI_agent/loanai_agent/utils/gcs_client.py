"""Google Cloud Storage client utilities for document retrieval."""

import os
import time
from functools import wraps
from typing import Dict, Optional, Tuple

from google.api_core import retry
from google.cloud import storage

from config.settings import settings
from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)


class GCSClient:
    """Client for interacting with Google Cloud Storage."""

    def __init__(self, cache_ttl: int = 300):
        """Initialize GCS client with credentials from settings.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self._client: Optional[storage.Client] = None
        self._bucket: Optional[storage.Bucket] = None
        self._file_cache: Dict[str, Tuple[bytes, float]] = {}  # url -> (content, timestamp)
        self.cache_ttl = cache_ttl
        self.max_retries = 3

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

    @retry.Retry(
        predicate=retry.if_transient_error,
        initial=1.0,
        maximum=10.0,
        multiplier=2.0,
        deadline=60.0,
    )
    def download_file(self, gs_url: str, use_cache: bool = True) -> bytes:
        """
        Download file from GCS with retry logic and caching.
        
        Args:
            gs_url: GCS URL in format gs://bucket-name/path/to/file
            use_cache: Whether to use cached files (default: True)
            
        Returns:
            File content as bytes
            
        Raises:
            ValueError: If URL format is invalid
            FileNotFoundError: If file doesn't exist in GCS
            Exception: If download fails after retries
        """
        # Check cache first
        if use_cache and gs_url in self._file_cache:
            content, timestamp = self._file_cache[gs_url]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {gs_url}")
                return content
            else:
                # Cache expired, remove it
                logger.debug(f"Cache expired for {gs_url}")
                del self._file_cache[gs_url]
        
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
            
            # Cache the result
            if use_cache:
                self._file_cache[gs_url] = (content, time.time())
                logger.debug(f"Cached file: {gs_url}")
            
            return content
            
        except FileNotFoundError:
            # Don't retry for file not found
            logger.error(f"File not found in GCS: {gs_url}")
            raise
        except Exception as e:
            logger.error(f"Failed to download file from GCS {gs_url}: {e}", exc_info=True)
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


    def clear_cache(self, gs_url: Optional[str] = None) -> None:
        """Clear file cache.
        
        Args:
            gs_url: Specific URL to clear, or None to clear all
        """
        if gs_url:
            if gs_url in self._file_cache:
                del self._file_cache[gs_url]
                logger.debug(f"Cleared cache for {gs_url}")
        else:
            self._file_cache.clear()
            logger.debug("Cleared all cache")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache size and item count
        """
        total_size = sum(len(content) for content, _ in self._file_cache.values())
        return {
            "cached_files": len(self._file_cache),
            "total_size_bytes": total_size,
            "cache_ttl_seconds": self.cache_ttl,
        }


# Global GCS client instance
_gcs_client: Optional[GCSClient] = None


def get_gcs_client() -> GCSClient:
    """Get or create global GCS client instance."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSClient()
    return _gcs_client
