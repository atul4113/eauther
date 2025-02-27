import pytest
from django.contrib.auth.models import User
from src.libraries.utility.queues import trigger_backend_task

from tests_src.TestCase import DBTestCase, TestCase
"""
    Basic tests created to check if script for running tests works correctly.
"""

@pytest.fixture()
def create_a_lot_of_users():
    for i in range(0, 100):
        User.objects.create(username="sd{}".format(i))

@pytest.fixture()
def create_another_a_lot_of_users():
    for i in range(0, 120):
        User.objects.create(username="ssd{}".format(i))


class TestsSomeTests(DBTestCase):
    def test_1(self, create_a_lot_of_users):
        trigger_backend_task('/my_super_url')
        assert self.get_task_count('default') == 1

    def test_2(self, create_a_lot_of_users):
        trigger_backend_task('/my_super_url')
        assert self.get_task_count('default') == 1

    def test_3(self, create_a_lot_of_users, create_another_a_lot_of_users):
        assert 220 == User.objects.all().count()

    def test_6(self, create_a_lot_of_users):
        pass

    def test_5(self, create_a_lot_of_users):
        pass

    def test_4(self, create_a_lot_of_users):
        pass


class TestSimpleUnitTests(TestCase):
    def test_1(self):
        assert True

    def test_2(self):
        assert True
