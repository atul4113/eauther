from xml.dom import minidom, NotFoundErr, Node
import re
from django.contrib.auth.models import User

from django.db import models
from src.lorepo.spaces.models import Space
from functools import partial

file_serve_search = partial(re.findall, '/file/serve/[\d]+')


class LessonCleaner():
    def __init__(self, main_page):
        self.doc = minidom.parseString(main_page.contents)
        self.assets_removed = []
        self.errors = []
        
    def print_doc(self):
        return self.doc.toprettyxml(encoding = 'UTF-8')
    
    def get_assets_nodes(self):
        return self.doc.getElementsByTagName('asset')

    def get_descriptors_nodes(self):
        return self.doc.getElementsByTagName('addon-descriptor')

    def get_node(self, name):
        found_nodes = self.doc.getElementsByTagName(name)
        if len(found_nodes) > 0:
            return found_nodes[0]
        else:
            return None
    
    def get_pages_nodes(self):
        return self.doc.getElementsByTagName('page')
    
    def get_attribute_values_from_many_nodes(self, attribute, nodes):
        values = []
        for node in nodes:
            if node.hasAttribute(attribute):
                values.append(node.getAttribute(attribute))
        return values
    
    def get_all_file_serves_from_page(self, page):
        return file_serve_search(page.contents)

    def get_all_addons_from_page(self, page):
        page_xml = minidom.parseString(page.contents)
        modules = page_xml.getElementsByTagName('modules')
        if len(modules) > 0:
            return self._get_all_addons_id_from_modules_tag(modules[0])
        return []

    def _get_all_addons_id_from_modules_tag(self, modules):
        addons_ids = []

        for addon in modules.getElementsByTagName('addonModule'):
            addonId = addon.getAttribute('addonId')
            addons_ids.append(addonId)

        return addons_ids

    def get_all_file_serves_from_styles(self):
        unparsed_version = self.doc.documentElement.getAttribute("version")
        version = int(unparsed_version) if unparsed_version != "" else 1

        if version == 2:
            return self._get_file_server_styles_semi_responsive()
        else:
            return self._get_file_server_styles_non_semi_responsive()

    def _get_file_server_styles_semi_responsive(self):
        styles_list = self.doc.getElementsByTagName("styles")
        if len(styles_list) > 0:
            result = []
            for style_node in styles_list[0].childNodes:
                if style_node.nodeType == Node.ELEMENT_NODE:
                    style_contents = style_node.firstChild
                    if style_contents is not None:
                        result = result + file_serve_search(style_contents.nodeValue)

            return result
        return []

    def _get_file_server_styles_non_semi_responsive(self):
        style_nodes = self.doc.getElementsByTagName('style')
        if len(style_nodes) > 0 and style_nodes[0].firstChild:
            style_contents = style_nodes[0].firstChild.nodeValue
            return file_serve_search(style_contents)
        return []


    def get_non_used_assets_nodes(self, assets_hrefs, pages_file_serves):
        non_used_hrefs = list( set(assets_hrefs) - set(pages_file_serves) )
        assets = self.get_assets_nodes()
        non_used_nodes = []
        
        for asset in assets:
            if asset.getAttribute('href') in non_used_hrefs:
                non_used_nodes.append(asset)
            
        return non_used_nodes

    def delete_specific_nodes(self, parent, nodes):
        for node in nodes:
            try:
                parent.removeChild(node)
                self.assets_removed.append(node.getAttribute('href'))
            except ValueError as NotFoundErr:
                self.errors.append('Error occured when trying to remove node %s from %s' % ( node.nodeName, parent.nodeName ))

    def delete_unused_descriptors(self, descriptors_to_delete):
        addons_descriptors = self.doc.getElementsByTagName("addons")
        if len(addons_descriptors) != 0:
            descriptors_parent = addons_descriptors[0]

            for descriptor in descriptors_to_delete:
                try:
                    descriptors_parent.removeChild(descriptor)
                except NotFoundErr:
                    self.errors.append('Error occured when trying to remove descriptor node %s from %s' % (descriptors_parent.nodeName, descriptor.nodeName))


class AssetsOrPagesReplacementConfig(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    assets = models.TextField()
    meta_data = models.TextField()
