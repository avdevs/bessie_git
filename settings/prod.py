from .base import *
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

#to be replaced with production db details
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'bessie',
    #     'USER': 'bessie_user', 
    #     'PASSWORD': '21hKqZ6vBYrLdVxsxxiyMjaq4zR0hPhb', 
    #     'HOST': 'dpg-cv4mnql2ng1s73bpkje0-a',
    #     'PORT': '5432',
    # }
    #external from render uri ::: postgresql://bessie_user:21hKqZ6vBYrLdVxsxxiyMjaq4zR0hPhb@dpg-cv4mnql2ng1s73bpkje0-a.oregon-postgres.render.com/bessie
    #render internal uri ::: postgresql://bessie_user:21hKqZ6vBYrLdVxsxxiyMjaq4zR0hPhb@dpg-cv4mnql2ng1s73bpkje0-a/bessie

    'default': dj_database_url.config(
        default='postgresql://bessie_user:21hKqZ6vBYrLdVxsxxiyMjaq4zR0hPhb@dpg-cv4mnql2ng1s73bpkje0-a/bessie',
        conn_max_age=600
    )
}

ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'