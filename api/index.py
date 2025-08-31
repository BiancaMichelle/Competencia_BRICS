import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

def handler(request):
    """
    Vercel handler function that processes HTTP requests
    """
    # Convert Vercel request to Django WSGI environ
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(request.body) if request.body else 0),
        'SERVER_NAME': 'vercel',
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body or b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers
    for key, value in request.headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

    # Response handling
    status = [200]
    headers = []
    body_parts = []

    def start_response(status_line, response_headers, exc_info=None):
        status[0] = int(status_line.split()[0])
        headers.extend(response_headers)

    # Call the Django application
    try:
        response = application(environ, start_response)
        body_parts.extend(response)
    except Exception as e:
        # Error handling
        status[0] = 500
        headers = [('Content-Type', 'text/plain')]
        body_parts = [f'Internal Server Error: {str(e)}'.encode()]

    # Return response in Vercel format
    return {
        'statusCode': status[0],
        'headers': dict(headers),
        'body': b''.join(body_parts).decode('utf-8', errors='ignore')
    }

# For local development
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 8000, application, use_reloader=True)
