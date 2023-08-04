from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "ecs-lb-1023174556.ap-northeast-2.elb.amazonaws.com",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",  # engine: mysql
        "NAME": "mysqldb",  # DB Name
        "USER": "admin",  # DB User
        "PASSWORD": env("AWS_DB_PASSWORD"),  # Password
        "HOST": env("AWS_DB_HOST"),  # 생성한 데이터베이스 엔드포인트
        "PORT": "3306",  # 데이터베이스 포트
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://localhost:80",
    "ecs-lb-1023174556.ap-northeast-2.elb.amazonaws.com",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://localhost:80",
    "ecs-lb-1023174556.ap-northeast-2.elb.amazonaws.com",
]
