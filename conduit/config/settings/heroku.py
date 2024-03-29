# Local
from .base import *  # noqa
from .mixins.aws import *  # noqa
from .mixins.secure import *  # noqa

# Required for Heroku SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
