import re
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from src.libraries.utility.decorators import backend
from src.libraries.wiki.forms import WikiPageForm, WikiPageTranslatedForm
from src.libraries.wiki.models import WikiPage, WikiFile, WikiPageTranslated
from src.libraries.wiki.util import make_url, has_access_to_wiki
from src.lorepo.filestorage.forms import UploadForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from src.mauthor.utility.db_safe_iterator import safe_iterate
import datetime


def index(request, url=None, lang_code=None, highlight_word=''):
    """
    Main view for the wiki index page.
    """
    no_menu = 'no_menu' in request.GET
    user = request.user

    if not lang_code:
        lang_code = settings.LANGUAGE_CODE
        if user.is_authenticated:
            lang_code = user.profile.language_code
        if url:
            return HttpResponsePermanentRedirect(f'/doc/{lang_code}/page/{url}' + ('?no_menu' if no_menu else ''))
        else:
            return HttpResponsePermanentRedirect(f'/doc/{lang_code}')

    if user.is_staff or user.is_superuser:
        lang_code = WikiPageTranslated.validated_language_code(lang_code, settings.LANGUAGES)
    else:
        lang_code = WikiPageTranslated.validated_language_code(lang_code)

    toc = WikiPageTranslated.toc_pages(lang_code)

    if not url and toc:
        url = toc[0]['url']
    selected_page = WikiPageTranslated.page_for_url(url, lang_code)

    if not selected_page and url:
        return HttpResponseRedirect(f'/doc/add?title={url}')

    context = {
        'toc_pages': toc,
        'selected_page': selected_page,
        'lang_code': lang_code,
        'languages': None,
        'page_url': url,
        'highlight_word': highlight_word,
        'no_menu': no_menu,
    }

    if user.is_authenticated and (user.is_staff or user.is_superuser):
        context['languages'] = [lang[0] for lang in settings.LANGUAGES]

    return render(request, 'wiki/index.html', context)


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def edit_toc(request):
    """
    View to edit the table of contents.
    """
    WikiPageTranslated.flush_toc()
    wiki_pages = WikiPageTranslated.objects.filter(parent=None, is_toc=True, language_code='en').order_by('order')
    for page in wiki_pages:
        page.load_kids()
    pages = WikiPageTranslated.objects.filter(is_toc=False, language_code='en')
    return render(request, 'wiki/edit_toc.html', {'wiki_pages': wiki_pages, 'pages': pages})


def preview_page(request):
    """
    View to preview a wiki page.
    """
    if request.method == 'POST':
        page = WikiPageTranslated(title=request.POST['title'], text=request.POST['text'])
        return render(request, 'wiki/preview.html', {'page': page})
    raise Http404


def pageIndex(request):
    """
    View to display the wiki index page.
    """
    if not WikiPageTranslated.objects.exists():
        if not has_access_to_wiki(request.user):
            raise Http404
        return HttpResponseRedirect('/doc/add')

    page = WikiPageTranslated.objects.first()
    if WikiPageTranslated.objects.filter(is_toc=True).exists():
        page = WikiPageTranslated.objects.filter(is_toc=True).first()
    return render(request, 'wiki/page.html', {'page': page})


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def addPage(request):
    """
    View to add a new wiki page.
    """
    title = request.GET.get('title')
    if request.method == 'POST':
        form = WikiPageForm(request.POST)
        if form.is_valid():
            page = WikiPageTranslated(
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                url=make_url(form.cleaned_data['title']),
                modified_date=datetime.datetime.now(),
                author=request.user,
                language_code='en'
            )
            page.save()
            page.clone_for_languages(settings.LANGUAGES)
            messages.info(request, f"Page {page.title} has been added.")
            return HttpResponseRedirect('/doc')
        return render(request, 'wiki/addpage.html', {'form': form})
    return render(request, 'wiki/addpage.html', {'title': title})


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def edit(request, page_id):
    """
    View to edit an existing wiki page.
    """
    page = get_object_or_404(WikiPageTranslated, pk=page_id)
    if request.method == 'POST':
        form = WikiPageTranslatedForm(request.POST)
        if form.is_valid():
            page.title = form.cleaned_data['title']
            page.text = form.cleaned_data['text']
            page.modified_date = datetime.datetime.now()
            if page.language_code == 'en':
                url = make_url(form.cleaned_data['title'])
                for trans_page in page.get_translations().values():
                    trans_page.url = url
                    trans_page.save()
            else:
                page.save()
            messages.info(request, f"Page {page.title} has been edited.")
            WikiPageTranslated.flush_toc()
            return HttpResponseRedirect(f'/doc/{page.language_code}/page/{page.url}')
        return render(request, 'wiki/edit.html', {'page': page, 'form': form})
    return render(request, 'wiki/edit.html', {'page': page})


