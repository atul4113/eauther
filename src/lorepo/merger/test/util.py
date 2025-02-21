from xml.dom import minidom
from libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr
from lorepo.support.util import parse_lesson_id
from lorepo.merger.models import ContentMerger
from libraries.utility.test_assertions import the

class ContentMergerTests(FormattedOutputTestCase):
    lessonA_main_src = "<?xml version='1.0' encoding='UTF-8' ?><interactiveContent name='Lesson A' scoreType='last'><metadata></metadata><addons></addons><pages><page id='NVLAzJ' name='Page Zero 1' href='6342292306657280' preview='' reportable='true'/><page id='RXcFWc' name='Page Zero 2' href='4934917423104000' preview='' reportable='true'/><chapter name='A'><page id='ABdyoE' name='Page A1' href='6060817329946624' preview='' reportable='true'/><chapter name='E'><page id='GyEGjd' name='Page E1' href='5497867376525312' preview='' reportable='true'/></chapter></chapter><chapter name='B'><page id='GLzXic' name='Page B1' href='6623767283367936' preview='' reportable='true'/></chapter><chapter name='C'><page id='Zpp3dY' name='Page C1' href='4583073702215680' preview='' reportable='true'/></chapter><folder name='commons'><page id='Diph3A' name='Common A1' href='5849711097413632' preview='' reportable='true'/><page id='hyBwwW' name='Common A2' href='5286761143992320' preview='' reportable='true'/><page id='MGPnoG' name='header' href='5005286167281664' preview='' reportable='false'/><page id='cYBrQK' name='footer' href='6131186074124288' preview='' reportable='false'/></folder><header ref='commons/header'/><footer ref='commons/footer'/></pages><assets></assets></interactiveContent>"
    lessonB_main_src = "<?xml version='1.0' encoding='UTF-8' ?><interactiveContent name='Lesson B' scoreType='last'><metadata></metadata><addons></addons><pages><page id='Huac9U' name='Page Zero 1' href='6271923562479616' preview='' reportable='true'/><chapter name='A'><page id='XGRRTt' name='Page AAA' href='4864548678926336' preview='' reportable='true'/><chapter name='E'><page id='DQ0C7G' name='Page EEE' href='5990448585768960' preview='' reportable='true'/><page id='u3SMrS' name='Page E1' href='5427498632347648' preview='' reportable='true'/></chapter></chapter><chapter name='B'><page id='ctvuiA' name='Page B1' href='6553398539190272' preview='' reportable='true'/></chapter><chapter name='G'><page id='FB8Yg0' name='Page G1' href='4723811190571008' preview='' reportable='true'/></chapter><folder name='commons'><page id='T4v98J' name='Commons B1' href='5568236120702976' preview='' reportable='true'/><page id='lwF5U9' name='header' href='6694136027545600' preview='' reportable='false'/></folder><header ref='commons/header'/><footer ref='commons/footer'/></pages><assets></assets></interactiveContent>"

    def setUp(self):
        self.A_root = minidom.parseString(self.lessonA_main_src)
        self.B_root = minidom.parseString(self.lessonB_main_src)
        self.A_pages = self.A_root.getElementsByTagName("pages")[0]
        self.B_pages = self.B_root.getElementsByTagName("pages")[0]
        self.A_chapter_A = self.A_pages.getElementsByTagName("chapter")[0]
        self.B_chapter_A = self.B_pages.getElementsByTagName("chapter")[0]
        self.chapters_combined_str = '<chapter name="A"><page href="6060817329946624" id="ABdyoE" name="Page A1" preview="" reportable="true"/><chapter name="E"><page href="5497867376525312" id="GyEGjd" name="Page E1" preview="" reportable="true"/></chapter><page href="4864548678926336" id="XGRRTt" name="Page AAA" preview="" reportable="true"/><chapter name="E"><page href="5990448585768960" id="DQ0C7G" name="Page EEE" preview="" reportable="true"/><page href="5427498632347648" id="u3SMrS" name="Page E1" preview="" reportable="true"/></chapter></chapter>'
        self.duplicate_chapters_fixed_str = '<chapter name="A"><page href="6060817329946624" id="ABdyoE" name="Page A1" preview="" reportable="true"/><chapter name="E"><page href="5497867376525312" id="GyEGjd" name="Page E1" preview="" reportable="true"/><page href="5990448585768960" id="DQ0C7G" name="Page EEE" preview="" reportable="true"/><page href="5427498632347648" id="u3SMrS" name="Page E1" preview="" reportable="true"/></chapter><page href="4864548678926336" id="XGRRTt" name="Page AAA" preview="" reportable="true"/></chapter>'
        self.page_names_fixed_str = '<chapter name="A"><page href="6060817329946624" id="ABdyoE" name="Page A1" preview="" reportable="true"/><chapter name="E"><page href="5497867376525312" id="GyEGjd" name="Page E1" preview="" reportable="true"/><page href="5990448585768960" id="DQ0C7G" name="Page EEE" preview="" reportable="true"/><page href="5427498632347648" id="u3SMrS" name="Page E1 (1)" preview="" reportable="true"/></chapter><page href="4864548678926336" id="XGRRTt" name="Page AAA" preview="" reportable="true"/></chapter>'
        self.empty_chapters_str = '<chapter name="A"><chapter name="E"><chapter name="H"/></chapter><chapter name="G"></chapter><chapter name="B"><page href="4864548678926336" id="XGRRTt" name="Page AAA" preview="" reportable="true"/></chapter></chapter>'
        self.empty_chapters_fixed_str = '<chapter name="A"><chapter name="B"><page href="4864548678926336" id="XGRRTt" name="Page AAA" preview="" reportable="true"/></chapter></chapter>'

    @attr('unit')
    def test_combine_chapters(self):
        ContentMerger._combine_chapters(self.A_chapter_A, self.B_chapter_A)
        the(self.chapters_combined_str).equals(self.A_chapter_A.toxml())

    @attr('unit')
    def test_fix_duplicate_chapters(self):
        chapters_combined_node = minidom.parseString(self.chapters_combined_str)
        dup_chapters_node = minidom.parseString(self.duplicate_chapters_fixed_str)
        ContentMerger._fix_duplicate_chapters(chapters_combined_node)
        the(dup_chapters_node.toxml()).equals(chapters_combined_node.toxml())

    @attr('unit')
    def test_fix_page_names(self):
        dup_chapters_node = minidom.parseString(self.duplicate_chapters_fixed_str)
        ContentMerger._fix_page_names(dup_chapters_node)
        the(minidom.parseString(self.page_names_fixed_str).toxml()).equals(dup_chapters_node.toxml())

    @attr('unit')
    def test_remove_empty_chapters(self):
        empty_chapters_node = minidom.parseString(self.empty_chapters_str)
        empty_chapters_fixed_node = minidom.parseString(self.empty_chapters_fixed_str)
        ContentMerger._remove_empty_chapters(empty_chapters_node)
        the(empty_chapters_fixed_node.toxml()).equals(empty_chapters_node.toxml())

