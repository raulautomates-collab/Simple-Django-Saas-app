

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(f'the base directory is{BASE_DIR}')

#Quick-start development settings - unsuitable for production


# Email Configuration

# settings.py

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', default='587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', default='True')
#EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', default='False') 
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', default=None)

DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'raulautomates@gmail.com')
SERVER_EMAIL = os.environ.get('EMAIL_HOST_USER', 'raulautomates@gmail.com')

# Email admins for sending emails
ADMINS = [('dominic','dominicomondi747@gamil.com')]
MANAGERS = ADMINS

#1->notes: Changed my user email several times,used an older email indicated above for authentictaion
#2->notes:Remove the email use SSL setting ,both are mutually exclusive.Unfortunately have to add.env file to github for testing
#3->notes: Do not use .env in production


# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.environ.get('DJANGO_SECRET_KEY'))


# Default (no need to add this unless customizing)
AUTH_USER_MODEL = 'auth.User'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  str(os.environ.get('DJANGO_DEBUG'))
BASE_URL=os.environ.get('BASE_URL',default=None)
ALLOWED_HOSTS = ['.railway.app']
if DEBUG:
    ALLOWED_HOSTS+=[
        '127.0.0.1',
        'localhost'
    ]



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    
    #internal apps
    'Visits',
    'commando',
    'PROFILES',
    'CHECKOUTS',
    'SUBS',
   
    'PROSPECTS',
    

    #tThird party apps
     "allauth_ui",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "widget_tweaks",
    "slippers",

    
]
# settings.py
ALLAUTH_UI_THEME = "light"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    "allauth.account.middleware.AccountMiddleware",

    #WHITENOISE MIDDLWARE
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    

]

SOCIALACCOUNT_PROVIDERS = {
    'github':{
        "VERIFIED_EMAIL":True
    }
}

ROOT_URLCONF = 'cfehome.urls'
LOGIN_REDIRECT_URL='/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cfehome.wsgi.application'


#DJANGO ALL AUTH CONFIG




# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASE_URL =os.environ.get('NEON_DATABASE_URL')


CONN_HEALTH_CHECKS = True



#
#  Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
    
]

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_BASE_DIR=BASE_DIR /"staticfiles"
STATICFILES_BASE_DIR.mkdir(exist_ok=True,parents=True)

STATICFILES_VENDOR_DIR=STATICFILES_BASE_DIR /"vendors"

#source for manage.py collect static
STATICFILES_DIRS=[
    STATICFILES_BASE_DIR
]

#LOCAL CDN FOR STATICFILES
STATIC_ROOT=BASE_DIR.parent /"local-cdn"
BASE_URL=os.environ.get('BASE_URL')