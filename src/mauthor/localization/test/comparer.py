from libraries.utility.noseplugins import FormattedOutputTestCase
from mauthor.localization.models import Page, Comparer, Module, Field,\
    Difference, DifferenceType
from nose.plugins.attrib import attr

class Lesson(object):
    def __init__(self, title):
        self.title = title

class ComparerTests(FormattedOutputTestCase):

    def setUp(self):
        self.moduleX_fields = [
            Field('test1', 'test1', 'string', 'test', 0),
            Field('test2', 'test1', 'string', 'test', 1)
        ]
        
        self.moduleY_fields = [
            Field('test1', 'test1', 'string', 'test', 0)
        ]
        
        self.pageX_modules = [
            Module('Text1'),
            Module('Text2')
        ]
        
        self.pageX_modules[0].fields.extend(self.moduleX_fields)
        
        self.pageY_modules = [
            Module('Text1')
        ]
        
        self.pageY_modules[0].fields.extend(self.moduleY_fields)
        
        self.pagesX = [
            Page(name='Test1', page_id='abc123'),
            Page(name='Test2', page_id='cde456'),
            Page(name='Test3', page_id='fgh789')
        ]
        
        self.pagesX[0].modules.extend(self.pageX_modules)

        self.pagesY = [
            Page(name='Testowa1', page_id='abc123'),
            Page(name='Testowa2', page_id='cde456')
        ]
        
        self.pagesY[0].modules.extend(self.pageY_modules)

        self.lessonX = Lesson('Original Lesson')
        self.lessonY = Lesson('Localized Lesson')

    @attr('unit')
    def test_page_exists_positive(self):
        searching_page = Page(name='Test', page_id='abc123')
        
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        result = comparer.get_page(searching_page)
        
        self.assertTrue(result != None)

    @attr('unit')
    def test_page_exists_negative(self):
        searching_page = Page(name='Test', page_id='fgh789')
        
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        result = comparer.get_page(searching_page)
        
        self.assertTrue(result == None)

    @attr('unit')
    def test_compare_pages_no_differences(self):
        self.pagesY.append(Page(name='Testowa3', page_id='fgh789'))
        
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        comparer.compare()
        messages = [diff.msg for diff in comparer.differences]
        
        self.assertFalse('Page with name Test3 was NOT found in lesson Localized Lesson.' in messages)

    @attr('unit')
    def test_compare_pages_with_differences(self):
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        comparer.compare()
        messages = [diff.msg for diff in comparer.differences]
        
        self.assertTrue('Page with name Test3 was NOT found in lesson Localized Lesson.' in messages)

    @attr('unit')
    def test_module_exists_positive(self):
        searching_module = Module('Text1')
        
        result = self.pagesY[0].get_module(searching_module)
        
        self.assertTrue(result != None)

    @attr('unit')
    def test_module_exists_negative(self):
        searching_module = Module('Text2')
        
        result = self.pagesY[0].get_module(searching_module)
        
        self.assertTrue(result == None)

    @attr('unit')
    def test_compare_all_has_differences(self):
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        comparer.compare()
        
        self.assertEqual(3, len(comparer.differences))

    @attr('unit')
    def test_compare_all_has_no_differences(self):
        self.pagesY.append(Page(name='Testowa3', page_id='fgh789'))
        self.pagesY[0].modules.append(Module('Text2'))
        self.pagesY[0].modules[0].fields.append(Field('test2', 'test1', 'string', 'test', 1))
        
        comparer = Comparer(self.lessonX, self.pagesX, self.lessonY, self.pagesY)
        
        comparer.compare()
        
        self.assertEqual(0, len(comparer.differences))
        self.assertEqual([], comparer.differences)

    @attr('unit')
    def test_difference_type_page_missing(self):
        diff = Difference('test', self.pagesX[0], None, None)
        
        self.assertEqual(DifferenceType.PAGE_MISSING, diff.get_type())

    @attr('unit')
    def test_difference_type_module_missing(self):
        diff = Difference('test', self.pagesX[0], self.pagesX[0].modules[0], None)
        
        self.assertEqual(DifferenceType.MODULE_MISSING, diff.get_type())

    @attr('unit')
    def test_difference_type_field_missing(self):
        diff = Difference('test', self.pagesX[0], self.pagesX[0].modules[0], self.pagesX[0].modules[0].fields[0])
        
        self.assertEqual(DifferenceType.FIELD_MISSING, diff.get_type())