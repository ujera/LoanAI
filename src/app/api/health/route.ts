import { NextResponse } from 'next/server';

export async function GET() {
  const checks = {
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'unknown',
    status: 'checking',
    services: {
      database: {
        configured: !!(process.env.DB_HOST && process.env.DB_USER && process.env.DB_NAME),
        host: process.env.DB_HOST ? '✓ Set' : '✗ Missing',
        user: process.env.DB_USER ? '✓ Set' : '✗ Missing',
        database: process.env.DB_NAME ? '✓ Set' : '✗ Missing',
      },
      storage: {
        configured: !!(process.env.GCS_BUCKET_NAME && process.env.GOOGLE_APPLICATION_CREDENTIALS),
        bucket: process.env.GCS_BUCKET_NAME ? '✓ Set' : '✗ Missing',
        credentials: process.env.GOOGLE_APPLICATION_CREDENTIALS ? '✓ Set' : '✗ Missing',
      },
      gcp: {
        projectId: process.env.GCP_PROJECT_ID ? '✓ Set' : '✗ Missing',
        apiKey: process.env.GOOGLE_API_KEY ? '✓ Set' : '✗ Missing',
      }
    },
    recommendations: [] as string[],
  };

  // Add recommendations based on checks
  if (!checks.services.database.configured) {
    checks.recommendations.push('Database not configured. Set DB_HOST, DB_USER, DB_NAME in .env');
  }
  
  if (!checks.services.storage.configured) {
    checks.recommendations.push('Cloud Storage not configured. Set GCS_BUCKET_NAME and GOOGLE_APPLICATION_CREDENTIALS in .env');
  }

  // Test database connection if configured
  if (checks.services.database.configured) {
    try {
      const { query } = await import('@/lib/db');
      await query('SELECT 1');
      checks.services.database.status = '✓ Connected';
    } catch (error) {
      checks.services.database.status = '✗ Failed';
      checks.services.database.error = error instanceof Error ? error.message : 'Unknown error';
      checks.recommendations.push('Database connection failed. Ensure Cloud SQL Proxy is running.');
    }
  } else {
    checks.services.database.status = '⚠ Not configured';
  }

  // Test storage connection if configured
  if (checks.services.storage.configured) {
    try {
      const { getBucket } = await import('@/lib/storage');
      const bucket = getBucket();
      const [exists] = await bucket.exists();
      checks.services.storage.status = exists ? '✓ Connected' : '✗ Bucket not found';
      if (!exists) {
        checks.recommendations.push('Storage bucket not found. Verify GCS_BUCKET_NAME in .env');
      }
    } catch (error) {
      checks.services.storage.status = '✗ Failed';
      checks.services.storage.error = error instanceof Error ? error.message : 'Unknown error';
      checks.recommendations.push('Storage connection failed. Check GOOGLE_APPLICATION_CREDENTIALS path.');
    }
  } else {
    checks.services.storage.status = '⚠ Not configured';
  }

  // Determine overall status
  const dbOk = checks.services.database.status?.includes('✓') || checks.services.database.status?.includes('⚠');
  const storageOk = checks.services.storage.status?.includes('✓') || checks.services.storage.status?.includes('⚠');
  
  if (dbOk && storageOk && checks.recommendations.length === 0) {
    checks.status = '✓ All systems operational';
  } else if (checks.recommendations.length > 0) {
    checks.status = '⚠ Configuration needed';
  } else {
    checks.status = '✗ Services unavailable';
  }

  return NextResponse.json(checks, { 
    status: checks.status.includes('✗') ? 503 : 200 
  });
}
