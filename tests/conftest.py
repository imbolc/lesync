from pathlib import Path
import django
from django.conf import settings
from django.core.management import call_command


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / '.tests.sqlite'


def pytest_configure():
    if DB_PATH.exists():
        DB_PATH.unlink()
    settings.configure(
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(DB_PATH)
        }},
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'channels',
        ],
        ROOT_URLCONF='urls',
    )
    django.setup()
    call_command('migrate')
