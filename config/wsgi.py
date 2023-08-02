"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Docker로 실행해서 환경변수를 사용했을 때
category = "local" if os.environ.get("DEBUG", "1") == "1" else "prod"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{category}")

application = get_wsgi_application()
