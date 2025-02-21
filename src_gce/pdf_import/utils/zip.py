from zipfile import ZipFile, ZIP_DEFLATED
from libraries import zip


def zip_lesson(path):
    zipfile = ZipFile(path + "/zip_file.zip", 'w', ZIP_DEFLATED)
    zip.zip_directory(path + "/pages/", zipfile, "pages")
    zip.zip_directory(path + "/resources/", zipfile, "resources")
    zipfile.write(path + "/metadata.xml", "metadata.xml")
    zipfile.close()