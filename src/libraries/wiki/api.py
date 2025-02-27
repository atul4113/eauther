import json
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from src.libraries.utility.helpers import get_object_or_none
from src.libraries.wiki.models import WikiPageTranslated, PrivateAddonWikiPage
from src.lorepo.mycontent.models import Content, ContentType
from src.lorepo.permission.decorators import has_space_access
from src.lorepo.permission.models import Permission
from src.markdown import markdown


def page(request, lang_code, url):
    if request.method != 'GET' or not lang_code or not url:
        raise Http404

    selected_page = WikiPageTranslated.page_for_url(url, lang_code)

    if selected_page:
        return HttpResponse(markdown(selected_page.text))

    content = get_object_or_none(Content, name=url, content_type=ContentType.ADDON)
    if content:
        wiki_page_entry, _ = PrivateAddonWikiPage.objects.get_or_create(
            addon=content,
            defaults={
                'text': PrivateAddonWikiPage.get_default_text()
            }
        )

        return HttpResponse(wiki_page_entry.get_page())

    raise Http404()


def section(request, lang_code, url):
    if request.method != 'GET' or not lang_code or not url:
        raise Http404

    selected_page = WikiPageTranslated.page_for_url(url, 'en')
    selected_translated_page = WikiPageTranslated.page_for_url(url, lang_code)

    if selected_page:
        selected_page.load_kids()
        children = []
        for child in selected_page.loaded_kids:
            translated_child = WikiPageTranslated.page_for_url(child.url, lang_code)
            children.append({
                'name': translated_child.title,
                'html': markdown(translated_child.text)
            })

        return HttpResponse(json.dumps({
            'page': {
                'name': selected_translated_page.title,
                'html': markdown(selected_translated_page.text)
            },
            'children': children
        }))
    raise Http404


@has_space_access(Permission.CONTENT_EDIT)
def private_addon(request, content_id):
    get_object_or_404(Content, id=content_id, content_type=ContentType.ADDON)
    wiki_page_entry, _ = PrivateAddonWikiPage.objects.get_or_create(
        addon_id=content_id,
        defaults={
            'text': PrivateAddonWikiPage.get_default_text()
        }
    )

    if request.method == 'GET':
        return HttpResponse(wiki_page_entry.text)

    elif request.method == 'POST':

        wiki_page_entry.text = request.read()
        wiki_page_entry.save()
        return HttpResponse("OK")