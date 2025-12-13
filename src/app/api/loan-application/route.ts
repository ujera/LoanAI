import { NextRequest, NextResponse } from 'next/server';
import { query, getClient } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: NextRequest) {
  let client;
  
  try {
    client = await getClient();
  } catch (dbError) {
    console.error('Database connection error:', dbError);
    return NextResponse.json(
      { 
        error: 'Database connection failed',
        details: 'Please ensure Cloud SQL Proxy is running. See QUICKSTART.md for setup instructions.',
        technicalError: dbError instanceof Error ? dbError.message : 'Unknown error'
      },
      { status: 503 }
    );
  }

  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.firstName || !body.lastName || !body.personalId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    await client.query('BEGIN');

    // 1. Create customer record
    const customerResult = await client.query(
      `INSERT INTO customers (customer_id, application_status, eligibility_score)
       VALUES ($1, $2, $3)
       RETURNING customer_id`,
      [uuidv4(), 'pending', null]
    );

    const customerId = customerResult.rows[0].customer_id;

    // 2. Insert personal information
    await client.query(
      `INSERT INTO customer_personal_info (
        customer_id, first_name, last_name, personal_id, 
        gender, birth_year, phone, address
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        customerId,
        body.firstName,
        body.lastName,
        body.personalId,
        body.gender,
        body.birthYear,
        body.phone,
        body.address
      ]
    );

    // 3. Insert education information
    await client.query(
      `INSERT INTO customer_education (
        customer_id, education_level, university
      ) VALUES ($1, $2, $3)`,
      [
        customerId,
        body.educationLevel,
        body.university || null
      ]
    );

    // 4. Insert employment information
    await client.query(
      `INSERT INTO customer_employment (
        customer_id, employment_status, company_name, 
        monthly_salary, experience_years
      ) VALUES ($1, $2, $3, $4, $5)`,
      [
        customerId,
        body.employmentStatus,
        body.companyName || null,
        parseFloat(body.monthlySalary) || 0,
        parseInt(body.experienceYears) || 0
      ]
    );

    // 5. Insert loan application
    await client.query(
      `INSERT INTO loan_applications (
        customer_id, loan_purpose, loan_amount, 
        loan_duration, additional_info, application_date
      ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)`,
      [
        customerId,
        body.loanPurpose,
        parseFloat(body.loanAmount) || 0,
        parseInt(body.loanDuration) || 0,
        body.additionalInfo || null
      ]
    );

    // 6. Insert document records (if documents were uploaded)
    if (body.bankStatementUrl) {
      const bankFileName = body.bankStatementUrl.split('/').pop() || 'bank_statement.pdf';
      await client.query(
        `INSERT INTO customer_documents (
          customer_id, document_type, file_name, file_path, file_size, mime_type, uploaded_at
        ) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)`,
        [
          customerId,
          'bank_statement',
          bankFileName,
          body.bankStatementUrl,
          body.bankStatementSize || 0,
          body.bankStatementMimeType || 'application/octet-stream'
        ]
      );
    }

    if (body.salaryStatementUrl) {
      const salaryFileName = body.salaryStatementUrl.split('/').pop() || 'salary_statement.pdf';
      await client.query(
        `INSERT INTO customer_documents (
          customer_id, document_type, file_name, file_path, file_size, mime_type, uploaded_at
        ) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)`,
        [
          customerId,
          'salary_statement',
          salaryFileName,
          body.salaryStatementUrl,
          body.salaryStatementSize || 0,
          body.salaryStatementMimeType || 'application/octet-stream'
        ]
      );
    }

    await client.query('COMMIT');

    // Send data to AI agent system for processing
    try {
      const agentResponse = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customerId: customerId,
          firstName: body.firstName,
          lastName: body.lastName,
          personalId: body.personalId,
          gender: body.gender,
          birthYear: body.birthYear,
          phone: body.phone,
          address: body.address,
          educationLevel: body.educationLevel,
          university: body.university || 'Not Specified',
          employmentStatus: body.employmentStatus,
          companyName: body.companyName || null,
          monthlySalary: parseFloat(body.monthlySalary) || 0,
          experienceYears: parseInt(body.experienceYears) || 0,
          loanPurpose: body.loanPurpose,
          loanAmount: parseFloat(body.loanAmount) || 0,
          loanDuration: parseInt(body.loanDuration) || 0,
          additionalInfo: body.additionalInfo || null,
          bankStatementUrl: body.bankStatementUrl || null,
          bankStatementSize: body.bankStatementSize || null,
          bankStatementMimeType: body.bankStatementMimeType || null,
          salaryStatementUrl: body.salaryStatementUrl || null,
          salaryStatementSize: body.salaryStatementSize || null,
          salaryStatementMimeType: body.salaryStatementMimeType || null,
        }),
      });

      if (!agentResponse.ok) {
        console.error('AI Agent processing failed:', await agentResponse.text());
        // Don't fail the whole request if AI processing fails
      } else {
        const agentResult = await agentResponse.json();
        console.log('AI Agent processing started:', agentResult);
      }
    } catch (agentError) {
      console.error('Error sending to AI agent system:', agentError);
      // Don't fail the whole request if AI agent is unavailable
    }

    return NextResponse.json(
      {
        success: true,
        customerId: customerId,
        message: 'Loan application submitted successfully and sent for AI processing'
      },
      { status: 201 }
    );

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Error creating loan application:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to submit loan application',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  } finally {
    client.release();
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const customerId = searchParams.get('customerId');

    if (!customerId) {
      // Return all applications (limit to recent 100)
      const result = await query(
        `SELECT 
          c.customer_id,
          c.application_status,
          c.eligibility_score,
          c.created_at,
          cpi.first_name,
          cpi.last_name,
          la.loan_amount,
          la.loan_purpose
        FROM customers c
        JOIN customer_personal_info cpi ON c.customer_id = cpi.customer_id
        JOIN loan_applications la ON c.customer_id = la.customer_id
        ORDER BY c.created_at DESC
        LIMIT 100`
      );

      return NextResponse.json({ applications: result.rows });
    }

    // Return specific application
    const result = await query(
      `SELECT 
        c.*,
        cpi.*,
        ce.*,
        cem.*,
        la.*
      FROM customers c
      LEFT JOIN customer_personal_info cpi ON c.customer_id = cpi.customer_id
      LEFT JOIN customer_education ce ON c.customer_id = ce.customer_id
      LEFT JOIN customer_employment cem ON c.customer_id = cem.customer_id
      LEFT JOIN loan_applications la ON c.customer_id = la.customer_id
      WHERE c.customer_id = $1`,
      [customerId]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: 'Application not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ application: result.rows[0] });

  } catch (error) {
    console.error('Error fetching loan application:', error);
    return NextResponse.json(
      { error: 'Failed to fetch loan application' },
      { status: 500 }
    );
  }
}
