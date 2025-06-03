from pathlib import Path
import os

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass 



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    if os.environ.get('GAE_APPLICATION') or os.environ.get('PYTHONANYWHERE_DOMAIN'):
        raise Exception('SECRET_KEY must be set in production environment variables!')
    else:
        SECRET_KEY = '_zhm+iw-psshyakjos-@t8)=63ow#qjxk&67x*dxv2=h!*vsy0'
        print("AVISO: Usando SECRET_KEY de desenvolvimento. Defina DJANGO_SECRET_KEY em variáveis de ambiente para produção.")


# SEGURANÇA CRÍTICA: DEBUG
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True' 
# Lista de hosts/domínios pelos quais seu Django pode servir requisições.
ALLOWED_HOSTS = [] 

if DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']
else:
 
    pythonanywhere_domain = os.environ.get('PYTHONANYWHERE_DOMAIN')
    if pythonanywhere_domain:
        ALLOWED_HOSTS.append(pythonanywhere_domain)
    if 'Edison88.pythonanywhere.com' not in ALLOWED_HOSTS: 
        ALLOWED_HOSTS.append('Edison88.pythonanywhere.com')
    if not ALLOWED_HOSTS:
        raise Exception('ALLOWED_HOSTS must be set in production (e.g., in PythonAnywhere Web tab environment variables) or explicitly in settings.py!')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'core', 
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agenda_dentista.urls'
LOGIN_REDIRECT_URL = 'agenda' 
LOGIN_URL = 'login'           

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'agenda_dentista.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuração para Produção (irá substituir a do SQLite quando DEBUG=False)
if not DEBUG:
    DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.mysql') 
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST') 
    DB_PORT = os.environ.get('DB_PORT', '') 

    if all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
        DATABASES['default'] = {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    else:
        raise Exception("Credenciais de banco de dados de produção (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST) não definidas em variáveis de ambiente!")


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Definido pt-br como você queria

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5" 
CRISPY_TEMPLATE_PACK = "bootstrap5"
