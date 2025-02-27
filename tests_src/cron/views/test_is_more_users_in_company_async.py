# coding=utf-8
from tests_src.cron.cron_mocks import RequestMock
from tests_src.TestCase import DBTestCase
from mock import patch
from src.lorepo.cron.views import is_more_users_in_company_async
import pytest
from django.contrib.auth.models import User

from src.lorepo.corporate.models import CompanyProperties, CompanyUser
from src.lorepo.spaces.models import Space, SpaceType

OWNER_EMAILS = ['user@user.com', 'user1@user.com']


def get_owner_email_patch(users, company):
    return OWNER_EMAILS


@pytest.fixture(scope='function')
def company_space():
    return Space.objects.create(
        space_type=SpaceType.CORPORATE,
        parent=None,
        is_deleted=False
    )


@pytest.fixture(scope='function')
def space_properties_with_1_user(company_space):
    return CompanyProperties.objects.create(
        company=company_space,
        max_accounts=1
    )


@pytest.fixture(scope='function')
def space_properties_with_2_users(company_space):
    return CompanyProperties.objects.create(
        company=company_space,
        max_accounts=2
    )


@pytest.fixture(scope='function')
def two_company_users(company_space):
    for i in range(2):
        user = User.objects.create()

        CompanyUser.objects.create(
            user=user,
            company=company_space
        )


@patch('lorepo.public.util.EmailMultiAlternatives')
@patch('lorepo.cron.views.get_owners_emails', get_owner_email_patch)
class TestSendingMessagesWithAddressesSetToBCCWhenCheckingForTooManyUsers(DBTestCase):

    def test_given_two_users_and_space_allowing_one_user_when_calling_is_more_users_in_company_THEN_message_sent_to_owners_in_BCC_field(
            self,
            email_mock, company_space, space_properties_with_1_user, two_company_users):

        request = RequestMock()
        is_more_users_in_company_async(request)

        expected_emails_first_call = OWNER_EMAILS

        assert 1 == email_mock.call_count
        assert expected_emails_first_call == email_mock.call_args_list[0][1]['bcc']
        assert 1 == len(email_mock.call_args_list[0][1]['to'])

    def test_given_two_users_and_space_allowing_two_users_when_calling_lock_companies_async_THEN_mail_is_not_sent(
            self,
            email_mock, company_space, space_properties_with_2_users, two_company_users):

        request = RequestMock()
        is_more_users_in_company_async(request)

        assert 0 == email_mock.call_count


