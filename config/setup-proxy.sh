#!/bin/bash

# Cloud SQL Proxy Setup Script for macOS
# This script downloads and sets up the Cloud SQL Proxy

echo "🔧 Setting up Cloud SQL Proxy..."
echo ""

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    PROXY_URL="https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.darwin.arm64"
    echo "📱 Detected Apple Silicon (M1/M2/M3)"
elif [ "$ARCH" = "x86_64" ]; then
    PROXY_URL="https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.darwin.amd64"
    echo "💻 Detected Intel processor"
else
    echo "❌ Unknown architecture: $ARCH"
    exit 1
fi

echo ""
echo "📥 Downloading Cloud SQL Proxy..."
curl -o cloud_sql_proxy "$PROXY_URL"

if [ $? -ne 0 ]; then
    echo "❌ Failed to download Cloud SQL Proxy"
    exit 1
fi

echo "✅ Download complete"
echo ""
echo "🔐 Making executable..."
chmod +x cloud_sql_proxy

if [ $? -ne 0 ]; then
    echo "❌ Failed to make executable"
    exit 1
fi

echo "✅ Cloud SQL Proxy is ready!"
echo ""
echo "📋 To start the proxy, run:"
echo "   ./cloud_sql_proxy fourth-flag-481108-s5:us-central1:loanai-db-dev"
echo ""
echo "📋 Or with port forwarding:"
echo "   ./cloud_sql_proxy --port 5432 fourth-flag-481108-s5:us-central1:loanai-db-dev"
echo ""
echo "⚠️  Note: Make sure you have gcp-credentials.json in this directory!"
