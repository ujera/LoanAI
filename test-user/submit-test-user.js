/**
 * Test User Submission Script
 * Sends a test loan application to the backend API
 */

const testUserData = {
  // Personal Information
  firstName: "Luka",
  lastName: "Narsia",
  personalId: "0XX010XXXX",
  gender: "male",
  birthYear: "1990",
  phone: "+995555123456",
  address: "Tbilisi, Georgia",

  // Education
  educationLevel: "bachelor",
  university: "Georgian Technical University",

  // Employment
  employmentStatus: "employed",
  companyName: "GeoTech Solutions LLC",
  monthlySalary: "3500",
  experienceYears: "5",

  // Loan Details
  loanPurpose: "business",
  loanAmount: "15000",
  loanDuration: "24",
  additionalInfo: "Software Engineer at GeoTech Solutions LLC. Payment date: March 5, 2025. Currency: GEL",

  // Documents (if you have uploaded them)
  // bankStatementUrl: "path/to/bank/statement",
  // salaryStatementUrl: "path/to/salary/statement",
};

async function submitTestUser() {
  const backendUrl = 'http://localhost:3000/api/loan-application';
  
  console.log('Submitting test user to backend...');
  console.log('Backend URL:', backendUrl);
  console.log('\nTest User Data:');
  console.log(JSON.stringify(testUserData, null, 2));
  console.log('\n' + '='.repeat(50));

  try {
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testUserData),
    });

    const responseData = await response.json();

    console.log('\nResponse Status:', response.status);
    console.log('Response Data:');
    console.log(JSON.stringify(responseData, null, 2));

    if (response.ok) {
      console.log('\n✅ SUCCESS! Test user submitted successfully!');
      console.log('Customer ID:', responseData.customerId);
      
      if (responseData.customerId) {
        console.log('\nYou can check the application at:');
        console.log(`http://localhost:3000/api/loan-application?customerId=${responseData.customerId}`);
      }
    } else {
      console.log('\n❌ FAILED! Submission failed.');
      if (responseData.error) {
        console.log('Error:', responseData.error);
      }
      if (responseData.details) {
        console.log('Details:', responseData.details);
      }
    }
  } catch (error) {
    console.error('\n❌ ERROR! Failed to submit test user:');
    console.error(error.message);
    console.error('\nMake sure:');
    console.error('1. Backend server is running (npm run dev)');
    console.error('2. Cloud SQL Proxy is running (./start-proxy.sh)');
    console.error('3. Database is properly configured');
  }
}

// Run the submission
submitTestUser();
