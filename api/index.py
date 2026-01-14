"""
Vercel Serverless Function Entry Point
This file is required for Vercel to properly route requests to the Flask app
"""
from app import app

# Export the Flask app as the serverless function handler
# Vercel's Python runtime will automatically wrap this
application = app

