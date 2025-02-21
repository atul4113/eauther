# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from lorepo.mycontent.models import Content
from lorepo.mycontent.signals import metadata_updated
from lorepo.spaces.models import Space, SpaceType
from lorepo.spaces.util import get_private_space_for_user
from lorepo.merger.models import ContentMerger
from libraries.utility.redirect import get_redirect
from lorepo.mycontent.service import add_content_to_space
from django.contrib import messages
from lorepo.permission.decorators import has_space_access
from querystring_parser import parser
from lorepo.permission.models import Permission
from libraries.utility.helpers import get_object_or_none
from mauthor.metadata.util import copy_page_metadata

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def extract_pages(request, content_id, space_id=None):
    content = Content.get_cached_or_404(id=content_id)
    parsed = parser.parse(request.POST.urlencode())
    pages_to_extract = []
    common_pages_to_extract = []
    if 'pages' in parsed:
        pages_to_extract = list(parsed['pages'].keys())
    if 'common_pages' in parsed:
        common_pages_to_extract = list(parsed['common_pages'].keys())
    if not pages_to_extract and not common_pages_to_extract:
        messages.warning(request, 'You need to select some pages to extract new lesson')
        return get_redirect(request)
    lesson_dict = {}
    lesson_dict['title'] = content.title
    lesson_dict['content_id'] = content_id
    lesson_dict['pages'] = sorted(pages_to_extract) if pages_to_extract else []
    lesson_dict['common_pages'] = sorted(common_pages_to_extract) if common_pages_to_extract else []
    if 'merge_lessons' not in request.session or request.session['merge_lessons'] is None:
        request.session['merge_lessons'] = []
    merge_list = request.session['merge_lessons']
    merge_list.append(lesson_dict)
    request.session['merge_lessons'] = merge_list  #there has to be an assignment here or the session won't be saved
    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def merge_undo(request):
    request.session.pop('merge_lessons',None)
    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def list_merge_pages(request, content_id, space_id):
    space = get_object_or_none(Space, pk = space_id)
    content = Content.get_cached_or_404(id=content_id)
    next_url = '/mycontent'
    if space:
        if space.space_type == SpaceType.CORPORATE:
            next_url = '/corporate/list/' + space_id
        else:
            next_url = next_url +  '/' + space_id
    merger = ContentMerger(content)
    pages_chapters = merger.flat_page_chapter_structure()
    common_pages = merger.common_pages()

    return render(request, 'merger/list_merge_pages.html', {'content' : content,
                                                            'pages_chapters': pages_chapters,
                                                            'common_pages': common_pages,
                                                            'space' : space,
                                                            'next' : next_url })

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def merge(request,space_id = None):
    if 'merge_lessons' in request.session and request.session['merge_lessons'] is not None:
        #create merged lesson
        new_content, content_page_translated_ids = ContentMerger.create_merged_content(request.user, request.session['merge_lessons'])
        new_content.save()
        if space_id is not None:
            space = get_object_or_404(Space, pk=space_id)
        else:
            space = get_private_space_for_user(request.user)
        add_content_to_space(new_content, space, False)
        metadata_updated.send(sender=None, content_id=new_content.id)
        messages.info(request, 'New lesson has been created based on selected pages')
        #copy page metadata
        for content_id, translated_ids in content_page_translated_ids:
            content_from = Content.get_cached_or_404(id = content_id)
            copy_page_metadata(content_from, new_content, translated_ids)
        request.session.pop('merge_lessons',None)
    return get_redirect(request)
