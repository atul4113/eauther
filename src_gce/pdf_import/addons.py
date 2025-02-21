import re
import numpy as np
import logging
from os import path
import os
from PIL import Image as Imgs
from pdf_import.utils.check_parent import is_in_g_markup


class Calculator():
    matrix_reg = r'matrix\((?P<a>-?\d+(\.\d+)?(e-?\d+)?),(?P<b>-?\d+(\.\d+)?(e-?\d+)?),(?P<c>-?\d+(\.\d+)?(e-?\d+)?),(?P<d>-?\d+(\.\d+)?(e-?\d+)?),(?P<e>-?\d+(\.\d+)?(e-?\d+)?),(?P<f>-?\d+(\.\d+)?(e-?\d+)?)\)'  #https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform                                                                                                                                #http://stackoverflow.com/questions/15977591/parsing-svg-transformation-matrix-decomposition
    translate_reg =  r'translate\((?P<e>-?\d+(\.\d+)?(e-?\d+)?),(?P<f>-?\d+(\.\d+)?(e-?\d+)?)\)'
    scale_reg =  r'scale\((?P<a>-?\d+(\.\d+)?(e-?\d+)?),(?P<d>-?\d+(\.\d+)?(e-?\d+)?)\)'
    start_vector = np.array([0,0,1])
    end_vector = None

    def calculate(self, x, y, xml, page_size):
        self.trans_matrixes = []
        self.start_vector[1] = y
        self.start_vector[0] = x
        try:
            mat1 = self.read_matrix(xml.attrib['transform'])
            v1 = mat1.dot(self.start_vector)
            if self.end_vector is not None:
                v2 = mat1.dot(self.end_vector)
            self.trans_matrixes.append(mat1)
        except KeyError:
            v1 = self.start_vector
            if self.end_vector is not None:
                v2 = self.end_vector
        for p in xml.iterancestors():
            try:
                mat = self.read_matrix(p.attrib['transform'])
                v1 = mat.dot(v1)
                self.trans_matrixes.append(mat)
                if self.end_vector is not None:
                    v2 = mat.dot(v2)
            except KeyError:
                continue

        self.left = int(round(v1[0]))
        self.top = int(round(v1[1]))
        if self.end_vector is not None:
            self.width = int(round(v2[0]))
            self.height = int(round(v2[1]))
            self.scale = 1.0
            if float(v2[0]) == float(v2[1]):
                self.scale = float(v2[0])

        else:
            self.width = page_size[0] - self.left
            self.height = page_size[1] - self.top
        return self.left, self.top, self.width, self.height

    def read_matrix(self, matrix_string):
        match = re.match(self.matrix_reg, matrix_string)
        if match:
            a = float(match.group('a'))
            b = float(match.group('b'))
            c = float(match.group('c'))
            d = float(match.group('d'))
            e = float(match.group('e'))
            f = float(match.group('f'))
        else:
            match = re.match(self.translate_reg, matrix_string)
            if match:
                a = 1
                b = 0
                c = 0
                d = 1
                e = float(match.group('e'))
                f = float(match.group('f'))
            else:
                match = re.match(self.scale_reg, matrix_string)
                if match:
                    a = float(match.group('a'))
                    b = 0
                    c = 0
                    d = float(match.group('d'))
                    e = 0
                    f = 0

        return np.array([[a, c, e],
                         [b, d, f],
                         [0, 0, 1]])

    def absolute_coordinates(self, vector):
        v = vector
        for mat in self.trans_matrixes:
            v = mat.dot(v)
        return v[0], v[1]


