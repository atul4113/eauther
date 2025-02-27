from src.lorepo.spaces.models import Space


# needed when tested function is decorated by @backend
class RequestMock(object):
    def __init__(self):
        self.META = {
            'SERVER_SOFTWARE': 'Development'
        }


class SpacePropertiesMock(object):
    def __init__(self, valid_until):
        self.valid_until = valid_until


def create_space_mock(pk, title, valid_until, users, is_blocked, is_test):
    created_mock = Space()

    created_mock.properties = SpacePropertiesMock(valid_until)
    created_mock.is_blocked = is_blocked
    created_mock.users_count = len(users)
    created_mock.id = pk
    created_mock.title = title
    created_mock.users = users
    created_mock.is_test = is_test

    return created_mock
