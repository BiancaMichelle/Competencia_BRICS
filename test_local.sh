#!/bin/bash
# Test script for local development before Vercel deployment

echo "🧪 Testing Django app locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Test the Vercel handler
echo "🔧 Testing Vercel handler..."
python -c "
import sys
sys.path.insert(0, '.')
from api.index import handler

# Mock request
class MockRequest:
    def __init__(self):
        self.method = 'GET'
        self.path = '/'
        self.query_string = ''
        self.headers = {'host': 'localhost'}
        self.body = None

try:
    response = handler(MockRequest())
    print(f'✅ Handler test passed! Status: {response[\"statusCode\"]}')
except Exception as e:
    print(f'❌ Handler test failed: {e}')
"

# Run basic Django checks
echo "🔍 Running Django checks..."
python manage.py check

echo "✅ Local tests completed!"
echo ""
echo "🚀 If all tests pass, you can deploy to Vercel:"
echo "1. Push your code to GitHub"
echo "2. Connect your repo to Vercel"
echo "3. Configure environment variables"
echo "4. Deploy!"