@login_required
def upload(request):
    """
    View to handle file uploads for the wiki.
    """
    if request.method == 'POST':
        if 'file' in request.FILES:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file']
                file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
                model = form.save(commit=False)
                model.owner = request.user
                model.content_type = uploaded_file.content_type
                model.file = file_name
                model.save()
                wf = WikiFile(uploaded_file=model)
                wf.save()
                messages.info(request, "New file has been uploaded.")
                next_url = form.cleaned_data.get('next', '/doc')
                return HttpResponseRedirect(next_url)
        return HttpResponseRedirect('/doc/upload?next=' + request.POST.get('next', '/doc'))
    else:
        form = UploadForm()
        return render(request, 'wiki/upload.html', {
            'form': form,
            'next': request.GET.get('next', '/doc'),
        })


@login_required
def add_file(request):
    """
    View to display uploaded files.
    """
    wiki_files = WikiFile.objects.all()
    files = [wf.uploaded_file for wf in wiki_files]
    return render(request, 'wiki/add_file.html', {'files': files})


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def table_of_contents(request):
    """
    View to update the table of contents.
    """
    items_list = request.POST
    order = request.POST.get('order')
    if order:
        order = order.split(',')
        for i, wiki_id in enumerate(order):
            wiki = WikiPageTranslated.objects.get(pk=wiki_id)
            parent_id = items_list.get(f'list[{wiki_id}]')
            parent = None if parent_id == 'root' else WikiPageTranslated.objects.get(pk=parent_id)
            wiki.parent = parent
            wiki.order = i
            wiki.is_toc = True
            wiki.save()
        messages.info(request, 'Table of contents has been saved.')
        WikiPageTranslated.flush_toc()
    return HttpResponse('OK')


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def remove_from_toc(request):
    """
    View to remove a page from the table of contents.
    """
    items_to_remove = request.POST
    for key in items_to_remove:
        if key.startswith('list['):
            wiki_id = re.search(r'\d+', key).group()
            wiki = WikiPageTranslated.objects.get(pk=wiki_id)
            wiki.is_toc = False
            wiki.parent = None
            wiki.save()
    return HttpResponse('OK')


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@login_required
def delete(request, page_id):
    """
    View to delete a wiki page.
    """
    wiki = get_object_or_404(WikiPageTranslated, pk=page_id)
    for child in wiki.kids.all():
        child.parent = None
        child.order = None
        child.is_toc = False
        child.save()
    wiki.delete()
    messages.info(request, f"{wiki.title} has been removed.")
    WikiPageTranslated.flush_toc()
    return HttpResponseRedirect('/doc')


@user_passes_test(lambda user: user.is_superuser or user.is_staff)
@backend
def fixdb_reload_wiki(request):
    """
    View to reload wiki pages from the database.
    """
    wiki_query = WikiPage.objects.all()
    for pages in safe_iterate(wiki_query):
        for page in pages:
            try:
                page_translation = WikiPageTranslated.objects.get(url=page.url, language_code='en')
                page_translation.text = page.text
                page_translation.save()
            except Exception as e:
                mail_admins("Wiki fixdb error", str(e))
    return HttpResponse()