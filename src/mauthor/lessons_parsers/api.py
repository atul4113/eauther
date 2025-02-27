import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from src.lorepo.mycontent.models import Content
from src.mauthor.lessons_parsers.property_changer.parsers.parsers import ModuleParserFactory, AddonParser


@user_passes_test(lambda user: user.is_superuser)
@login_required
def get_properties(request):
    addon_module_name = request.POST.get('addon_module_name')
    module_parser_cls = ModuleParserFactory.get(addon_module_name)
    if module_parser_cls is None:
        module_parser_cls = AddonParser(name=addon_module_name)

    properties = module_parser_cls.parse_model()

    return HttpResponse(json.dumps(properties))


@user_passes_test(lambda user: user.is_superuser)
@login_required
def addon_exist(request):
    addon_name = request.POST.get('addon_module_name')
    get_object_or_404(Content, name=addon_name, content_type=3)
    return HttpResponse("OK")
