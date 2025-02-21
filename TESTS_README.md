## Executing tests
To run tests on mcourser you should execute run_tests.py script. The script will check installed dependencies and will run pytest with provided parameters. For example: 

`python run_tests.py -v --pdb`

There is additional option --fast_run which speed up recreating and creating database by django. It should be used only in development.

`python run_tests.py --fast_run`

### Requirements

run_tests script requires correctly configured `build.properties` file and correctly configured sys path to pip program.

Example `build.properties` file:

    modules=download,translations,ecommerce
    flex-modules=gce-backend
    appcfg.path=C:/GAE/appcfg.py
    appcfg.refresh.token=<token>
    
### Remarks
 * The script wasn't checked on Linux
 * The script wasn't checked on virtual environment

## Writing tests
### Base Class
Each group of tests should inherit from one from two available TestCases:
 1. ```from mcurriculum.tests.TestCase import TestCase```:  Test case which don't need a connection to database. Tests which inherit from this class should not use database. This class will run tests faster than DBTestCase.
 2. ```from mcurriculum.tests.TestCase import DBTestCase```:  Test case which for each test will clear database. Use this test case if you need connection to database.

If you need to configure something for each test then add setUp method to your class and call super. This method will be called for each test

        def setUp(self):
            super(MyTestClass, self).setUp()
            ...Initialization
### Requests
For making request to endpoints use ```APIClient``` class. This class contain possibility to creating request with data to provided URL.

Example:

        class TestsAssignmentCreation(AuthorizationTestMixin, EcommerceAssignAccessMixin, DBTestCase):
            def test_my_super_test(self):
                teacher_client = self.login_in_as(self.teacher) # Returns configured APIClient object
                response = teacher_client.post(self.CREATE_ASSIGNMENT_URL, self.init_data, format='json')
        
### Mixins
While writing tests you may need some basic functionality like "login as user". These functionality should be available in ```mixins``` directory. While writing tests try to extract useful functionality to mixins if currently these functionality is missing.

Available mixins:
1. authorization.py
    * ```AuthorizationTestMixin``` - functionality for authorize as user. Login method returns configured APIClient object. Examples methods: ```login_in_as(user)```
2. ecommerce.py
    * ```EcommerceAssignAccessMixin``` - functionality for setting access to a course for users of one user. Example methods: ```assign_course_for_user```, ```assign_course_for_users```

###Fixtures
For generating data you should use fixtures. Fixtures are function with ```pytest.fixture``` decorator which returns some data. Fixtures which are available for all tests are in ```fixtures``` directory. If you need to add new fixtures file, add it to ```conftest.py``` file as plugin.
Specific fixtures for one test should be defined in the same file with tests.

Fixtures which generates database objects should be declared as ```function``` scope:

        @pytest.fixture(scope='function')
        def my_super_fixture():
            return User.objects.create()

Pytest contains posibility to execute function for each test. 

        @pytest.fixture(autouse=True)
        def init_codes(self, codes_first_publisher):
            self.codes_details = codes_first_publisher 
            
### Cache problems
If while writing test you will have problem with some cache mechanizm, add fix to ```CacheCleanerMixin``` which should reset cache for each test.


