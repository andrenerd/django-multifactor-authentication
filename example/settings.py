import os
from django.urls import reverse_lazy

SITE_ID = 1

DEBUG = True

BASE_DIR = os.path.dirname(__file__)

SECRET_KEY = os.getenv('SECRET_KEY', 'xxx')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'multauth.sigent.com',
]

INSTALLED_APPS = (
    #'debug_toolbar',
    'django.contrib.sites',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.humanize',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',

    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg', # for dev only
    'localflavor',

    'multauth',
    'example',
)

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware', # custom
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'example.urls'

WSGI_APPLICATION = 'example.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data', 'db.sqlite3'),
    }
}


# Static Files
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
)


# API settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'multauth.api.authentication.TokenQueryAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
       'rest_framework.parsers.JSONParser',
       'rest_framework.parsers.FormParser',
       'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'multauth.api.handlers.api_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


SWAGGER_SETTINGS = {
   # default inspector classes, see advanced documentation
   'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
   'DEFAULT_FIELD_INSPECTORS': [
      'drf_yasg.inspectors.CamelCaseJSONFilter',
      'drf_yasg.inspectors.ReferencingSerializerInspector',
      'drf_yasg.inspectors.RelatedFieldInspector',
      'drf_yasg.inspectors.ChoiceFieldInspector',
      'drf_yasg.inspectors.FileFieldInspector',
      'drf_yasg.inspectors.DictFieldInspector',
      'drf_yasg.inspectors.SimpleFieldInspector',
      'drf_yasg.inspectors.StringDefaultFieldInspector',
   ],
   'DEFAULT_FILTER_INSPECTORS': [
      'drf_yasg.inspectors.CoreAPICompatInspector',
   ],
   'DEFAULT_PAGINATOR_INSPECTORS': [
      'drf_yasg.inspectors.DjangoRestResponsePagination',
      'drf_yasg.inspectors.CoreAPICompatInspector',
   ],

   # default api Info if none is otherwise given; should be an import string to an openapi.Info object
   'DEFAULT_INFO': None,
   # default API url if none is otherwise given
   'DEFAULT_API_URL': None,

   'USE_SESSION_AUTH': False,  # remove Django Login and Django Logout buttons, CSRF token to swagger UI page
   #'LOGIN_URL': getattr(django.conf.settings, 'LOGIN_URL', None),  # URL for the login button
   #'LOGOUT_URL': getattr(django.conf.settings, 'LOGOUT_URL', None),  # URL for the logout button

   # Swagger security definitions to include in the schema;
   # see https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#security-definitions-object
   'SECURITY_DEFINITIONS': {
      'basic': {
         'type': 'basic'
      },
      # 'Bearer': {
      #     'type': 'apiKey',
      #     'name': 'Authorization',
      #     'in': 'header'
      # },
   },

   # url to an external Swagger validation service; defaults to 'http://online.swagger.io/validator/'
   # set to None to disable the schema validation badge in the UI
   'VALIDATOR_URL': '',

   # swagger-ui configuration settings, see https://github.com/swagger-api/swagger-ui/blob/112bca906553a937ac67adc2e500bdeed96d067b/docs/usage/configuration.md#parameters
   'OPERATIONS_SORTER': None,
   'TAGS_SORTER': None,
   'DOC_EXPANSION': 'list',
   'DEEP_LINKING': False,
   'SHOW_EXTENSIONS': True,
   'DEFAULT_MODEL_RENDERING': 'example',
   'DEFAULT_MODEL_DEPTH': 3,
}


# MultAuth
AUTH_USER_MODEL = 'example.User'

AUTHENTICATION_BACKENDS = (
    'multauth.backends.UserBackend',
)

MULTAUTH_DEBUG = False
MULTAUTH_TOKEN_LENGTH = 6 # digits
MULTAUTH_TOKEN_EXPIRY = 3600 * 24 * 3 # days
MULTAUTH_EMAIL_REDIRECT = '/'
# MULTAUTH_EMAIL_TEMPLATE_NAME = 'custom'
# MULTAUTH_PHONE_TEMPLATE_NAME = 'custom'
# MULTAUTH_EMAIL_PROVIDER = CustomMailProvider
# MULTAUTH_PHONE_PROVIDER = CustomPhoneProvider

MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID = 'SID'
MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN = 'TOKEN'
MULTAUTH_PROVIDER_TWILIO_CALLER_ID = 'CALLER_ID'