class Addon(object):
    matrix_reg = r'matrix\((?P<a>-?\d+(\.\d+)?(e-?\d+)?),(?P<b>-?\d+(\.\d+)?(e-?\d+)?),(?P<c>-?\d+(\.\d+)?(e-?\d+)?),(?P<d>-?\d+(\.\d+)?(e-?\d+)?),(?P<e>-?\d+(\.\d+)?(e-?\d+)?),(?P<f>-?\d+(\.\d+)?(e-?\d+)?)\)'  #https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform                                                                                                                             #http://stackoverflow.com/questions/15977591/parsing-svg-transformation-matrix-decomposition
    translate_reg = r'translate\((?P<e>-?\d+(\.\d+)?(e-?\d+)?),(?P<f>-?\d+(\.\d+)?(e-?\d+)?)\)'
    scale_reg = r'scale\((?P<a>-?\d+(\.\d+)?(e-?\d+)?),(?P<d>-?\d+(\.\d+)?(e-?\d+)?)\)'
    start_vector = np.array([0,0,1])
    end_vector = None

    def __init__(self, xml, page_size):
        self.trans_matrixes = []
        for text_element in xml.iter('{http://www.w3.org/2000/svg}tspan'):
            self.start_vector[1] = ([float(y) for y in text_element.get('y').split()])[0]
            xRow = ([float(x) for x in text_element.get('x').split()])
            self.start_vector[0] = (xRow[0])
            break
        try:
            mat1 = self.read_matrix(xml.attrib['transform'])
            v1 = mat1.dot(self.start_vector)
            if self.end_vector is not None:
                v2 = mat1.dot(self.end_vector)
            self.trans_matrixes.append(mat1)
        except KeyError:
            v1 = self.start_vector
            if self.end_vector is not None:
                v2 = self.end_vector
        for p in xml.iterancestors():
            try:
                mat = self.read_matrix(p.attrib['transform'])
                v1 = mat.dot(v1)
                self.trans_matrixes.append(mat)
                if self.end_vector is not None:
                    v2 = mat.dot(v2)
            except KeyError:
                continue

        self.left = int(round(v1[0]))
        self.top = int(round(v1[1]))
        if self.end_vector is not None:
            self.width = int(round(v2[0]))
            self.height = int(round(v2[1]))
            self.scale = 1.0
            if float(v2[0]) == float(v2[1]):
                self.scale = float(v2[0])

        else:
            self.width = page_size[0] - self.left
            self.height = page_size[1] - self.top


    def read_matrix(self, matrix_string):
        match = re.match(self.matrix_reg, matrix_string)
        if match:
            a = float(match.group('a'))
            b = float(match.group('b'))
            c = float(match.group('c'))
            d = float(match.group('d'))
            e = float(match.group('e'))
            f = float(match.group('f'))
        else:
            match = re.match(self.translate_reg, matrix_string)
            if match:
                a = 1
                b = 0
                c = 0
                d = 1
                e = float(match.group('e'))
                f = float(match.group('f'))
            else:
                match = re.match(self.scale_reg, matrix_string)
                if match:
                    a =  float(match.group('a'))
                    b = 0
                    c = 0
                    d = float(match.group('d'))
                    e = 0
                    f = 0

        return np.array([[a, c, e],
                         [b, d, f],
                         [0, 0, 1]])

    def absolute_coordinates(self, vector):
        v = vector
        for mat in self.trans_matrixes:
            v = mat.dot(v)
        return v[0], v[1]

class ErrorText(Addon):

    template = """ <textModule id='%(id)s' left='%(left)d' top='%(top)d' width='%(width)d' height='%(height)d' right='0' bottom='0' isVisible='true'
                    isLocked='false' isModuleVisibleInEditor='true' class='%(css_class)s'>
            <layout type='LTWH'>
                <left relative='' property='left'/>
                <top relative='' property='top'/>
                <right relative='' property='right'/>
                <bottom relative='' property='bottom'/>
            </layout>
            <text draggable='false' math='false' gapMaxLength='0' gapWidth='80' isActivity='true'
                  isIgnorePunctuation='false' isKeepOriginalOrder='false' isClearPlaceholderOnFocus='false'
                  isDisabled='false' isCaseSensitive='false' openLinksinNewTab='true' valueType='All'
                  blockWrongAnswers='false' userActionEvents='false'><![CDATA[%(text)s]]></text>
        </textModule> """

    def __init__(self, error_msg):
        self.id = "text_error"
        self.left = 150
        self.top = 150
        self.width = 100
        self.height = 100
        self.css_class = 'TextErrorMsg'
        self.text = error_msg

    def to_xml(self):
        return self.template%self.__dict__


