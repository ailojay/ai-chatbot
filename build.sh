#!/bin/bash
set -e

echo "Building Lambda package..."

rm -rf build lambda.zip
mkdir build

echo "Installing dependencies..."
pip install \
  google-genai \
  requests \
  boto3 \
  -t build/ -q

echo "Copying application code..."
cp -r app build/
cp serverless/handler.py build/

echo "Creating zip..."
cd build && zip -r ../lambda.zip . -x "*.pyc" -x "__pycache__/*" && cd ..

echo "Done. lambda.zip is ready."
ls -lh lambda.zip