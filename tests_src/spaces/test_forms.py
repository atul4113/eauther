# -*- coding: utf-8 -*-

from lorepo.spaces.form import AccessForm
from django.core.exceptions import ValidationError


def test_given_utf_8_title_when_throwing_validation_error_then_correctly_convert_to_unicode():
    access_form = AccessForm()
    validation_error = ''
    try:
        access_form._throw_validation_error(u'{0} {1}', u'zółć', u'Добро дошли у е-учионицу')
    except ValidationError as e:
        validation_error = e.message

    assert validation_error == u'zółć Добро дошли у е-учионицу'


def test_given_string_title_when_throwing_validation_error_then_correctly_convert_to_unicode():
    access_form = AccessForm()
    validation_error = ''
    try:
        access_form._throw_validation_error(u'{0} {1}', 'username', 'title')
    except ValidationError as e:
        validation_error = e.message

    assert validation_error == u'username title'
