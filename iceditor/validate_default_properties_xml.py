import sys
import os
import fnmatch
from xml.etree import ElementTree

default_properties_folder = 'src/main/java/com/lorepo/iceditor/public/modules'

for root, dirnames, filenames in os.walk(default_properties_folder):
    for filename in fnmatch.filter(filenames, '*.xml'):
        file_src = os.path.join(root, filename)

        print '*', file_src

        with open(file_src, 'r') as file_source:
            ElementTree.fromstring(file_source.read())
