#!/usr/bin/env node

/**
 * Backend Health Check Script
 * Tests database and storage connectivity
 */

async function testDatabaseConnection() {
  console.log('\n🔍 Testing Database Connection...');
  try {
    const { query } = require('../src/lib/db');
    const result = await query('SELECT version()');
    console.log('✅ Database Connected Successfully');
    console.log('   PostgreSQL Version:', result.rows[0].version.split(',')[0]);
    
    // Test tables exist
    const tables = await query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    console.log('✅ Database Tables:');
    tables.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });
    
    return true;
  } catch (error) {
    console.error('❌ Database Connection Failed:', error.message);
    return false;
  }
}

async function testStorageConnection() {
  console.log('\n🔍 Testing Cloud Storage Connection...');
  try {
    const { getBucket } = require('../src/lib/storage');
    const bucket = getBucket();
    
    const [exists] = await bucket.exists();
    if (exists) {
      console.log('✅ Storage Bucket Connected Successfully');
      console.log('   Bucket Name:', bucket.name);
      
      // Test bucket permissions
      const [files] = await bucket.getFiles({ maxResults: 1 });
      console.log(`✅ Bucket Access: OK (${files.length > 0 ? 'Contains files' : 'Empty'})`);
    } else {
      console.error('❌ Storage Bucket Does Not Exist');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('❌ Storage Connection Failed:', error.message);
    return false;
  }
}

async function testEnvironmentVariables() {
  console.log('\n🔍 Checking Environment Variables...');
  const required = [
    'DB_HOST',
    'DB_PORT',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
    'GCS_BUCKET_NAME',
    'GCS_PROJECT_ID',
    'GOOGLE_APPLICATION_CREDENTIALS'
  ];
  
  let allPresent = true;
  required.forEach(varName => {
    if (process.env[varName]) {
      console.log(`✅ ${varName}: Set`);
    } else {
      console.log(`❌ ${varName}: Missing`);
      allPresent = false;
    }
  });
  
  return allPresent;
}

async function main() {
  console.log('╔════════════════════════════════════════╗');
  console.log('║   LoanAI Backend Health Check         ║');
  console.log('╚════════════════════════════════════════╝');
  
  // Load environment variables
  require('dotenv').config();
  
  const envOk = await testEnvironmentVariables();
  const dbOk = await testDatabaseConnection();
  const storageOk = await testStorageConnection();
  
  console.log('\n' + '═'.repeat(42));
  console.log('Summary:');
  console.log('═'.repeat(42));
  console.log(`Environment Variables: ${envOk ? '✅ OK' : '❌ FAIL'}`);
  console.log(`Database Connection:   ${dbOk ? '✅ OK' : '❌ FAIL'}`);
  console.log(`Storage Connection:    ${storageOk ? '✅ OK' : '❌ FAIL'}`);
  console.log('═'.repeat(42));
  
  if (envOk && dbOk && storageOk) {
    console.log('\n🎉 All systems operational!\n');
    process.exit(0);
  } else {
    console.log('\n⚠️  Some systems are not operational. Please check the errors above.\n');
    process.exit(1);
  }
}

main().catch(error => {
  console.error('\n❌ Health check failed:', error);
  process.exit(1);
});
