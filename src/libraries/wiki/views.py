import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from libraries.utility.decorators import backend
from libraries.wiki.forms import WikiPageForm, WikiPageTranslatedForm
from libraries.wiki.models import WikiPage, WikiFile, WikiPageTranslated
import datetime
from libraries.wiki.util import make_url, has_access_to_wiki
from lorepo.filestorage.forms import UploadForm
from google.appengine.api import blobstore
import re
from string import split
from django.contrib import messages
from mauthor.utility.db_safe_iterator import safe_iterate


def index(request, url=None, lang_code=None, highlight_word=''):
    no_menu = True if 'no_menu' in request.GET else False
    user = request.user
    if not lang_code:
        lang_code = settings.LANGUAGE_CODE
        if user.is_authenticated():
            lang_code = user.profile.language_code
        if url:
            return HttpResponsePermanentRedirect('/doc/%s/page/%s'%(lang_code, url) + ('?no_menu' if no_menu else ''))
        else:
            return HttpResponsePermanentRedirect('/doc/'+lang_code)

    if user.is_staff or user.is_superuser:
        lang_code = WikiPageTranslated.validated_language_code(lang_code, settings.LANGUAGES)
    else:
        lang_code = WikiPageTranslated.validated_language_code(lang_code)

    toc = WikiPageTranslated.toc_pages(lang_code)

    if not url and len(toc) > 0:
        url = toc[0]['url']
    selected_page = WikiPageTranslated.page_for_url(url, lang_code)

    if not selected_page and url:
        return HttpResponseRedirect('/doc/add?title=' + url)

    context = {
                'toc_pages' : toc,
                'selected_page' : selected_page,
                'lang_code' : lang_code,
                'languages' : None,
                'page_url'  :  url,
                'highlight_word' : highlight_word
              }

    if user.is_authenticated() and (user.is_staff or user.is_superuser):
        context['languages'] = [lang[0] for lang in settings.LANGUAGES]
    context['no_menu'] = no_menu
    return render(request, 'wiki/index.html', context)


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def edit_toc(request):
    WikiPageTranslated.flush_toc()
    wiki_pages = WikiPageTranslated.objects.filter(parent=None, is_toc=True, language_code='en').order_by('order')
    for page in wiki_pages:
        page.load_kids()
    pages = WikiPageTranslated.objects.filter(is_toc=False, language_code='en')
    return render(request, 'wiki/edit_toc.html', { 'wiki_pages' : wiki_pages, 'pages' : pages })

def preview_page(request):
    if request.method == 'POST':
        page = WikiPageTranslated(title=request.POST['title'], text=request.POST['text'])
        return render(request, 'wiki/preview.html', {'page' : page})
    else:
        raise Http404

def pageIndex(request):
    if len(WikiPageTranslated.objects.filter()) == 0:
        if not has_access_to_wiki(request.user):
            raise Http404
        return HttpResponseRedirect('/doc/add')

    page = WikiPageTranslated.objects.filter()[0]
    if len(WikiPageTranslated.objects.filter(is_toc=True)) > 0:
        page = WikiPageTranslated.objects.filter(is_toc=True)[0]
    return render(request, 'wiki/page.html', {'page' : page})

