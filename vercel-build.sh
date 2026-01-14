#!/bin/bash
# Vercel Build Script
# This script runs during the Vercel build process

echo "Starting Vercel build..."

# Create necessary directories (though they won't persist in serverless)
mkdir -p uploads recordings

# Install any additional build dependencies if needed
# pip install --upgrade pip

echo "Vercel build completed successfully!"
