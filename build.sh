#!/bin/bash

# Render build script for JurisBrain Legal Knowledge API

echo "🏗️ Building JurisBrain Legal Knowledge API..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create minimal database if it doesn't exist
echo "🗄️ Setting up database..."
python setup_minimal_db.py

echo "✅ Build complete!"
