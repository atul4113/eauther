from django.conf import settings


NUMBERS = getattr(settings, 'MATH_CAPTCHA_NUMBERS', list(range(1,6)))
OPERATORS = getattr(settings, 'MATH_CAPTCHA_OPERATORS', '-+')
QUESTION = getattr(settings, 'MATH_CAPTCHA_QUESTION', 'Are you human? ')
