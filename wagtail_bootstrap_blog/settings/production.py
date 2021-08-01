from .base import *
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0h1dnt(5_#46f8^k9q6c0bmjjt8u3cto)jet(3uhqsa&_iy8&4'
# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# DO NOT use on production, test key is available in the URL below
# https://developers.google.com/recaptcha/docs/faq
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
NOCAPTCHA = True
SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wagtail',
        'USER': 'pguser',
        'PASSWORD': 'pswdpass',
        'HOST': '172.18.1.2',
        'PORT': '',
    }
}
