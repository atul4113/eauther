from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.course.models import Course
from src.lorepo.course.scorm import create_manifest
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.exchange.models import ExportVersions
from src.nose.plugins.attrib import attr

class ScormTests(FormattedOutputTestCase):
    def setUp(self):
        self.test_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <course id="5735052650479616" name="Course 1">
            <chapters>
                <chapter chapter-id="1" name="Chapter 1">
                    <chapter chapter-id="2" name="SubChapter 1">
                        <lessons><lesson lesson-id="4538783999459328" name="Lesson 1" url="http://www.mauthor.com/file/serve/4890627720347648" version="1"/></lessons>
                    </chapter>
                </chapter>
                <chapter chapter-id="3" name="Chapter 2">
                    <chapter chapter-id="4" name="SubChapter 2">
                        <lessons><lesson lesson-id="5383208929591296" name="Lesson 2" url="http://www.mauthor.com/file/serve/6579477580611584" version="1"/></lessons>
                    </chapter>
                </chapter>
            </chapters>
            <ebooks><ebook ebook-id="4960996464525312" name="Ebook 1" url="http://www.mauthor.com/file/serve/5312840185413632" version="1"/></ebooks>
        </course>'''

    @attr('unit')
    def _build_manifest(self):
        course = Course()
        course.id = 5
        course.name = "Course 1"
        structure = FileStorage()
        structure.contents = self.test_xml
        course.structure_xml = structure
        manifest = create_manifest(course, ExportVersions.SCORM_2004.type)
