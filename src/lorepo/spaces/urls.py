# libraries/wiki/urls.py

from django.urls import re_path
from libraries.wiki import views  # Regular views
from libraries.wiki.api import page, section, private_addon  # API views

urlpatterns = [
    # Regular views
    re_path(r'^$', views.index),  # Homepage for wiki
    re_path(r'^(?P<lang_code>[A-Za-z]{2})/?$', views.index),  # Language-specific homepage
    re_path(r'^add/?$', views.addPage),  # Add page view
    re_path(r'^page$', views.index),  # Page listing
    re_path(r'^page/index$', views.pageIndex),  # Specific page index
    re_path(r'^page/(?P<url>.+)$', views.index),  # Wiki page view
    re_path(r'^(?P<lang_code>[A-Za-z]{2})/page/(?P<url>.+)$', views.index),  # Language-specific page view
    re_path(r'^(?P<lang_code>[A-Za-z]{2})/(?P<highlight_word>.+)/page/(?P<url>.+)$', views.index),  # Highlighted page view
    re_path(r'^edit/(?P<page_id>\d+)$', views.edit),  # Edit page view
    re_path(r'^(?P<lang_code>[A-Za-z]{2})/edit/(?P<page_id>\d+)$', views.edit),  # Edit page with language code
    re_path(r'^upload/?$', views.upload),  # Upload page view
    re_path(r'^file/?$', views.add_file),  # File upload view
    re_path(r'^preview$', views.preview_page),  # Preview page view
    re_path(r'^table_of_contents$', views.table_of_contents),  # Table of contents view
    re_path(r'^remove_from_table_of_contents$', views.remove_from_toc),  # Remove page from TOC
    re_path(r'^edit_table_of_contents$', views.edit_toc),  # Edit TOC view
    re_path(r'^delete/(?P<page_id>\d+)$', views.delete),  # Delete page view
    re_path(r'^fixdb_reload_wiki$', views.fixdb_reload_wiki),  # Reload wiki from DB

    # API Views
    re_path(r'^api/(?P<lang_code>[A-Za-z]{2})/page/(?P<url>.+)$', page),  # Page API
    re_path(r'^api/(?P<lang_code>[A-Za-z]{2})/section/(?P<url>.+)$', section),  # Section API
    re_path(r'^api/private/(?P<content_id>\d+)$', private_addon),  # Private Addon API
]
