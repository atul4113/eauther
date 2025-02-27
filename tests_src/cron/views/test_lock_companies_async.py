# coding=utf-8
from datetime import datetime, timedelta

from tests_src.cron.cron_mocks import create_space_mock, RequestMock
from tests_src.TestCase import TestCase
from mock import patch
from src.lorepo.cron.views import lock_companies_async

USER_EMAILS = ['user1@u.com', 'user2@u.com', 'user3@u.com']
SUPERUSERS_EMAILS = ['suser1@u.com', 'suser2@u.com', 'suser3@u.com']


def get_emails_patch(users):
    return USER_EMAILS


def get_superuser_emails_patch():
    return SUPERUSERS_EMAILS


def get_company_with_no_longer_valid_date():
    return [create_space_mock(1, 'test', datetime(2001, 9, 11), ['user1', 'user2', 'user3'], False, True)]


def get_company_with_no_longer_valid_date_and_title_with_unicode():
    return [create_space_mock(1, 'SPACE ąężłó â ˛ˇ˘'.decode('utf-8'), datetime(2001, 9, 11), ['user1', 'user2', 'user3'], False, True)]


def get_test_company_valid_for_ten_more_days():
    ten_days_date = datetime.today() + timedelta(days=10)
    return [create_space_mock(1, 'test', ten_days_date, ['user1', 'user2', 'user3'], False, True)]


@patch('lorepo.cron.views.lock')
@patch('lorepo.public.util.EmailMultiAlternatives')
@patch('lorepo.cron.views.get_users_emails', get_emails_patch)
@patch('lorepo.cron.views.get_superusers_emails', get_superuser_emails_patch)
class TestSendingMessagesWithAddressesSetToBCCWhenLockingCompanies(TestCase):

    @patch('lorepo.cron.views.get_companies', get_company_with_no_longer_valid_date)
    def test_given_out_of_date_space_when_calling_lock_companies_async_THEN_mail_is_sent_to_users_and_superusers_with_bcc_filled(
            self,
            email_mock, _):

        request = RequestMock()
        lock_companies_async(request)

        expected_emails_first_call = SUPERUSERS_EMAILS
        expected_emails_second_call = USER_EMAILS

        assert 2 == email_mock.call_count
        assert expected_emails_first_call == email_mock.call_args_list[0][1]['bcc']
        assert 1 == len(email_mock.call_args_list[0][1]['to'])
        assert expected_emails_second_call == email_mock.call_args_list[1][1]['bcc']
        assert 1 == len(email_mock.call_args_list[1][1]['to'])

    @patch('lorepo.cron.views.get_companies', get_company_with_no_longer_valid_date_and_title_with_unicode)
    def test_given_out_of_date_space_with_unicode_title_when_calling_lock_companies_async_then_mail_is_sent_to_users_and_superusers_with_bcc_filled(
            self,
            email_mock, _):

        request = RequestMock()
        lock_companies_async(request)

        expected_emails_first_call = SUPERUSERS_EMAILS
        expected_emails_second_call = USER_EMAILS

        assert 2 == email_mock.call_count
        assert expected_emails_first_call == email_mock.call_args_list[0][1]['bcc']
        assert 1 == len(email_mock.call_args_list[0][1]['to'])
        assert expected_emails_second_call == email_mock.call_args_list[1][1]['bcc']
        assert 1 == len(email_mock.call_args_list[1][1]['to'])

    @patch('lorepo.cron.views.get_companies', get_test_company_valid_for_ten_more_days)
    def test_given_space_valid_for_10_more_days_when_calling_lock_companies_async_then_mail_is_sent_to_space_users_with_bcc_field(
            self,
            email_mock, _):

        request = RequestMock()
        lock_companies_async(request)

        expected_emails_first_call = USER_EMAILS

        assert 1 == email_mock.call_count
        assert expected_emails_first_call == email_mock.call_args_list[0][1]['bcc']
        assert 1 == len(email_mock.call_args_list[0][1]['to'])
