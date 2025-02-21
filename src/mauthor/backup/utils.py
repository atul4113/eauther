import re

def make_path(content_id, content_title):
    cid = str(content_id)
    title = content_title.strip()
    title = re.sub('[/\?<>:\*\|"\^\\\]', '_', title)
    title = re.sub('_+', '_', title)
    exceeded_length = len(title) + len(cid) + 3 - 255
    if exceeded_length > 0:
        title = title[:0-exceeded_length]

    return "%s - %s/" % (cid, title)

def get_path(zip, old_id, title):

    paths = [
        make_path(old_id, title),
        "%s - %s/" % (old_id, title)
        ]

    i = 0
    paths_length = len(paths)

    for path in paths:
        try:
            zip.read(path + 'metadata.xml')
            return path
        except KeyError as e:
            i += 1
            if i == paths_length:
                raise e
