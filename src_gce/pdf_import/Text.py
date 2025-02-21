import operator

from addons import *
from alphabet_detector import AlphabetDetector

from pdf_import.models import TSpanModel


class CSS:
    exists = {}
    index = 0
    mnemonic = {"color": "c",
                "font-size": "fs",
                "font-family": "ff",
                "font-variant": "fv",
                "font-weight": "fw",
                "font-stretch": "fs",
                "stroke": "s"}  # list with short css class short name

    def __init__(self, xml):
        self.css_dict = {}
        self.rtl = False
        if 'style' in xml.attrib:
            self.set_css(xml)
        for tspan in xml.iter('{http://www.w3.org/2000/svg}tspan'):
            if 'style' in tspan.attrib:
                self.set_css(tspan)

    def set_css(self, xml_element):
        css_text = xml_element.attrib['style'].replace('fill:#', 'color:#')
        css_text = css_text.replace("{", "").replace('fill:#', 'color:#').replace("}", "").split(";")
        for element in css_text:
            css_value = element.split(":")
            self.css_dict[css_value[0]] = css_value[1]
            if not (css_value[0] + css_value[1]) in CSS.exists:
                CSS.exists[css_value[0] + css_value[1]] = str(CSS.index)
                CSS.index += 1

    def get_font_height(self):
        return float(self.css_dict["font-size"][:len(self.css_dict["font-size"]) - 2])

    def equal(self, css):
        if css.generateText() == self.generateHash():
            return True
        return False

    def generateHash(self):  # generate unique hash
        hash = 0
        if "font-weight" not in self.css_dict:
            self.css_dict["font-weight"] = str(0)
            CSS.exists["font-weight0"] = str(CSS.index)
            CSS.index += 1
        if "color" not in self.css_dict:
            self.css_dict["color"] = str("black")
            CSS.exists["colorblack"] = str(CSS.index)
            CSS.index += 1
        for char in self.css_dict["font-size"] + self.css_dict["color"]:
            hash = 31 * hash + ord(char)
        return str(hash)

    def get_formatted_css(self):
        css_text = []
        for css_element in self.css_dict:
            class_name = "a"
            if css_element in self.mnemonic:
                class_name = self.mnemonic[css_element]
            css_text.append(
                "." + class_name + CSS.exists[css_element + self.css_dict[css_element]] + "{" + css_element + ":" +
                self.css_dict[css_element] + ";}")
        return css_text

    def set_rtl(self, text):  # set css to right to left
        if self.rtl:
            return

        if self.is_rtl(text):
            self.rtl = True
        else:
            self.rtl = False

    def get_rtl(self):
        return self.rtl

    def is_rtl(self, text):
        if (AlphabetDetector().is_arabic(text.encode('utf-8').decode('utf-8')) \
                or AlphabetDetector().is_hebrew(text.encode('utf-8').decode('utf-8'))) \
                and not AlphabetDetector().is_latin(text.encode('utf-8').decode('utf-8')):
            return True
        else:
            return False

    def get_css_classes(self):  # css class name with spaces
        css_text = ""
        for css_element in self.css_dict:
            class_name = "a"
            if css_element in self.mnemonic:
                class_name = self.mnemonic[css_element]
            css_text += (class_name + CSS.exists[css_element + self.css_dict[css_element]] + " ")
        if self.rtl:
            css_text += "ralign "
            css_text += "rtl "
        return css_text


