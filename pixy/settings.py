from pathlib import Path
import environ
import sys, os, json
import pymysql

# environ 설정
env = environ.Env(
    DEBUG = (bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
pymysql.install_as_MySQLdb()

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
DOMAIN = env('DOMAIN')
API_DOMAIN = env('API_DOMAIN')
PUBLIC_IPv4 = env('PUBLIC_IPv4')
LOCAL_HOST = env('LOCAL_HOST')

ALLOWED_HOSTS = [DOMAIN, API_DOMAIN, PUBLIC_IPv4, LOCAL_HOST]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sites',
    
    'accounts',
    'notice',
    'post',
    'product',
    'store',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'storages',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.naver',
    'notifications',
    'corsheaders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://pixy.kro.kr",
    "http://localhost:8000",  # 개발 환경용
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "pixy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pixy.wsgi.application"

REDIS_USERNAME = env('REDIS_USERNAME')
REDIS_PASSWORD = env('REDIS_PASSWORD')
REDIS_PORT = env('REDIS_PORT')

# Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{PUBLIC_IPv4}:{REDIS_PORT}",
    }
}

# Swagger Authorize
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Token"
        }
    },
    'SECURITY_REQUIREMENTS': [{
        'BearerAuth': []
    }]
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env('DATABASE_NAME'),
        "USER": env('DATABASE_USERNAME'),
        "PASSWORD": env('DATABASE_PASSWORD'),
        "HOST": env('DATABASE_HOST'),
        "PORT": env('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 추가
AUTH_USER_MODEL = 'accounts.User' # 커스텀 유저를 장고에서 사용하기 위함
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # 인증된 요청인지 확인
        # 'rest_framework.permissions.IsAdminUser',  # 관리자만 접근 가능
        # 'rest_framework.permissions.AllowAny',  # 누구나 접근 가능
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT를 통한 인증방식 사용
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3,
}

REST_USE_JWT = True

from datetime import timedelta
SIMPLE_JWT = {
    'SIGNING_KEY': env('SECRET_KEY'),
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # True로 설정할 경우, refresh token을 보내면 새로운 access token과 refresh token이 반환된다.
    'ROTATE_REFRESH_TOKENS': False,
    # True로 설정될 경우, 기존에 있던 refresh token은 blacklist가된다.
    'BLACKLIST_AFTER_ROTATION': True,
}
# 이미지 추가
# MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 비밀번호 재설정(이메일 수신 : 발신(google))
EMAIL_BACKEND=env('EMAIL_BACKEND')
EMAIL_PORT=env('EMAIL_PORT')
EMAIL_HOST=env('EMAIL_HOST')
EMAIL_HOST_USER=env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=EMAIL_HOST_USER

# 소셜 로그인
# 사이트는 1개만 사용할 것이라고 명시
SITE_ID = 1

ACCOUNT_USER_MODEL_USERNAME_FIELD = None # username 필드 사용 x
ACCOUNT_EMAIL_REQUIRED = True            # email 필드 사용 o
ACCOUNT_USERNAME_REQUIRED = False        # username 필드 사용 x
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIAL_AUTH_GOOGLE_CLIENT_ID = env('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = env('SOCIAL_AUTH_GOOGLE_SECRET')
STATE = env('STATE')

# S3 Storages
# AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
# AWS_REGION = env('AWS_REGION')

# AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME, AWS_REGION)
# DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE')
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'