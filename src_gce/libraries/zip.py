import os


def zip_directory(path, zip_file, dest_dirname=""):
    for dirname, subdirs, files in os.walk(path):
        for filename in files:
            zip_file.write(os.path.join(dirname, filename), os.path.join(dest_dirname, filename))