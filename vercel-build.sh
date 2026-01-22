#!/bin/bash
# Vercel Build Script
# This script runs during the Vercel build process

echo "Starting Vercel build..."

# Create necessary directories (though they won't persist in serverless)
mkdir -p uploads recordings

# Install OEMER without dependencies to avoid onnxruntime-gpu requirement
pip install --no-deps oemer==0.1.8

echo "Vercel build completed successfully!"
