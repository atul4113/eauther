from itertools import groupby
from collections import namedtuple


def _page_text_filter(value):
    return value.startswith("page") and value.endswith("['text']")


def _page_index_key(value):
    index = value.find("]")
    lindex = value.find("[") + 1
    return int(value[lindex:index])


def convert_post_data(post_data):
    text_only = list(filter(_page_text_filter, post_data))
    sorted_only = sorted(text_only, key=_page_index_key)
    grouped_by_page = groupby(sorted_only, _page_index_key)

    pages = []
    for page_index, group in grouped_by_page:
        texts = []
        for text_index in group:
            text_data = post_data[text_index]
            text_id = post_data[text_index.replace("text", "id")]
            texts.append(TextModuleIndesign(text_id, text_data))
        pages.append(list(reversed(texts)))

    return pages

TextModuleIndesign = namedtuple("TextModuleIndesign", "id text")
