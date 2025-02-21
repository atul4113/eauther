import logging

import operator

from pdf_import.addons import Calculator


class CSSToRichTextParser(object):
    def __init__(self):
        pass

    @classmethod
    def parse(cls, css_dict):
        parsers = [
            cls.parse_text_color
        ]
        element = "%s"
        for parser in parsers:
            element %= parser(css_dict)
        return element

    @classmethod
    def parse_text_color(cls, css_dict):
        font = "<font "
        color = css_dict.get('color')
        if color:
            font += "color='%s' " % color
        size = css_dict.get('font-size').replace("px", "").split('.')[0]
        if size:
            font += "size='%s' " % cls.__get_font_size_from_px(int(size))

        face = css_dict.get('font-family')
        if face:
            font += "face='%s' " % face

        font += ">%s</font>"
        return font

    @classmethod
    def __get_font_size_from_px(cls, px):
        if px >= 40:
            return 7
        elif 27 <= px < 40:
            return 6
        elif 20 <= px < 27:
            return 5
        elif 17 <= px < 20:
            return 4
        elif 14 <= px < 17:
            return 3
        elif 12 <= px < 14:
            return 2
        else:
            return 1

class TSpanModel(object):
    def __init__(self, xml_element):
        self.tspan_xml = xml_element
        self.text = xml_element.text
        self.y = 0
        self.calculated_y = 0
        self.chars_x_list = []
        self.calculated_chars_x_list = []


    def is_valid(self):
        if self.text is None:
            return False
        return True

    def get_text(self):
        return self.text

    def complete_model(self, page_size, text_xml_element):
        self.y = ([float(y) for y in self.tspan_xml.get('y').split()])[0]
        self.chars_x_list = ([float(x) for x in self.tspan_xml.get('x').split()])
        for x in self.chars_x_list:
            calculated_x, self.calculated_y, width, height = Calculator().calculate(x, self.y, text_xml_element, page_size)
            self.calculated_chars_x_list.append(calculated_x)


class Paragraph(object):
    template = """ <textModule id='%(id)s' left='%(left)d' top='%(top)d' width='%(width)d' height='%(height)d' right='0'
                        bottom='0' isVisible='true' isLocked='false'
                        isModuleVisibleInEditor='true'>
            <layout type='LTWH'>
                <left relative='' property='left'/>
                <top relative='' property='top'/>
                <right relative='' property='right'/>
                <bottom relative='' property='bottom'/>
            </layout>
            <text draggable='false' math='false' gapMaxLength='0' gapWidth='80' isActivity='true'
                  isIgnorePunctuation='false' isKeepOriginalOrder='false' isClearPlaceholderOnFocus='false'
                  isDisabled='false' isCaseSensitive='false' openLinksinNewTab='true' valueType='All'
                  blockWrongAnswers='false' userActionEvents='false'><![CDATA[%(text_xml)s]]></text>
        </textModule> """

    line_template = """<div style='text-align: %s;'>%s</div>"""

    MAX_GAP_BETWEEN_LINES = 2       # font * MAX_GAP_BETWEEN_LINES

    def __init__(self, line):
        self.lines = [[line]]
        self.font_size = line.get_css().get_font_height()
        self.left = 0
        self.height = 0
        self.width = self.__calculate_line_width(self.lines[0]) * 1.5
        self.__check_left_position(self.lines[0])
        self.text_xml = ""
        self.top = line.get_y() - int(line.css.get_font_height())
        self.id = line.id

    def to_xml(self):
        self.text_xml = ""
        self.__sort_lines_by_x()

        for line in self.lines:
            self.text_xml += self.line_template % (self.get_text_position(line), self.__build_line(line))

        self.height = len(self.lines) * self.font_size
        return self.template % self.__dict__

    def __sort_lines_by_x(self):
        new_lines = []
        for line in self.lines:
            new_lines.append(sorted(line, key=operator.methodcaller('get_x_position')))

        self.lines = new_lines

    def __check_left_position(self, line):
        if line[0].css.get_rtl():
            self.__check_rtl_left_position(line)
        else:
            self.left = line[0].get_x_position()

    def __check_rtl_left_position(self, line):
        last_line_element = line[-1]
        module_right_position = last_line_element.x_list[-1]
        self.left = module_right_position - self.width


    def get_text_position(self, line):
        for element in line:
            if element.css.get_rtl():
                return "right"
        return "left"

    def __build_line(self, line):
        text_line = ""
        for line_element in line:
            text_line += CSSToRichTextParser.parse(line_element.css.css_dict) % line_element.get_formatted_text()

        return text_line

    def __calculate_line_width(self, line):
        calc_width = 0
        for element in line:
            calc_width += element.get_width()
        return calc_width

    def is_in_paragraph(self, line):
        validators = [
            self.__check_y_position,
            self.__check_x_position,
            self.__check_css
        ]

        for validator in validators:
            if not validator(line):
                return False
        return True

    def add_to_paragraph(self, line_to_add):

        for line in self.lines:
            if self.__line_position_on_second_line(line[0], line_to_add):
                line.append(line_to_add)
                if self.__calculate_line_width(line) > self.width:
                    self.width = self.__calculate_line_width(line)
                    self.__check_left_position(line)
                return
        self.lines.append([line_to_add])

        if self.__calculate_line_width([line_to_add]) > self.width:
            self.width = self.__calculate_line_width([line_to_add])
            self.__check_left_position([line_to_add])

    def __check_y_position(self, line_to_add):
        for line in self.lines:
            if self.__check_line_y_position(line[0], line_to_add):
                return True
        return False

    def __line_position_on_second_line(self, line_element, line_to_add):
        delta = line_to_add.get_y() - line_to_add.css.get_font_height() - line_element.get_y()

        if delta <= 0:
            return True
        return False

    def __check_line_y_position(self, line, line_to_add):
        delta = abs(line_to_add.get_y() - line.get_y())

        if delta > self.font_size * Paragraph.MAX_GAP_BETWEEN_LINES:
            return False
        return True

    def __check_x_position(self, line_to_add):
        self.__sort_lines_by_x()

        for line in self.lines:
            if line_to_add.css.get_rtl():
                self_position = self.__get_last_x_position(line)
                line_to_add_index = len(line_to_add.x_list) - 1
            else:
                self_position = line[0].x_list[0]
                line_to_add_index = 0

            delta = abs(self_position - line_to_add.x_list[line_to_add_index])
            if delta < int(line_to_add.css.get_font_height() * 2):
                return True
        return False

    def __get_last_x_position(self, lines_elements):
        x_position = 0
        for line in lines_elements:
            x_position = max([x_position, max(line.x_list)])

        return x_position

    def __check_css(self, line_to_add):
        return line_to_add.css.get_rtl() == self.lines[0][0].css.get_rtl()