class Line:
    template = """ <textModule id='%(id)s' left='%(left)d' top='%(top)d' width='%(width)d' height='%(height)d' right='0'
                        bottom='0' isVisible='true' isLocked='false'
                        isModuleVisibleInEditor='true' class='%(css_class)s'>
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

    unique_id = 0

    def __init__(self, css, page_size):
        self.text = ""
        self.page_width = page_size[0]
        self.page_height = page_size[1]
        self.css = css
        self.id = Line.unique_id
        Line.unique_id += 1
        self.height = css.get_font_height()
        self.width = 1000
        self.css_class = self.css.get_css_classes()
        self.x_list = []

    def get_x_list(self):
        return self.x_list

    def get_x_position(self):
        return self.x_list[0]

    def get_y(self):
        return self.y_list[0]

    def get_y_list(self):
        return self.y_list

    def get_css(self):
        return self.css

    def get_text(self):
        return self.text

    def get_css_hash(self):
        return self.css.generateHash()

    def get_char_at(self, position):
        return self.text[position]

    @staticmethod
    def is_ascii(string_value):
        return all(ord(c) < 128 for c in string_value)

    def add_text(self, text, x_list, y):  # add new text to existing
        for other_x_position in range(0, min(len(x_list), len(text))):
            added = False
            for self_x_position in range(0, min(len(self.x_list), len(self.text))):
                if x_list[other_x_position] < self.x_list[self_x_position]:
                    self.text = self.text[:self_x_position ] + text[other_x_position] + self.text[
                                                                                               self_x_position:]
                    self.y_list.insert(self_x_position, y)
                    self.x_list.insert(self_x_position, x_list[other_x_position])
                    added = True
                    break
            if not added:
                self.text = self.text[:len(self.x_list)] + text[other_x_position] + self.text[
                                                                                            len(self.x_list):]
                self.x_list.insert(len(self.x_list), x_list[other_x_position])
                self.y_list.insert(len(self.x_list), y)

    def set_text(self, text, y):
        self.text = text
        self.y_list = [y] * len(text)

    def set_x_list(self, x_list):
        self.x_list = x_list

    def to_xml(self):
        self.left = self.x_list[0]
        self.top = self.get_y() - int(self.css.get_font_height())
        self.width = self.get_width()
        buff = self.text
        if self.css.get_rtl():
            if (AlphabetDetector().is_arabic(self.text.encode('utf-8').decode('utf-8'))
                or AlphabetDetector().is_hebrew(self.text.encode('utf-8').decode('utf-8')))\
                    and not AlphabetDetector().is_latin(self.text.encode('utf-8').decode('utf-8')):
                buff = self.__reflect_text(self.text)
        self.text_xml = "<div>" + buff + "<br\\></div>"
        return self.template % self.__dict__

    def get_formatted_text(self):
        text = self.text
        if self.css.get_rtl():
            if (AlphabetDetector().is_arabic(self.text.encode('utf-8').decode('utf-8'))
                or AlphabetDetector().is_hebrew(self.text.encode('utf-8').decode('utf-8')))\
                    and not AlphabetDetector().is_latin(self.text.encode('utf-8').decode('utf-8')):
                text = self.__reflect_text(self.text)
        return text

    def get_width(self):
        return round((np.ceil(float(self.x_list[-1] - self.x_list[0])))) + int(self.css.get_font_height() / 1.8)

    def __reflect_text(self, text):
        map, keys = self.__get_latin_map(text)
        map = map[::-1]     # reflect map, now mark is written as: "}nital{"
        return self.__recover_map(map, keys)

    def __get_latin_map(self, text):
        new_text = []
        keys = []
        key = []

        start = False

        for index, char in enumerate(text):
            if AlphabetDetector().is_latin(char.encode('utf-8').decode('utf-8')):
                if not start:
                    start = True
                    new_text.append("{latin}")
                key.append(char)

            else:
                if start:
                    start = False
                    keys.append(u"".join(key))
                    key = []

                new_text.append(char)
        if start:
            keys.append(u"".join(key))

        return u"".join(new_text), keys

    def __recover_map(self, text_map, keys):
        def replace_marker(match):
            value = keys[replace_marker.index]
            replace_marker.index -= 1
            return value

        replace_marker.index = len(keys) - 1
        pattern = "(}nital{)"
        return re.sub(pattern, replace_marker, text_map)


class LineList:
    PERCENT_TO_CONNECT_ARABIC = 15  # how many percent to connect two neraby lines(y)
    PERCENT_TO_CONNECT_OTHER = 0  # how many percent to connect two neraby lines(y)

    def __init__(self, page_size):
        self.page_size = page_size
        self.line_list = []
        self.iter_index = 0

    def get_lines_sorted_by_y(self):
        return sorted(self.line_list, key=operator.methodcaller('get_y'))

    def add_line(self, text_element):
        css = CSS(text_element)

        for tspan_element in text_element.iter('{http://www.w3.org/2000/svg}tspan'):
            tspan_model = TSpanModel(tspan_element)
            if not tspan_model.is_valid():
                continue

            tspan_model.complete_model(self.page_size, text_element)
            css.set_rtl(tspan_model.get_text())

            percent = 0
            percent_changed = False
            if not AlphabetDetector().is_latin(tspan_element.text.encode('utf-8').decode('utf-8')):
                if AlphabetDetector().is_arabic(tspan_element.text.encode('utf-8').decode('utf-8')):
                    percent = ((css.get_font_height() * self.PERCENT_TO_CONNECT_ARABIC) / 100.)  # calculate percent for arabic text
                    percent_changed = True
            if not percent_changed:
                percent = (
                (css.get_font_height() * self.PERCENT_TO_CONNECT_OTHER) / 100.)  # calculate percent for non arabic text
            added = False
            for line in self.line_list:
                if line.get_y() + percent >= tspan_model.calculated_y >= line.get_y() - percent:  # check for existing line with the same y
                    if line.get_css_hash() == css.generateHash():
                        line.add_text(tspan_element.text, tspan_model.calculated_chars_x_list, tspan_model.calculated_y)  # add text to existing line
                        line.get_css().set_rtl(line.get_text())
                        added = True
                        break
            if not added:
                newLine = Line(css, self.page_size)
                newLine.set_text(tspan_element.text, tspan_model.calculated_y)  # add new line
                newLine.set_x_list(tspan_model.calculated_chars_x_list)
                self.line_list.append(newLine)

    def __separate(self, x_list, font_size):  # cut one line to many
        delta_x = []
        for iter in range(1, len(x_list)):
            delta_x.append(abs(x_list[iter] - x_list[iter-1]))
        cut_pos = []
        for iter in range(0, len(delta_x)):
            if delta_x[iter] >= font_size * 2:
                cut_pos.append(iter + 1)
        return cut_pos

    def cut_and_connect_lines(self):
        new_line_list = []
        for line in self.line_list:
            x_list = [line.get_x_list()]
            cut_pos = self.__separate(x_list[0], line.get_css().get_font_height())
            last_pos = 0
            for position in cut_pos:
                new_line = Line(line.get_css(), self.page_size)
                new_line.set_x_list(line.get_x_list()[last_pos:position])
                if position >= len(line.get_text()):
                    continue
                new_line.set_text(line.get_text()[last_pos:position], line.get_y_list()[position])
                new_line_list.append(new_line)
                last_pos = position
            new_line = Line(line.get_css(), self.page_size)
            new_line.set_x_list(line.get_x_list()[last_pos:])
            new_line.set_text(line.get_text()[last_pos:], line.get_y_list()[last_pos])
            new_line_list.append(new_line)
        self.line_list = new_line_list

    def write_lines(self):
        for element in self.line_list:
            element.write_text()

    def get_line_list(self):
        return self.line_list

