import re

EMBED = re.compile('.*/embed/(\d+).*')
MYCONTENT = re.compile('.*/mycontent/view/(\d+).*')
CORPORATE = re.compile('.*/corporate/view/(\d+).*')

def parse_lesson_id(url):
    match = EMBED.match(url)
    if match is not None:
        return match.group(1)
    match = MYCONTENT.match(url)
    if match is not None:
        return match.group(1)
    match = CORPORATE.match(url)
    if match is not None:
        return match.group(1)