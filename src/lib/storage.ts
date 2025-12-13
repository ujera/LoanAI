import { Storage } from '@google-cloud/storage';

// Initialize Google Cloud Storage client
let storageClient: Storage | null = null;

export function getStorageClient(): Storage {
  if (!storageClient) {
    // Check if credentials are configured
    if (!process.env.GOOGLE_APPLICATION_CREDENTIALS) {
      console.warn('GOOGLE_APPLICATION_CREDENTIALS not set. Storage operations may fail.');
    }
    
    try {
      storageClient = new Storage({
        projectId: process.env.GCS_PROJECT_ID,
        keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
      });
    } catch (error) {
      console.error('Failed to initialize Storage client:', error);
      throw new Error('Storage client initialization failed. Check your GCP credentials.');
    }
  }
  return storageClient;
}

export function getBucket() {
  const storage = getStorageClient();
  const bucketName = process.env.GCS_BUCKET_NAME || 'loanai-customer-documents-dev';
  return storage.bucket(bucketName);
}

export async function uploadFile(
  file: Buffer,
  destination: string,
  contentType: string
): Promise<string> {
  try {
    const bucket = getBucket();
    const blob = bucket.file(destination);

    await blob.save(file, {
      contentType: contentType,
      metadata: {
        cacheControl: 'public, max-age=31536000',
      },
    });

    console.log(`File uploaded to ${destination}`);
    
    // Return the public URL or signed URL
    return `gs://${bucket.name}/${destination}`;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}

export async function deleteFile(filePath: string): Promise<void> {
  try {
    const bucket = getBucket();
    await bucket.file(filePath).delete();
    console.log(`File ${filePath} deleted successfully`);
  } catch (error) {
    console.error('Error deleting file:', error);
    throw error;
  }
}

export async function getSignedUrl(filePath: string, expiresIn: number = 3600): Promise<string> {
  try {
    const bucket = getBucket();
    const [url] = await bucket.file(filePath).getSignedUrl({
      action: 'read',
      expires: Date.now() + expiresIn * 1000,
    });
    return url;
  } catch (error) {
    console.error('Error generating signed URL:', error);
    throw error;
  }
}
