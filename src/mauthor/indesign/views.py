from django.shortcuts import render, get_object_or_404
from lorepo.filestorage.forms import UploadForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from lorepo.filestorage.models import UploadedFile, FileStorage
import xml.etree.ElementTree as ET
import datetime
from django.template import loader
from django.template.context import Context
from lorepo.mycontent.models import Content
from lorepo.spaces.util import get_private_space_for_user
from lorepo.spaces.models import Space
from lorepo.mycontent.service import add_content_to_space
from querystring_parser import parser
from libraries.utility.redirect import get_redirect_url

from lorepo.token.util import create_mycontent_editor_token
from mauthor.indesign.utils import convert_post_data


@login_required
def upload(request, space_id=None):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():  # Ensure form validation
            model = form.save(commit=False)  # Save instance without committing to DB yet
            model.owner = request.user
            model.content_type = request.FILES['file'].content_type
            model.filename = request.FILES['file'].name
            model.save()

            # Generate the redirect URL using reverse
            redirect_url = reverse('indesign:editor', args=[model.id])
            redirect_url += f'?space_id={space_id}&next={get_redirect_url(request)}'

            return redirect(redirect_url)
    else:
        form = UploadForm()

    upload_url = reverse('indesign:upload', args=[space_id])  # Assuming 'upload' is a named URL
    upload_url = f'{upload_url}?next={get_redirect_url(request)}'

    return render(request, 'indesign/upload.html', {
        'upload_url': upload_url,
        'form': form,
        'space_id': space_id,
        'next': get_redirect_url(request)
    })

@login_required
def editor(request, file_id):
    xml_file = get_object_or_404(UploadedFile, pk=file_id)
    root = ET.fromstring(xml_file.file.read())
    space_id = request.GET.get('space_id') if 'space_id' in request.GET else None
    return render(request, 'indesign/editor.html', {'root' : root, 'space_id' : space_id, 'next' : get_redirect_url(request)})

@login_required
def create_lesson(request):
    now = datetime.datetime.now()
    if not request.method == 'POST':
        return HttpResponseRedirect('/indesign/upload')

    parsed = parser.parse(request.POST.urlencode())
    if 'page' not in parsed:
        return HttpResponseRedirect('/indesign/upload')
    page_files = []
    t = loader.get_template('initdata/lesson/page_with_texts.xml')
    for page in convert_post_data(request.POST):
        template_result = t.render(Context({'texts' : page}))
        page_file = FileStorage(
                           created_date = now,
                           modified_date = now,
                           content_type = "text/xml",
                           contents = template_result.encode('utf-8'),
                           owner = request.user)
        page_file.save()
        page_files.append(page_file)

    params = {'pages' : page_files }
    t = loader.get_template('initdata/lesson/content.xml')
    c = Context(params)
    contents = t.render(c)

    contentFile = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = contents.encode('utf-8'),
                            owner = request.user)
    contentFile.version = 1
    contentFile.save()

    content = Content(
                    title='InDesign import',
                    tags='',
                    description='Lesson imported from InDesign', 
                    short_description='',
                    created_date = now, 
                    modified_date = now, 
                    author = request.user,
                    file = contentFile,
                    icon_href = None)

    content.add_title_to_xml()
    content.save()
    contentFile.history_for = content
    contentFile.save()

    space_id = request.REQUEST['space_id'] if 'space_id' in request.REQUEST else None
    if space_id is None:
        space = get_private_space_for_user(request.user)
    else:
        space = Space.objects.get(pk=space_id)
    add_content_to_space(content, space)

    skip_editor = request.REQUEST['skip_editor'] if 'skip_editor' in request.REQUEST else None
    if skip_editor:
        return HttpResponseRedirect(get_redirect_url(request))

    token, token_key = create_mycontent_editor_token(request.user)
    return HttpResponseRedirect('/mycontent/{}/editor?next={}&{}={}'.format(content.id, get_redirect_url(request), token_key, token))