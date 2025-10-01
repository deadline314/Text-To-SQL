#!/bin/bash

# Unzip SSL certificates for database connection

CERT_DIR="./server-cert"

echo "Unzipping SSL certificates..."

cd "$CERT_DIR" || exit 1

if [ -f "server-ca.zip" ]; then
    unzip -o server-ca.zip
    echo "✓ server-ca.pem extracted"
fi

if [ -f "client-cert.zip" ]; then
    unzip -o client-cert.zip
    echo "✓ client-cert.pem extracted"
fi

if [ -f "client-key.zip" ]; then
    unzip -o client-key.zip
    echo "✓ client-key.pem extracted"
fi

echo ""
echo "SSL certificates ready!"
echo "Files in $CERT_DIR:"
ls -la *.pem 2>/dev/null || echo "No .pem files found"