class Image(Addon):

    template = """ <imageModule  id='%(id)s' left='%(left)d' top='%(top)d' width='%(width)d' height='%(height)d' right='0' bottom='0' isVisible='true'
                     isLocked='false' isModuleVisibleInEditor='true'>
            <layout type='LTWH'>
                <left relative='' property='left'/>
                <top relative='' property='top'/>
                <right relative='' property='right'/>
                <bottom relative='' property='bottom'/>
            </layout>
            <image src='.%(image_path)s' mode='%(mode)s'/>
        </imageModule>
        """


    end_vector = np.array([1,1,0])

    #formatting: id, left, top, width, height, css_class, image_name
    #other: image_source

    def __init__(self, xml=None, page_id=None, page_size=None, image_name=None, mime = 'image/png'):
        if image_name:
            self.image_name = image_name
            self.image_path = './resources/'+image_name
            self.mode = 'originalSize'
            self.top = 0
            self.left = 0
            self.width = page_size[0]
            self.height = page_size[1]
            self.id = 'image_background_'+image_name
        else:
            super(Image,self).__init__(xml, page_size)    #will calculate position
            self.id = xml.attrib['id']+'_'+str(page_id)
            self.image_path = xml.attrib['{http://www.w3.org/1999/xlink}href']
            self.image_name = path.basename(self.image_path)
            self.mode = 'stretch'
        self.mime = mime

    def to_xml(self):
        return self.template % self.__dict__

    @classmethod
    def set_images_masks(cls, root, temp_path, page_number, page):
        def scale_image(from_image, to_image):
            if from_image.size != to_image.size:
                return from_image.resize(to_image.size, Imgs.ANTIALIAS)
            return from_image

        def set_mask_to_image(mask, image):
            try:
                image.putalpha(mask)
                return image
            except ValueError:
                logging.error("Size: width: %d, height: %d" % mask.size)
                logging.error("Original, Size: width: %d, height: %d" % original.size)
                logging.exception("Mask exception")

        images = []
        images_modules = []
        images_to_delete = []

        for image_element in root.iter('{http://www.w3.org/2000/svg}image'):
            if is_in_g_markup(image_element.getparent()):
                images.append(image_element)
                images_modules.append(Image(image_element, page_number, page.page_size))
                if cls.have_mask(image_element):
                    reg = r"url\(#(.*)\)"
                    mask_id = re.findall(reg, image_element.get("mask"))[0]  # mask of that image
                    for mask_element in root.iter('{http://www.w3.org/2000/svg}mask'):
                        if mask_element.get("id") == mask_id:
                            mask_xml_element = mask_element.find("{http://www.w3.org/2000/svg}image")
                            mask_path = mask_xml_element.get("{http://www.w3.org/1999/xlink}href")
                            original_path = temp_path + image_element.get("{http://www.w3.org/1999/xlink}href")[1:]

                            mask = Imgs.open(temp_path + mask_path[1:])  # open mask
                            original = Imgs.open(original_path)  # open original image
                            mask = scale_image(mask, original)  # resize mask to original image
                            original = set_mask_to_image(mask, original)
                            original.save(original_path)
            else:  # if not in g markup, then mask
                images_to_delete.append(image_element)

        for element in images_to_delete:    # remove files used to mask
            if os.path.isfile(temp_path + element.get("{http://www.w3.org/1999/xlink}href")[1:]):
                os.remove(temp_path + element.get("{http://www.w3.org/1999/xlink}href")[1:])

        return images, images_modules

    @classmethod
    def have_mask(cls, image_element):
        if image_element.get("mask") is not None:
            return True
        return False
