#!/usr/bin/env node

/**
 * Quick Backend Status Checker
 * Run this before starting the dev server
 */

const fs = require('fs');
const path = require('path');

console.log('╔════════════════════════════════════════╗');
console.log('║   LoanAI Backend Status Check         ║');
console.log('╚════════════════════════════════════════╝\n');

let allGood = true;

// Check 1: .env file exists
console.log('📝 Checking .env file...');
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  console.log('   ✅ .env file found\n');
} else {
  console.log('   ❌ .env file NOT found');
  console.log('   📋 Action: Copy .env.example to .env\n');
  allGood = false;
}

// Check 2: config directory exists
console.log('📁 Checking config directory...');
const configPath = path.join(__dirname, '..', 'config');
if (fs.existsSync(configPath)) {
  console.log('   ✅ config/ directory found');
  
  // Check for GCP credentials
  const credPath = path.join(configPath, 'gcp-credentials.json');
  if (fs.existsSync(credPath)) {
    console.log('   ✅ gcp-credentials.json found\n');
  } else {
    console.log('   ❌ gcp-credentials.json NOT found');
    console.log('   📋 Action: Add your service account key to config/gcp-credentials.json\n');
    allGood = false;
  }
  
  // Check for Cloud SQL Proxy
  const proxyPath = path.join(configPath, 'cloud_sql_proxy');
  if (fs.existsSync(proxyPath)) {
    console.log('   ✅ cloud_sql_proxy found\n');
  } else {
    console.log('   ⚠️  cloud_sql_proxy NOT found');
    console.log('   📋 Action: Run cd config && ./setup-proxy.sh\n');
    allGood = false;
  }
} else {
  console.log('   ❌ config/ directory NOT found');
  console.log('   📋 Action: mkdir config\n');
  allGood = false;
}

// Check 3: Environment variables (if .env exists)
if (fs.existsSync(envPath)) {
  console.log('🔍 Checking environment variables...');
  const envContent = fs.readFileSync(envPath, 'utf-8');
  
  const requiredVars = [
    'DB_HOST',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
    'GCS_BUCKET_NAME',
    'GOOGLE_APPLICATION_CREDENTIALS'
  ];
  
  let missingVars = [];
  requiredVars.forEach(varName => {
    if (envContent.includes(`${varName}=`) && !envContent.includes(`${varName}=your-`)) {
      console.log(`   ✅ ${varName}`);
    } else {
      console.log(`   ❌ ${varName} - Not set or using placeholder`);
      missingVars.push(varName);
      allGood = false;
    }
  });
  
  if (missingVars.length > 0) {
    console.log('\n   📋 Action: Update these variables in .env');
  }
  console.log('');
}

// Check 4: Cloud SQL Proxy running
console.log('🔌 Checking Cloud SQL Proxy...');
const { execSync } = require('child_process');
try {
  const result = execSync('lsof -i :5432', { encoding: 'utf-8', stdio: 'pipe' });
  if (result.includes('cloud_sql_proxy') || result.includes('postgres')) {
    console.log('   ✅ Service running on port 5432\n');
  } else {
    console.log('   ⚠️  Port 5432 is used by unknown service\n');
  }
} catch (error) {
  console.log('   ❌ Nothing running on port 5432');
  console.log('   📋 Action: Start Cloud SQL Proxy in a separate terminal:');
  console.log('      cd config');
  console.log('      ./cloud_sql_proxy fourth-flag-481108-s5:us-central1:loanai-db-dev\n');
  allGood = false;
}

// Summary
console.log('═'.repeat(42));
if (allGood) {
  console.log('✅ All checks passed! Ready to start.');
  console.log('\n🚀 Run: npm run dev');
  console.log('═'.repeat(42));
  process.exit(0);
} else {
  console.log('⚠️  Some checks failed. Follow the actions above.');
  console.log('\n📚 For detailed help, see:');
  console.log('   - TROUBLESHOOTING.md');
  console.log('   - QUICKSTART.md');
  console.log('\n💡 Quick health check: http://localhost:3000/api/health');
  console.log('   (after starting the dev server)');
  console.log('═'.repeat(42));
  process.exit(1);
}
