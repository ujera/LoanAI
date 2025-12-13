import { NextRequest, NextResponse } from 'next/server';
import { uploadFile } from '@/lib/storage';

export async function POST(request: NextRequest) {
  try {
    // Check if storage is configured
    if (!process.env.GCS_BUCKET_NAME || !process.env.GOOGLE_APPLICATION_CREDENTIALS) {
      console.error('Storage not configured. Missing environment variables.');
      return NextResponse.json(
        { 
          error: 'Storage service not configured',
          details: 'Cloud Storage credentials are missing. Please check TROUBLESHOOTING.md'
        },
        { status: 503 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const documentType = formData.get('documentType') as string;
    const customerId = formData.get('customerId') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    if (!documentType) {
      return NextResponse.json(
        { error: 'Document type is required' },
        { status: 400 }
      );
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File size exceeds 10MB limit' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/jpg',
      'image/png',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Only PDF, images, and Word documents are allowed' },
        { status: 400 }
      );
    }

    // Convert file to buffer
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Generate unique filename
    const timestamp = Date.now();
    const fileExtension = file.name.split('.').pop();
    const sanitizedDocumentType = documentType.replace(/[^a-zA-Z0-9]/g, '_');
    const destination = customerId 
      ? `customers/${customerId}/${sanitizedDocumentType}_${timestamp}.${fileExtension}`
      : `temp/${sanitizedDocumentType}_${timestamp}.${fileExtension}`;

    // Upload to Google Cloud Storage
    const fileUrl = await uploadFile(buffer, destination, file.type);

    return NextResponse.json(
      {
        success: true,
        fileUrl: fileUrl,
        fileName: file.name,
        fileSize: file.size,
        mimeType: file.type,
        documentType: documentType,
        destination: destination
      },
      { status: 200 }
    );

  } catch (error) {
    console.error('Error uploading document:', error);
    
    // Provide specific error messages
    let errorMessage = 'Failed to upload document';
    let errorDetails = 'Unknown error';
    
    if (error instanceof Error) {
      errorDetails = error.message;
      
      // Check for specific error types
      if (error.message.includes('credentials') || error.message.includes('authentication')) {
        errorMessage = 'Storage authentication failed';
        errorDetails = 'Please ensure gcp-credentials.json is in the config folder and GOOGLE_APPLICATION_CREDENTIALS is set in .env';
      } else if (error.message.includes('bucket') || error.message.includes('not found')) {
        errorMessage = 'Storage bucket not found';
        errorDetails = 'Please verify GCS_BUCKET_NAME in .env matches your Google Cloud Storage bucket';
      }
    }
    
    return NextResponse.json(
      { 
        error: errorMessage,
        details: errorDetails,
        troubleshooting: 'See TROUBLESHOOTING.md for setup instructions'
      },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filePath = searchParams.get('filePath');

    if (!filePath) {
      return NextResponse.json(
        { error: 'File path is required' },
        { status: 400 }
      );
    }

    const { deleteFile } = await import('@/lib/storage');
    await deleteFile(filePath);

    return NextResponse.json(
      { success: true, message: 'File deleted successfully' },
      { status: 200 }
    );

  } catch (error) {
    console.error('Error deleting document:', error);
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}
