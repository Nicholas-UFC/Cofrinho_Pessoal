import sys
from datetime import timedelta
from pathlib import Path

import environ

# Detecta se estamos em modo de teste (pytest importado) para ajustar configs.
_MODO_TESTE = "pytest" in sys.modules

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Segurança — cabeçalhos e cookies (sempre ativos, não só em produção).
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt.token_blacklist",
]

LOCAL_APPS = [
    "financas",
    "whatsapp",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "axes",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "financas.middleware.MiddlewareLogAcesso",
    "financas.middleware.MiddlewareSecurityHeaders",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# PostgreSQL é o único banco suportado — sempre lido do DATABASE_URL.
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# Configurações de segurança HTTPS — ativas apenas em produção.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation"
        ".MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"  # noqa: E501
    },
    {
        "NAME": "financas.validators.ValidadorComplexidadeSenha",
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = env("TIME_ZONE", default="America/Fortaleza")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Jazzmin — personalização do Django Admin
JAZZMIN_SETTINGS = {
    "site_title": "Cofrinho Pessoal",
    "site_header": "Cofrinho Pessoal",
    "site_brand": "Cofrinho",
    "welcome_sign": "Bem-vindo ao painel de controle",
    # Link de atalho no menu superior para a documentação da API.
    "topmenu_links": [
        {
            "name": "API Docs",
            "url": "/api/docs/",
            "new_window": True,
            "icon": "fas fa-book",
        },
    ],
    # Ícones Font Awesome para cada model na barra lateral.
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "financas.Categoria": "fas fa-tags",
        "financas.Fonte": "fas fa-wallet",
        "financas.Gasto": "fas fa-arrow-trend-down",
        "financas.Entrada": "fas fa-arrow-trend-up",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Cookie-based auth tem prioridade — OWASP prática 76.
        "financas.autenticacao.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Paginação padrão: 20 itens por página.
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
    # Rate limiting — OWASP prática 94.
    # Em modo de teste o throttling é desabilitado para evitar contaminação
    # entre testes; test_throttling.py re-habilita via override_settings.
    "DEFAULT_THROTTLE_CLASSES": (
        []
        if _MODO_TESTE
        else [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ]
    ),
    "DEFAULT_THROTTLE_RATES": (
        {}
        if _MODO_TESTE
        else {
            "anon": "20/min",
            "user": "200/min",
        }
    ),
}

# SimpleJWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    # Blacklista o refresh anterior ao rotacionar — OWASP prática 62.
    "BLACKLIST_AFTER_ROTATION": True,
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Cofrinho Pessoal API",
    "DESCRIPTION": "API para controle de gastos pessoais.",
    "VERSION": "0.1.0",
}

# CORS — OWASP prática 92.
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = False
# Necessário para withCredentials (cookies httpOnly) — OWASP prática 76.
CORS_ALLOW_CREDENTIALS = True

# django-axes
AXES_FAILURE_LIMIT = 5

# WAHA — WhatsApp HTTP API
WAHA_API_URL = env("WAHA_API_URL", default="http://localhost:3000")
WAHA_API_KEY = env("WAHA_API_KEY", default="")
WAHA_GROUP_ID = env("WAHA_GROUP_ID", default="")
WAHA_SESSION = env("WAHA_SESSION", default="default")
WAHA_OWNER_USERNAME = env("WAHA_OWNER_USERNAME", default="")
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]

# Logging estruturado — OWASP práticas 113-130.
# Registra eventos de segurança (401, 403, 5xx) em arquivo e console.
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detalhado": {
            "format": ("%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detalhado",
        },
        "arquivo_seguranca": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "seguranca.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "detalhado",
            "encoding": "utf-8",
        },
        "arquivo_erros": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "erros.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "detalhado",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # Eventos de segurança (auth, axes, JWT).
        "django.security": {
            "handlers": ["console", "arquivo_seguranca"],
            "level": "WARNING",
            "propagate": False,
        },
        # Erros internos do servidor (5xx).
        "django.request": {
            "handlers": ["console", "arquivo_erros"],
            "level": "ERROR",
            "propagate": False,
        },
        # Axes — bloqueio de contas.
        "axes": {
            "handlers": ["console", "arquivo_seguranca"],
            "level": "WARNING",
            "propagate": False,
        },
        # App local — whatsapp (falhas TLS, HTTP).
        "whatsapp": {
            "handlers": ["console", "arquivo_seguranca"],
            "level": "WARNING",
            "propagate": False,
        },
        # App local — financas.
        "financas": {
            "handlers": ["console", "arquivo_seguranca"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
