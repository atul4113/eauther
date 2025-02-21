from django.core.mail.message import EmailMultiAlternatives
from lorepo.mycontent.models import Content, ContentSpace
from lorepo.mycontent.service import get_list_by_ids
from django.utils.html import strip_tags
from lorepo.spaces.util import get_all_user_spaces, get_space_for_content
from lorepo.corporate.utils import is_in_public_category


# that function will send mail to all receivers in BCC field, with TO field set to undisclosed-recipients
def send_message(sender, receivers, subject, data):
    email_message = EmailMultiAlternatives(subject=subject, body=strip_tags(data), from_email=sender, to=['undisclosed-recipients:;'], bcc=receivers)
    email_message.attach_alternative(data, "text/html")
    email_message.send()


def filter_public_contents(user, contents):
    contents = [content for content in contents if (is_in_public_category(content, user.public_category) and content.is_content_public()) or content.is_globally_public]
    filtered_contents = []
    for content in contents:
        if content.is_globally_public:
            filtered_contents.append(content)
            continue
        space = get_space_for_content(content)
        if space.top_level == user.company:
            filtered_contents.append(content)
    return filtered_contents
