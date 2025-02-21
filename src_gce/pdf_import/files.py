from lxml import etree as ET
import re
import hashlib
import base64
from subprocess import call
from os import path


class ImageRepo:

    image_reg = r'xlink:href="data:image/png;base64,(?P<image_source>[A-Za-z0-9+/-=]*)"'
    temp_svg_name = 'temp_svg.xml'

    def __init__(self):
        self.image_repo = {}

    def repl(self, m, temp_path):
        dig = hashlib.md5()
        image_source = m.group('image_source')
        dig.update(image_source)
        short = str(int(dig.hexdigest(),16))
        if short not in self.image_repo:
            image_path = temp_path + 'resources/'+short+'.png'
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_source))
        else:
            image_path = self.image_repo[short]
        return 'xlink:href="%s"'%('./resources/'+short+'.png')

    def parse_file(self, svg_file, path):
        reg = re.compile(self.image_reg)
        with open(path + self.temp_svg_name, 'w') as fout:
            try:
                with open(svg_file) as fin:
                    fout.write(reg.sub(lambda m: self.repl(m, path), fin.read()))
            except IOError:
                return None

        return path + self.temp_svg_name


class MetadataFile(object):
    template = """<?xml version="1.0" encoding="utf-8"?>
<metadata content_type="1" description="" enable_page_metadata="False" icon_href="../resources/1.png" id="1" short_description="" tags="" title="%(title)s">
	<resources>
	</resources>
	<addons/>
</metadata>
"""
    resource_template = """<resource content_type="%(mime)s" filename="resources/%(image_name)s"/>"""

    def __init__(self, presentation_name):
        self.title = presentation_name
        self.root = ET.fromstring(self.template%self.__dict__)
        self.resource_node = self.root[0]
        self.href = 'metadata.xml'

    def create_icon(self, icon_path, page_name, size):
        #inkscape -z -e test.png -w 1024 -h 1024 test.svg
        call(['inkscape',
              '--without-gui',
              '--export-png=' + icon_path + 'resources/1.png' ,
              '--export-width='+str(size[0]/4),
              '--export-height='+str(size[1]/4),
              '--file='+ page_name])
        res_str = self.resource_template%{'image_name': '1.png', 'mime':'image/png'}
        self.resource_node.append(ET.fromstring(res_str))

    def add_resource(self, image):
        xml_string = self.resource_template % image.__dict__
        self.resource_node.append(ET.fromstring(xml_string))

    def to_xml(self):
        return ET.tostring(self.root, pretty_print=True)


class MainFile(object):
    template = """<?xml version="1.0" encoding="utf-8"?>
            <interactiveContent name="%(title)s" scoreType="last">
                <metadata>
                    <entry key="useGrid" value="false"/>
                    <entry key="snapToGrid" value="true"/>
                    <entry key="gridSize" value="25"/>
                    <entry key="staticHeader" value="true"/>
                    <entry key="staticFooter" value="false"/>
                    <entry key="useRulers" value="true"/>
                    <entry key="snapToRulers" value="true"/>
                </metadata>
                <addons>
                </addons>
                <style>
                .ic_navi_panel_prev, .ic_navi_panel_next, .ic_navi_panel_bar
                {
                    display: block;
                }

                </style>
                <pages>
                </pages>
                <assets>
                </assets>
            </interactiveContent>
    """

    asset_template = """ <asset contentType="%(mime)s" fileName="%(image_name)s" href="../resources/%(image_name)s" title="" type="image"/>"""
    main_node_template = """<page href="%(href)s" id="%(unique_id)s" modulesMaxScore="0" name="%(title)s" pageWeight="1" reportable="false"/>"""


    def __init__(self, pdfname):
        self.title = pdfname
        self.root = ET.fromstring(self.template%self.__dict__)
        self.pages_node = self.root[3]
        self.asset_node = self.root[4]
        self.style_node = self.root[2]
        self.href = 'main.xml'

    def add_page(self, page):
        xml_string = self.main_node_template % page.__dict__
        self.pages_node.append(ET.fromstring(xml_string))

    def add_asset(self, image):
        xml_string = self.asset_template % image.__dict__
        self.asset_node.append(ET.fromstring(xml_string))

    def add_styles(self, styles):
        for element in styles:
            self.style_node.text += element

    def to_xml(self):
        return ET.tostring(self.root, pretty_print=True)


class PageFile(object):

    page_xml = """<?xml version='1.0' encoding='UTF-8'?>
                    <page layout='pixels' name='%(title)s' isReportable='false' scoring='percentage' width='%(width)d' height='%(height)d' version='2'>
                    <modules>
                    </modules>
                    <groups/>
                    <page-weight value='1' mode='defaultWeight'></page-weight>
                    </page>
                    """
    # node formatting: page_name, unique_id (six letters), title
    # xml: width, height, modules

    def __init__(self, xml, page_id):
        self.title = str(page_id)
        self.unique_id = '%06d'%(page_id)
        #extract page size
        if not xml:
            self.width = 400
            self.height = 400
        else:
            self.width = int(round(float(xml.attrib['width'])))
            self.height = int(round(float(xml.attrib['height'])))

        self.page_size = (self.width, self.height)
        self.image_modules = []
        self.text_modules = []
        self.href = self.title+'.xml'

    def add_image(self, image):
        self.image_modules.append(image)

    def add_text(self, text):
        self.text_modules.append(text)
    def to_xml(self):
        xml_string = self.page_xml%self.__dict__
        root_node = ET.fromstring(xml_string)
        modules_node = root_node[0]
        for image in self.image_modules:
            modules_node.append(ET.fromstring(image.to_xml()))
        for text in self.text_modules:
            modules_node.append(ET.fromstring(text.to_xml()))
        return ET.tostring(root_node, pretty_print=True)