@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def addPage(request):
    title = request.GET.get('title')
    if request.method == 'POST':
        form = WikiPageForm(request.POST)

        if form.is_valid():
            page = WikiPageTranslated(
                title = form.cleaned_data['title'],
                text = form.cleaned_data['text'],
                url = make_url(form.cleaned_data['title']),
                modified_date=datetime.datetime.now(),
                author=request.user,
                language_code='en')
            page.save()
            page.clone_for_languages(settings.LANGUAGES)
            messages.info(request, "Page %(page_name)s has been added." % { 'page_name' : page.title })
            return HttpResponseRedirect('/doc')
        else:
            return render(request, 'wiki/addpage.html', { 'form' : form })

    return render(request, 'wiki/addpage.html', { 'title' : title })


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def edit(request, page_id):
    page = get_object_or_404(WikiPageTranslated, pk=page_id)
    if request.method == 'POST':
        form = WikiPageTranslatedForm(request.POST)
        if form.is_valid():
            page.title = form.cleaned_data['title']
            page.text = form.cleaned_data['text']
            page.modified_date=datetime.datetime.now()
            if page.language_code == 'en':
                url = make_url(form.cleaned_data['title'])
                for trans_page in list(page.get_translations().values()):
                    trans_page.url = url
                    trans_page.save()
            else:
                page.save()
            messages.info(request, "Page %(page_name)s has been edited." % { 'page_name' : page.title })
            WikiPageTranslated.flush_toc()
            return HttpResponseRedirect('/doc/%s/page/%s' %(page.language_code , page.url))
        else:
            return render(request, 'wiki/edit.html', {'page' : page, 'form' : form })
        

    return render(request, 'wiki/edit.html', {'page' : page })   

@login_required
def upload(request):
    """
    Handler wywolywany po uploadzie obrazka dla wiki
    """
    
    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            model = form.save(False)
            model.owner = request.user
            model.content_type = request.FILES['file'].content_type
            model.save()
            wf = WikiFile(uploaded_file=model)
            wf.save()
            messages.info(request, "New file has been uploaded")
            return HttpResponseRedirect('/doc') if form.data["next"] is None else HttpResponseRedirect(form.data["next"])
        form = UploadForm(request.POST)
        return HttpResponseRedirect('/doc/upload?next=' + form.data['next'])
    else:
        upload_url = blobstore.create_upload_url('/doc/upload')
        form = UploadForm()
        return render(request, 'wiki/upload.html', 
                      {
                    'upload_url' : upload_url,
                    'form' : form,
                    'next' : request.GET.get("next", None)
                    })

@login_required
def add_file(request):
    wiki_files = WikiFile.objects.all()
    files = [wf.uploaded_file for wf in wiki_files]
    return render(request, 'wiki/add_file.html', 
                    {
                    'files' : files,
                    })

@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required  
def table_of_contents(request):
    itemsList = request.POST
    i = 0
    order = request.POST.get("order")
    if order:
        order = split(order, ",")
        for wiki_id in order:
            wiki = WikiPageTranslated.objects.filter(pk=wiki_id)[0]
            parent_id = itemsList['list[%(wiki_id)s]' % { 'wiki_id' : wiki_id }]
            if parent_id == 'root':
                parent = None
            else:
                parent = WikiPageTranslated.objects.filter(pk=parent_id)[0]
            wiki.parent = parent
            wiki.order = i
            wiki.is_toc = True
            wiki.save()
            i += 1

    messages.info(request, 'Table of contents has been saved.')
    WikiPageTranslated.flush_toc()
    return HttpResponse("OK")

@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def remove_from_toc(request):
    items_to_remove = request.POST
    for key in list(items_to_remove.keys()):
        m = re.search("(?P<index>\d+)", key)
        wiki_id = m.group('index')
        wiki = WikiPageTranslated.objects.filter(pk=wiki_id)[0]
        wiki.is_toc = False
        wiki.parent = None
        wiki.save()
    return HttpResponse('ok')


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required   
def delete(request, page_id):
    wiki = get_object_or_404(WikiPageTranslated, pk=page_id)
    messages.info(request, "%(wiki)s has been removed." % locals())
    for child in wiki.kids.all():
        child.parent = None
        child.order = None
        child.is_toc = False
        child.save()
    wiki.delete()
    WikiPageTranslated.flush_toc()
    return HttpResponseRedirect("/doc")

@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@backend
def fixdb_reload_wiki(request):
    wiki_query =  WikiPage.objects.all()
    for pages in safe_iterate(wiki_query):
        for page in pages:
            try:
                page_translation = WikiPageTranslated.objects.get(url=page.url,language_code='en')
                page_translation.text = page.text
                page_translation.save()
            except Exception as e:
                import traceback
                mail_admins("Wiki fixdb error", e)
    return HttpResponse()
