-- Common Database Queries for LoanAI

-- ==========================================
-- INSPECTION QUERIES
-- ==========================================

-- View all applications with customer names
SELECT 
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
LIMIT 20;

-- Get complete application details
SELECT 
    c.customer_id,
    c.application_status,
    c.eligibility_score,
    c.created_at,
    cpi.first_name,
    cpi.last_name,
    cpi.personal_id,
    cpi.gender,
    cpi.birth_year,
    cpi.phone,
    cpi.address,
    ce.education_level,
    ce.university,
    cem.employment_status,
    cem.company_name,
    cem.monthly_salary,
    cem.experience_years,
    la.loan_purpose,
    la.loan_amount,
    la.loan_duration_months,
    la.additional_info
FROM customers c
JOIN customer_personal_info cpi ON c.customer_id = cpi.customer_id
LEFT JOIN customer_education ce ON c.customer_id = ce.customer_id
LEFT JOIN customer_employment cem ON c.customer_id = cem.customer_id
LEFT JOIN loan_applications la ON c.customer_id = la.customer_id
WHERE c.customer_id = 'PASTE_CUSTOMER_ID_HERE';

-- View all documents for a customer
SELECT 
    cd.document_id,
    cd.document_type,
    cd.document_url,
    cd.upload_date,
    cpi.first_name,
    cpi.last_name
FROM customer_documents cd
JOIN customer_personal_info cpi ON cd.customer_id = cpi.customer_id
WHERE cd.customer_id = 'PASTE_CUSTOMER_ID_HERE';

-- Count applications by status
SELECT 
    application_status,
    COUNT(*) as count
FROM customers
GROUP BY application_status
ORDER BY count DESC;

-- Average loan amount by purpose
SELECT 
    loan_purpose,
    AVG(loan_amount) as avg_amount,
    COUNT(*) as count
FROM loan_applications
GROUP BY loan_purpose
ORDER BY avg_amount DESC;

-- Average salary by employment status
SELECT 
    employment_status,
    AVG(monthly_salary) as avg_salary,
    COUNT(*) as count
FROM customer_employment
GROUP BY employment_status
ORDER BY avg_salary DESC;

-- ==========================================
-- MAINTENANCE QUERIES
-- ==========================================

-- Delete a specific customer and all related data (CASCADE)
-- WARNING: This will delete all related records
DELETE FROM customers 
WHERE customer_id = 'PASTE_CUSTOMER_ID_HERE';

-- Update application status
UPDATE customers 
SET application_status = 'approved', 
    eligibility_score = 85,
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id = 'PASTE_CUSTOMER_ID_HERE';

-- Find applications without documents
SELECT 
    c.customer_id,
    cpi.first_name,
    cpi.last_name,
    c.created_at
FROM customers c
JOIN customer_personal_info cpi ON c.customer_id = cpi.customer_id
LEFT JOIN customer_documents cd ON c.customer_id = cd.customer_id
WHERE cd.document_id IS NULL
ORDER BY c.created_at DESC;

-- ==========================================
-- STATISTICS QUERIES
-- ==========================================

-- Daily application count
SELECT 
    DATE(created_at) as application_date,
    COUNT(*) as applications
FROM customers
GROUP BY DATE(created_at)
ORDER BY application_date DESC
LIMIT 30;

-- Approval rate by education level
SELECT 
    ce.education_level,
    COUNT(*) as total_applications,
    SUM(CASE WHEN c.application_status = 'approved' THEN 1 ELSE 0 END) as approved,
    ROUND(100.0 * SUM(CASE WHEN c.application_status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate
FROM customers c
JOIN customer_education ce ON c.customer_id = ce.customer_id
GROUP BY ce.education_level
ORDER BY approval_rate DESC;

-- Average eligibility score by employment status
SELECT 
    cem.employment_status,
    AVG(c.eligibility_score) as avg_score,
    COUNT(*) as count
FROM customers c
JOIN customer_employment cem ON c.customer_id = cem.customer_id
WHERE c.eligibility_score IS NOT NULL
GROUP BY cem.employment_status
ORDER BY avg_score DESC;

-- Top loan purposes
SELECT 
    loan_purpose,
    COUNT(*) as count,
    SUM(loan_amount) as total_amount,
    AVG(loan_amount) as avg_amount
FROM loan_applications
GROUP BY loan_purpose
ORDER BY count DESC;

-- ==========================================
-- TESTING QUERIES
-- ==========================================

-- Insert a test customer (for development)
DO $$
DECLARE
    test_customer_id UUID := uuid_generate_v4();
BEGIN
    -- Create customer
    INSERT INTO customers (customer_id, application_status)
    VALUES (test_customer_id, 'pending');
    
    -- Add personal info
    INSERT INTO customer_personal_info (
        customer_id, first_name, last_name, personal_id,
        gender, birth_year, phone, address
    ) VALUES (
        test_customer_id, 'Test', 'User', 'TEST123456',
        'male', '1990', '+1234567890', '123 Test Street'
    );
    
    -- Add education
    INSERT INTO customer_education (customer_id, education_level, university)
    VALUES (test_customer_id, 'bachelor', 'Test University');
    
    -- Add employment
    INSERT INTO customer_employment (
        customer_id, employment_status, company_name,
        monthly_salary, experience_years
    ) VALUES (
        test_customer_id, 'employed', 'Test Company', 5000, 5
    );
    
    -- Add loan application
    INSERT INTO loan_applications (
        customer_id, loan_purpose, loan_amount,
        loan_duration_months, application_date
    ) VALUES (
        test_customer_id, 'personal', 10000, 24, CURRENT_TIMESTAMP
    );
    
    RAISE NOTICE 'Test customer created with ID: %', test_customer_id;
END $$;

-- Verify table counts
SELECT 
    'customers' as table_name, COUNT(*) as row_count FROM customers
UNION ALL
SELECT 'customer_personal_info', COUNT(*) FROM customer_personal_info
UNION ALL
SELECT 'customer_education', COUNT(*) FROM customer_education
UNION ALL
SELECT 'customer_employment', COUNT(*) FROM customer_employment
UNION ALL
SELECT 'loan_applications', COUNT(*) FROM loan_applications
UNION ALL
SELECT 'customer_documents', COUNT(*) FROM customer_documents;

-- ==========================================
-- CLEANUP QUERIES
-- ==========================================

-- Delete all test data (BE CAREFUL!)
-- DELETE FROM customers WHERE customer_id IN (
--     SELECT customer_id FROM customer_personal_info 
--     WHERE first_name = 'Test'
-- );

-- Vacuum and analyze tables (for performance)
VACUUM ANALYZE customers;
VACUUM ANALYZE customer_personal_info;
VACUUM ANALYZE customer_education;
VACUUM ANALYZE customer_employment;
VACUUM ANALYZE loan_applications;
VACUUM ANALYZE customer_documents;
