# Production Configuration for Better Performance
import os

# Production database with connection pooling
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:<your_password>@db.jpqmcqeextxdaqfhzeqb.supabase.co:5432/postgres')

# Redis for caching (recommended for production)
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHE_DEFAULT_TIMEOUT = 600  # 10 minutes

# Gzip Compression
COMPRESS_ENABLED = True
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')
DEBUG = False
TESTING = False

# CDN for static files
CDN_URL = os.environ.get('CDN_URL', 'https://your-cdn.com')

# Rate limiting
RATELIMIT_ENABLED = True
RATELIMIT_DEFAULT = '100 per minute'
RATELIMIT_STRATEGY = 'fixed-window'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = '/var/log/portfolio/app.log'

# Static file optimization
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files
PREFERRED_URL_SCHEME = 'https'
