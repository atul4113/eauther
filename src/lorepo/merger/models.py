import itertools
import random
import string
import xml.dom
import xml.dom.minidom

from django.shortcuts import get_object_or_404
from src.libraries.utility.lxml_utilities.content.xml_model import ContentXML
from src.libraries.utility.lxml_utilities.utilities import parse_main_xml_layouts
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.merger.utils import ensure_unique_layouts_and_css_ids, create_replace_map, replace_in_page_ids
from src.lorepo.mycontent.models import Content
from lxml import etree


class ContentMerger():
    main_xml = None

    def __init__(self, content):
        self.main_xml = xml.dom.minidom.parseString(content.file.contents)

    """
        Returns a tuple with:
            1. new content by merging pages from lessons in the merge_lessons list,
            2. a list of unique page ids that have been added to the new content
        merge_lessons is a list of dictionaries. Each dictionary should hold a 'content_id' referencing the merged lesson
        and a 'pages' list - a list od indices of the pages to be merged, for example:
        merge_lessons = [{'content_id':123354213,'pages':[0,4,6]},{'content_id':654321,'pages':[5]}]
        Newly created lesson has the title of the first lesson from merge_lessons with "Merge of " prefix
    """
    @staticmethod
    def create_merged_content(new_author, merge_lessons):
        first_content = merge_lessons[0]
        content_id = first_content['content_id']
        pages_indexes_to_extract = first_content['pages']
        common_pages_indexes_to_extract = first_content['common_pages']
        merged_content = Content.get_cached_or_404(id=content_id)
        main_xml_string = merged_content.file.contents
        new_xml_doc, first_translated_ids = ContentMerger._filter_content_pages(new_author, main_xml_string, pages_indexes_to_extract, common_pages_indexes_to_extract)
        main_content_semi_responsive_configuration = parse_main_xml_layouts(etree.fromstring(main_xml_string))

        content_translated_ids = [(content_id, first_translated_ids)]
        for lesson in itertools.islice(merge_lessons, 1, None):
            content_id = lesson['content_id']
            merge_pages = lesson['pages']
            merge_common_pages = lesson['common_pages']
            merged_content = Content.get_cached_or_404(id=content_id)
            merged_content_xml_string = merged_content.file.contents

            layouts_replace_map = ContentMerger._resolve_semi_responsive_configuration(main_content_semi_responsive_configuration, merged_content_xml_string)

            new_xml_doc, translated_ids = ContentMerger._merge_with_lesson_pages(new_author, merged_content_xml_string, merge_pages,
                                                                                 merge_common_pages, new_xml_doc, layouts_replace_map)
            content_translated_ids.append((content_id, translated_ids))

        content_xml = ContentXML.fromstring(new_xml_doc.toxml("utf-8"))
        content_xml.override_content_xml_with_layouts_and_css(main_content_semi_responsive_configuration)
        content_xml.update_content_version()

        content_file = FileStorage(
                           content_type = "text/xml",
                           contents = str(content_xml),
                           owner = new_author)
        content_file.save()
        #take the first lesson and get the title
        content_id = merge_lessons[0]['content_id']
        content = Content.get_cached_or_404(id=content_id)
        # save new content
        new_content = Content(
                       title = 'Merge of ' + content.title,
                       author = new_author,
                       icon_href = content.icon_href,
                       file = content_file,
                       tags = content.tags,
                       description = content.description,
                       short_description = content.short_description,
                       content_type = content.content_type
                       )
        new_content.save()

        content_file.history_for = new_content
        content_file.version = 1
        content_file.save()
        return new_content, content_translated_ids

    @staticmethod
    def _resolve_semi_responsive_configuration(main_content_semi_responsive_configuration, merged_content_xml_string):
        merged_content_layouts = parse_main_xml_layouts(etree.fromstring(merged_content_xml_string))

        missing_layouts_from_merged_content, missing_styles_from_merged_content, overlapping_thresholds = ContentMerger._find_missing_and_overlapping_configuration(
            main_content_semi_responsive_configuration, merged_content_layouts)

        new_missing_layouts, new_missing_styles, conversion_map = ensure_unique_layouts_and_css_ids(
            missing_layouts_from_merged_content,
            missing_styles_from_merged_content,
            main_content_semi_responsive_configuration.layouts_ids_set(),
            main_content_semi_responsive_configuration.styles_ids_set())

        main_content_semi_responsive_configuration.add_styles(new_missing_styles)
        main_content_semi_responsive_configuration.add_layouts(new_missing_layouts)

        overlapping_merged_content_layouts = merged_content_layouts.matching_threshold_layouts(overlapping_thresholds)
        overlapping_main_content_layouts = main_content_semi_responsive_configuration.matching_threshold_layouts(overlapping_thresholds)

        layouts_replace_map = create_replace_map(from_layouts=overlapping_merged_content_layouts, to_layouts=overlapping_main_content_layouts)
        layouts_replace_map.update(conversion_map)
        return layouts_replace_map

    @staticmethod
    def _find_missing_and_overlapping_configuration(main_content_semi_responsive_configuration, merged_content_layouts):
        main_content_thresholds, merged_content_thresholds = main_content_semi_responsive_configuration.thresholds_set(), merged_content_layouts.thresholds_set()

        overlapping_thresholds = main_content_thresholds & merged_content_thresholds
        missing_thresholds = merged_content_thresholds - main_content_thresholds

        missing_layouts_from_merged_content = merged_content_layouts.matching_threshold_layouts(missing_thresholds)
        missing_styles_from_merged_content = merged_content_layouts.matching_threshold_styles(missing_thresholds)
        return missing_layouts_from_merged_content, missing_styles_from_merged_content, overlapping_thresholds

    @staticmethod
    def _merge_with_lesson_pages(new_author, xml_string, pages_to_extract, commons_to_extract, new_xml_document, layouts_replace_map):
        merged_document = xml.dom.minidom.parseString(xml_string)

        merged_document_pages = merged_document.getElementsByTagName("pages")[0]

        new_pages = new_xml_document.getElementsByTagName("pages")[0]
        existing_page_ids = {node.getAttribute("id") for node in new_pages.getElementsByTagName('page')}

        translated_ids = ContentMerger._remove_not_picked_pages_and_ensure_unique_ids(existing_page_ids, merged_document_pages,
                                                                                      new_author,
                                                                                      pages_to_extract,
                                                                                      layouts_replace_map)

        merged_document_commons, commons_translated_ids = ContentMerger._remove_not_picked_commons_and_ensure_unique_ids(commons_to_extract,
                                                                                                                         existing_page_ids,
                                                                                                                         merged_document,
                                                                                                                         new_author,
                                                                                                                         layouts_replace_map)

        ContentMerger._copy_left_over_pages(from_node=merged_document_pages,
                                            to_node=new_pages)  # combine duplicate chapters, remove any empty chapters and fix duplicate page names in those chapters
        ContentMerger._normalize_chapters(new_pages)

        folder_nodes = new_xml_document.getElementsByTagName('folder')
        ContentMerger._copy_left_over_pages_from_commons(folder_nodes, merged_document_commons, new_xml_document)
        ContentMerger._copy_addon_descriptors(to_node=new_xml_document, from_node=merged_document)
        ContentMerger._copy_assets_descriptors(to_node=new_xml_document, from_node=merged_document)
        translated_ids.update(commons_translated_ids)
        return new_xml_document, translated_ids

    @staticmethod
    def _copy_left_over_pages_from_commons(folder_nodes, merged_doc_commons, newXmlDoc):
        # copy pages from commons
        if folder_nodes.length > 0 and merged_doc_commons:
            new_commons = folder_nodes[0]
            for node in merged_doc_commons.childNodes:
                if node.nodeName == "page":
                    new_commons.appendChild(node.cloneNode(deep=True))
            ContentMerger._fix_page_names(new_commons)
        elif merged_doc_commons:
            newXmlDoc.appendChild(merged_doc_commons)

    @staticmethod
    def _copy_left_over_pages(from_node, to_node):
        # copy leftover pages and chapters
        page_or_chapter_predicate = lambda node: node.nodeName == "page" or node.nodeName == "chapter"
        for node in filter(page_or_chapter_predicate, from_node.childNodes):
            to_node.appendChild(node.cloneNode(deep=True))

    @staticmethod
    def _remove_not_picked_commons_and_ensure_unique_ids(commons_to_extract, existing_page_ids, merged_doc, new_author, replace_map):
        merged_doc_commons = None
        translated_ids = {}
        if len(commons_to_extract):
            merged_doc_commons = merged_doc.getElementsByTagName("folder")[0]
            for idx, node in enumerate(merged_doc_commons.getElementsByTagName("page")):
                if idx not in commons_to_extract:
                    merged_doc_commons.removeChild(node)
                else:
                    page_id = node.getAttribute("id")
                    if page_id in existing_page_ids:
                        new_page_id = ContentMerger._gen_new_page_id(existing_page_ids)
                        translated_ids[page_id] = new_page_id
                        page_id = new_page_id
                        node.setAttribute("id", page_id)
                    else:
                        translated_ids[page_id] = None  # id not translated, but needs to be here
                    href = node.getAttribute("href")
                    pageFile = get_object_or_404(FileStorage, pk=href)
                    new_page_xml = replace_in_page_ids(pageFile.contents, replace_map)
                    node.setAttribute("href", str(pageFile.getCopy(new_author, contents=new_page_xml).id))
                    existing_page_ids.add(page_id)
        return merged_doc_commons, translated_ids

    @staticmethod
    def _remove_not_picked_pages_and_ensure_unique_ids(existing_page_ids, merged_doc_pages, new_author, pages_to_extract, replace_map):
        translated_ids = {}
        for idx, node in enumerate(merged_doc_pages.getElementsByTagName('page')):
            if idx not in pages_to_extract and node.parentNode.nodeName != "folder":
                node.parentNode.removeChild(node)
            else:
                page_id = node.getAttribute("id")
                if page_id in existing_page_ids:
                    new_page_id = ContentMerger._gen_new_page_id(existing_page_ids)
                    translated_ids[page_id] = new_page_id
                    page_id = new_page_id
                    node.setAttribute("id", page_id)
                else:
                    translated_ids[page_id] = None  # id not translated, but needs to be here
                href = node.getAttribute("href")
                pageFile = get_object_or_404(FileStorage, pk=href)
                new_contents = replace_in_page_ids(pageFile.contents, replace_map)
                node.setAttribute("href", str(pageFile.getCopy(new_author, contents=new_contents).id))
                existing_page_ids.add(page_id)
        return translated_ids

    """
        generate a random page id, a unique id in the set_of_ids
    """
    @staticmethod
    def _gen_new_page_id(set_of_ids=None):
        allowed_chars =  string.lowercase + string.uppercase + string.digits
        rand_id = ''.join(random.choice(allowed_chars) for i in range(6))
        if set_of_ids is not None:
            while rand_id in set_of_ids:
                rand_id = ''.join(random.choice(allowed_chars) for i in range(6))
        return rand_id

    @staticmethod
    def _find_child_chapters_with_name(root_node, original_node):
        dups = []
        name = original_node.getAttribute("name")
        for node in root_node.childNodes:
            if node.nodeName == "chapter":
                if node.getAttribute("name") == name and node != original_node:
                    dups.append(node)
        return dups

    @staticmethod
    def _combine_chapters(first_node, second_node):
        for node in second_node.childNodes:
            first_node.appendChild(node.cloneNode(deep=True))

    @staticmethod
    def _fix_duplicate_chapters(current_node):
        #first: combine duplicated chapters
        for node in current_node.childNodes:
            if node.nodeName == "chapter":
                dups = ContentMerger._find_child_chapters_with_name(current_node,node)
                for dup in dups:
                    ContentMerger._combine_chapters(node, dup)
                    current_node.removeChild(dup)
        #second: fix duplications in sub chapters that are result of the previous operation
        for node in current_node.childNodes:
            if node.nodeName == "chapter":
                ContentMerger._fix_duplicate_chapters(node)

    @staticmethod
    def _append_page_name_prefixes(current_node, page_name):
        page_counter = 0
        for node in current_node.childNodes:
            if node.nodeName == "page":
                if page_name == node.getAttribute("name"):
                    if page_counter>0:
                        node.setAttribute("name",page_name+" ("+str(page_counter)+")")
                    page_counter += 1

    @staticmethod
    def _fix_page_names(pages_node):
        for node in pages_node.childNodes:
            if node.nodeName == "chapter":
                ContentMerger._fix_page_names(node)
            elif node.nodeName == "page":
                ContentMerger._append_page_name_prefixes(pages_node, node.getAttribute("name"))

    @staticmethod
    def _remove_empty_chapters(root_node):
        for node in list(root_node.childNodes):
            if node.nodeName == "chapter":
                ContentMerger._remove_empty_chapters(node)
                if not node.hasChildNodes():
                    root_node.removeChild(node)

    @staticmethod
    def _normalize_chapters(pages_node):
        ContentMerger._remove_empty_chapters(pages_node)
        ContentMerger._fix_duplicate_chapters(pages_node)
        ContentMerger._fix_page_names(pages_node)

    @staticmethod
    def _copy_addon_descriptors(to_node, from_node):
        if len(to_node.getElementsByTagName("addons")):
            to_addons = to_node.getElementsByTagName("addons")[0]
            existting_addon_desc = [node.getAttribute("addonId") for node in to_addons.getElementsByTagName("addon-descriptor")]
            for node in from_node.getElementsByTagName("addon-descriptor"):
                if node.getAttribute("addonId") not in existting_addon_desc:
                    to_addons.appendChild(node.cloneNode(deep=False))
        elif len(from_node.getElementsByTagName("addons")):
            from_addons = from_node.getElementsByTagName("addons")[0]
            to_node.appendChild(from_addons.cloneNode(deep=True))

    @staticmethod
    def _copy_assets_descriptors(to_node, from_node):
        if len(to_node.getElementsByTagName("assets")):
            to_assets = to_node.getElementsByTagName("assets")[0]
            existing_file_names = []
            existing_file_url  = []
            for node in to_assets.getElementsByTagName("asset"):
                existing_file_names.append(node.getAttribute("fileName"))
                existing_file_url.append(node.getAttribute("href"))
            for node in from_node.getElementsByTagName("asset"):
                if node.getAttribute("href") not in existing_file_url:
                    name = node.getAttribute("fileName")
                    if name in existing_file_names:
                        name += "1"
                        node.setAttribute("fileName", name)
                        existing_file_names.append(name)
                    to_assets.appendChild(node.cloneNode(deep=False))
                    existing_file_url.append(node.getAttribute("href"))
        elif len(from_node.getElementsByTagName("assets")):
            from_assets = from_node.getElementsByTagName("assets")[0]
            to_node.appendChild(from_assets.cloneNode(deep=True))


    @staticmethod
    def _build_page_chapter_titles(xml_node, index):
        chapter_root = []
        i = index
        for node in xml_node.childNodes:
            if node.nodeName == "page":
                chapter_root.append({'isPage':True, 'title': node.getAttribute("name"), 'index': i})
                i+=1
            elif node.nodeName == "chapter":
                new_chapter, i =  ContentMerger._build_page_chapter_titles(node, i)
                chapter_root.append({'isPage':False, 'title': node.getAttribute("name"), 'content': new_chapter})
        return chapter_root, i

    @staticmethod
    def _filter_content_pages(new_author, xml_string, pages_to_extract, commons_to_extract):
        tranlated_ids = {}
        content = xml.dom.minidom.parseString(xml_string)
        pages = content.getElementsByTagName("pages")[0]
        for idx, node in enumerate(pages.getElementsByTagName('page')):
            if idx not in pages_to_extract and node.parentNode.nodeName != "folder":
                node.parentNode.removeChild(node)
            else:
                href = node.getAttribute("href")
                pageFile = get_object_or_404(FileStorage, pk=href)
                node.setAttribute("href", str(pageFile.getCopy(new_author).id))
                # id not translated, but needs to be here, to indicate it's being copied
                tranlated_ids[node.getAttribute("id")] = None

        folders = content.getElementsByTagName("folder")

        if len(folders) > 0:
            commons = folders[0]
            for idx, node in enumerate(commons.getElementsByTagName("page")):
                name = node.getAttribute("name")
                if idx not in commons_to_extract and name != "header" and name != "footer":  # preserve header and footer for first lesson
                    commons.removeChild(node)
                else:
                    href = node.getAttribute("href")
                    pageFile = get_object_or_404(FileStorage, pk=href)
                    node.setAttribute("href", str(pageFile.getCopy(new_author).id))
                    # id not translated, but needs to be here, to indicate it's being copied
                    tranlated_ids[node.getAttribute("id")] = None
        ContentMerger._remove_empty_chapters(pages)
        return content, tranlated_ids

    def get_page_chapter_titles(self):
        lesson_root = []
        pages = self.main_xml.getElementsByTagName("pages")[0]
        i = 0
        for node in pages.childNodes:
            if node.nodeName == "page":
                lesson_root.append({'isPage':True, 'title': node.getAttribute("name"), 'index': i})
                i+=1
            elif node.nodeName == "chapter":
                chapter_root,i =  ContentMerger._build_page_chapter_titles(node, i)
                lesson_root.append({'isPage':False, 'title': node.getAttribute("name"), 'content': chapter_root})
        return lesson_root

    @staticmethod
    def _flat_page_chapter_impl(all_pages, indent=""):
        pages_chapters = []
        INDENT_CHAR = "&nbsp;&nbsp;&nbsp;"
        for node in all_pages:
            if node['isPage']:
                pages_chapters.append({'isPage':True, 'indent':indent, 'title':node['title'], 'index': node['index']})
            else:
                pages_chapters.append({'isPage':False, 'indent':indent, 'title':node['title']})
                pages_chapters+=ContentMerger._flat_page_chapter_impl(node['content'], indent+INDENT_CHAR)
        return  pages_chapters

    def flat_page_chapter_structure(self):
        all_pages = self.get_page_chapter_titles()
        return  ContentMerger._flat_page_chapter_impl(all_pages)

    def common_pages(self):
        common_pages = []
        commons_nodes = self.main_xml.getElementsByTagName("folder")
        if commons_nodes.length > 0:
            commons_node = commons_nodes[0]
            for idx, page_node in enumerate(commons_node.getElementsByTagName("page")):
                title = page_node.getAttribute('name')
                if  title != "header" and title != "footer":
                    common_pages.append({'title': title, 'index': idx})
        return common_pages
