from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from lorepo.editor.forms import FeedbackForm
from lorepo.editor.models import UserFeedback
from lorepo.filestorage.models import FileStorage
from lorepo.mycontent.models import Content, ContentType, AddonToCategory, DefaultTemplate
from lorepo.public.util import filter_public_contents
from lorepo.spaces.util import get_all_user_spaces, get_space_for_content, get_private_space_for_user
import datetime
import json
import libraries.utility.cacheproxy as cache
from lorepo.mycontent.util import get_contents_from_specific_space
from lorepo.spaces.models import Space, SpaceType
from lorepo.editor.decorators import is_logged


@is_logged
def templates(request):
    templates = _read_corporate_templates(request)
    uri = request.build_absolute_uri("/")
    return render(request, 'editor/templates.json', {'templates': templates, 'uri': uri})


@is_logged
def addons(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    space = get_space_for_content(content)
    addons_from_request_space = Content.objects.filter(spaces=str(space.id), content_type=ContentType.ADDON,
                                                       is_deleted=False)
    for addon in addons_from_request_space:
        addon.category = 'Private'

    if request.user.company:
        contents = _read_corporate_addons(request)
    else:
        contents = set()  # read_corporate_addons returns a set
    contents.update(addons_from_request_space)

    uri = request.build_absolute_uri("/")
    resp = render(request, 'editor/addons.json', {'addons': contents, 'uri': uri})
    local = json.loads(resp.content)
    resp.content = json.dumps(local)
    return resp


def _should_include_contents_in_editor(space):
    return hasattr(space, 'include_contents_in_editor') and space.include_contents_in_editor


def _read_corporate_addons(request):
    contents = cache.get('addons_for_%s' % (request.user.company.id))
    if contents is None:
        contents = []
        spaces = list(Space.objects.filter(parent__id=request.user.company.id,
                                           space_type=SpaceType.CORPORATE))  # get all company divisions
        for space in spaces:
            if _should_include_contents_in_editor(space):
                contents.extend(
                    Content.objects.filter(spaces=str(space.id), content_type=ContentType.ADDON, is_deleted=False,
                                           is_public=True))
        for content in contents:
            content.category = 'Corporate'
        cache.set('addons_for_%s' % (request.user.company.id), contents, 60 * 60 * 24)
    return set(contents)


def _read_corporate_templates(request):
    default_templates = [dt.template for dt in DefaultTemplate.objects.all()]
    _assign_category(default_templates, 'Public')

    user_space = get_private_space_for_user(request.user)
    user_templates = None
    if user_templates is None:
        user_templates = Content.objects.filter(spaces=str(user_space.id), content_type=ContentType.TEMPLATE,
                                                is_deleted=False).order_by('title')
        _assign_category(user_templates, 'Private')
        cache.set('templates_for_%s' % (request.user), user_templates, 60 * 60 * 24)

    sharing_corporate_spaces = Space.objects.filter(top_level=request.user.company, include_contents_in_editor=True)

    corporate_templates = None
    if corporate_templates is None:
        corporate_templates = []
        for space in sharing_corporate_spaces:
            corporate_templates.extend(Content.objects.filter(spaces=str(space.id), content_type=ContentType.TEMPLATE,
                                                              is_deleted=False).order_by('title'))
        _assign_category(corporate_templates, 'Public')
        cache.set('templates_for_%s' % (request.user.company.id), corporate_templates, 60 * 60 * 24)

    all_templates = set()
    all_templates.update(default_templates)
    all_templates.update(user_templates)
    all_templates.update(corporate_templates)
    all_templates = sorted(all_templates, key=lambda c: c.title)

    return all_templates


def _assign_category(contents, category):
    for content in contents:
        content.category = category


def _read_contents(request, content_type, is_deleted=False):
    contents = Content.objects.filter(content_type=content_type)
    contents = filter_public_contents(request.user, contents)
    for content in contents:
        associated_categories = AddonToCategory.objects.filter(addon=content)
        if len(associated_categories) > 0:
            content.category = associated_categories[0].category.title
        else:
            content.category = 'Others'
    user_spaces = get_all_user_spaces(request.user)
    for space in user_spaces:
        tmp_contents = get_contents_from_specific_space(space.id, lambda
            content: content.content_type == content_type and content.is_deleted == is_deleted)
        for content in tmp_contents:
            content.category = 'Private'
            contents.append(content)
    return sorted(contents, key=lambda content: content.title)


@is_logged
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = UserFeedback(content=form.cleaned_data['text'])
            feedback.created_date = datetime.datetime.now()
            feedback.author = request.user
            feedback.save()

    return HttpResponse("ok")


@is_logged
def addPage(request):
    now = datetime.datetime.now()
    xml = render_to_string('initdata/lesson/page.xml', {}).encode('utf-8')

    content_file = request.GET.get('content_file', '')
    content_file_id = content_file.replace('/file/', '')
    if content_file_id and content_file_id != '':
        content_file = get_object_or_404(FileStorage, pk=content_file_id)
        if content_file.owner != request.user:
            return HttpResponseForbidden('You are not logged in')
    else:
        return HttpResponseForbidden('Bad request from Editor')

    if request.GET.get('page'):
        page_url = request.GET.get('page')
        xml = page_url
        index = page_url.rfind('/')
        if index > 0:
            file_id = page_url[index + 1:]
            file = FileStorage.objects.get(pk=file_id)
            if file:
                xml = file.contents

    pageFile = FileStorage(
        created_date=now,
        modified_date=now,
        content_type="text/xml",
        contents=xml,
        owner=request.user)
    pageFile.save()

    return HttpResponse(pageFile.id)


# Removed AppEngine Blobstore handling
@is_logged
def blob_upload_dir(request):
    # Assuming this is replaced by your own file upload mechanism
    upload_url = '/file/upload'  # Modify with your own URL
    return HttpResponse(upload_url)
