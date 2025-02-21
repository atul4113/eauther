import sys
import os
import re
from timeit import default_timer as timer
from subprocess import Popen, check_output
import subprocess
from lxml import etree as ET
from addons import ErrorText
from files import PageFile, MetadataFile
from files import MainFile
from files import ImageRepo
from Text import LineList
from addons import Image as Imgs
from pdf_import.models import Paragraph

PDF_PAGE_NAME_PATTERN = "%d_page_"
PDF_PAGE_NAME_REG = r'(?P<page_num>\d+)_page_.*(?:pdf|PDF)'

MAX_PDF_PAGE_SIZE = 1024 * 1024 * 2.5  # max page size to parse is 2,5 MB
MAX_SVG_BACKGROUND_SIZE = 1024 * 1024 * 15  # max output svg background size is 15MB
INKSCAPE_ABORD_TIME = 15  # max time to parse one page
INKSCAPE_MAX_PROCESS = 2
try_extract_images = False





def parse_pdf(temp_path, presentation_name):
    import logging

    logging.info("%s: pdftk is working..." % presentation_name)
    # extract pdf pages
    # call(["pdfseparate", pdfname, PDF_PAGE_NAME_PATTERN+pdfname])
    check_output(["pdftk", "%s%s" % (temp_path, presentation_name), "burst", "output", temp_path + PDF_PAGE_NAME_PATTERN + presentation_name], stderr=subprocess.STDOUT)

    # convert pages to SVG
    reg = re.compile(PDF_PAGE_NAME_REG)
    svg_pages = {}
    procs = []
    timers = []
    logging.info("%s: inkscape is working..." % presentation_name)
    procs_len = 0
    for path in os.listdir(temp_path):
        m = reg.match(path)
        if m:
            page_number = int(m.group('page_num'))
            src_abs_path = temp_path + path
            dest_abs_path = temp_path + '%d_page_%s.svg' % (page_number, presentation_name[:-4])
            statinfo = os.stat(src_abs_path)
            logging.info("%s: started: %s page." % (presentation_name, str(page_number)))
            if (not os.path.isfile(dest_abs_path) and
                    statinfo.st_size < MAX_PDF_PAGE_SIZE):
                procs.append(
                    Popen(['inkscape', '--without-gui',
                           '--export-plain-svg=' + dest_abs_path,
                           '--file=' + src_abs_path]))
                procs_len += 1
            else:
                if not os.path.isfile(dest_abs_path):
                    logging.error("%s: Can't find file after pdftk" % presentation_name)
                if statinfo.st_size < MAX_PDF_PAGE_SIZE:
                    logging.error("%s: Page is too big" % presentation_name)
            svg_pages[page_number] = dest_abs_path
            timers.append(timer())
            ended = [False] * len(procs)
            endedCount = 0
            if page_number % INKSCAPE_MAX_PROCESS == 0:  # spawn no more than 10 processes at once
                while procs_len > endedCount:
                    for iterator in range(0, procs_len):  # wait for svg's to export
                        if (timer() - timers[iterator] >= INKSCAPE_ABORD_TIME and not ended[iterator]):
                            if not procs[iterator] is None:
                                procs[iterator].kill()
                                ended[iterator] = True
                                endedCount += 1
                                logging.info("%s: inkscape task was killed (deadline exceeded)" % presentation_name)
                        else:
                            if not procs[iterator].poll() is None and ended[iterator] is not True:
                                ended[iterator] = True
                                endedCount += 1
                                logging.info("%s: Successfully ended inkscape task" % presentation_name)
                procs = []
                procs_len = 0
                timers = []
    for p in procs:  # wait for svg's to export
        p.wait()

    logging.info("%s: Start editing" % presentation_name)
    # create pages and resources directory
    for directory in ['resources', 'pages']:
        if not os.path.exists(temp_path + directory):
            os.makedirs(temp_path + directory)

    image_repo = ImageRepo()

    main_file = MainFile(presentation_name.encode('utf-8'))
    meta_file = MetadataFile(presentation_name.encode('utf-8'))
    first = True

    for page_number, svg_page_path in svg_pages.iteritems():

        logging.info("%s: working on: %s" % (presentation_name, str(page_number)))
        temp_file = image_repo.parse_file(svg_page_path, temp_path)
        if not temp_file:
            page = PageFile(None, page_number)
            page.add_text(ErrorText("Page parsing error."))
            logging.error("%s: Can't find page. Creating page parsing error page for page nr %d." % (presentation_name, page_number))
            with open(temp_path + 'pages/' + page.href, 'w') as f:
                f.write(page.to_xml())

            main_file.add_page(page)
            continue

        parser = ET.XMLParser(huge_tree=True,
                              encoding='UTF-8',
                              recover=True)
        tree = ET.parse(temp_file, parser)
        root = tree.getroot()
        page = PageFile(root, page_number)
        line_list = LineList(page.page_size)    # list of all text lines
        if first:
            logging.info("%s: Creating icon in %s from %s" % (presentation_name, temp_path, svg_page_path))
            meta_file.create_icon(temp_path, svg_page_path, page.page_size)
            first = False

        images, image_modules = Imgs.set_images_masks(root, temp_path, page_number, page)
        remove_from_background = set(images)

        for text_element in root.iter('{http://www.w3.org/2000/svg}text'):
            line_list.add_line(text_element)
            remove_from_background.add(text_element)
        line_list.cut_and_connect_lines()   # split lines

        paragraphs = separate_to_paragraphs(line_list)

        for item in remove_from_background:
            item.getparent().remove(item)

        bg_image_name = '%d_background.svg' % (page_number)
        with open(temp_path + 'resources/' + bg_image_name, "w") as f:
            f.write(ET.tostring(root, pretty_print=False))
            statinfo = os.stat(temp_path + 'resources/' + bg_image_name)


        if statinfo.st_size < MAX_SVG_BACKGROUND_SIZE:  # only deal with images less than 15 MB
            background_image = Imgs(image_name=bg_image_name, page_size=page.page_size, mime='image/svg+xml')
            page.add_image(background_image)
            main_file.add_asset(background_image)
            meta_file.add_resource(background_image)
        else:
            os.remove(temp_path + 'resources/' + bg_image_name)

        for image in image_modules:
            page.add_image(image)
            main_file.add_asset(image)
            meta_file.add_resource(image)

        for paragraph in paragraphs:
            page.add_text(paragraph)

        with open(temp_path + 'pages/' + page.href, 'w') as f:
            f.write(page.to_xml())

        main_file.add_page(page)
        os.remove(temp_file)

    with open(temp_path + 'pages/' + main_file.href, 'w') as f:
        f.write(main_file.to_xml())

    with open(temp_path + meta_file.href, 'w') as f:
        f.write(meta_file.to_xml())


def separate_to_paragraphs(line_list_obj):
    paragraphs = []
    sorted_line_list = line_list_obj.get_lines_sorted_by_y()
    for line in sorted_line_list:
        added = False
        for paragraph in paragraphs:
            if paragraph.is_in_paragraph(line):
                paragraph.add_to_paragraph(line)
                added = True
                break
        if not added:
            paragraphs.append(Paragraph(line))

    return paragraphs
