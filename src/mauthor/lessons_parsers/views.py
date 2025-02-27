import json

from django.contrib import messages
from django.http import  HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from src.libraries.utility.decorators import backend, SuperUserRequiredMixin
from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.queues import trigger_backend_task
from src.mauthor.lessons_parsers.form import ChangePropertiesForm
from src.mauthor.lessons_parsers.remove_descriptor.form import RemoveAddonDescriptorsForm
from src.mauthor.lessons_parsers.property_changer.properties_changer import PropertiesChanger
from src.mauthor.lessons_parsers.remove_descriptor.descriptors_cleaner import DescriptorsCleaner
from src.mauthor.localization.IcplayerZipped import IcplayerZipped
from src.mauthor.utility.decorators import LoginRequiredMixin


# noinspection PyMethodMayBeStatic
class ChangePropertiesView(SuperUserRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'lessons_parsers/change_properties.html'

    def post(self, request, space_id, *args, ** kwargs):
        form = ChangePropertiesForm(request.POST)
        form.fields['addon_name'].choices = self.__get_addons_and_modules()
        if form.is_valid():
            trigger_backend_task('/lessons_parsers/fix_properties_async/%s/%s' % (request.user.id, space_id),
                                 target=get_versioned_module('download'),
                                 queue_name='download',
                                 payload=json.dumps(form.cleaned_data))
            messages.info(request, 'Parser will run in background. You will be notified by email about the result')
            return HttpResponseRedirect('/mycontent')

        context = {
            'form': form,
            'space_id': space_id
        }
        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, space_id, *args, ** kwargs):
        form = ChangePropertiesForm()
        form.fields['addon_name'].choices = self.__get_addons_and_modules()
        return {
            'form': form,
            'space_id': space_id
        }

    def __get_addons_and_modules(self):
        tuples_list = []
        with IcplayerZipped() as player:
            modules_addons_list = player.get_modules_and_addons_list()

        for element in sorted(modules_addons_list, key=lambda s: s.lower()):
            tuples_list.append(('%s' % element, '%s' % element))
        return tuples_list


@backend
def fix_properties_async(request, user_id, space_id):
    properties_changer = PropertiesChanger(user_id, space_id, json.loads(request.body))
    properties_changer.change()
    return HttpResponse("ok")


class RemoveDescriptorsView(SuperUserRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'lessons_parsers/remove_descriptors.html'

    def get_context_data(self, space_id, *args, ** kwargs):
        form = RemoveAddonDescriptorsForm()
        return {
            'form': form,
            'space_id': space_id
        }

    def post(self, request, space_id, *args, ** kwargs):
        form = RemoveAddonDescriptorsForm(request.POST)
        if form.is_valid():
            trigger_backend_task('/lessons_parsers/remove_descriptors_async/%s/%s' % (request.user.id, space_id),
                                 target=get_versioned_module('download'),
                                 queue_name='download',
                                 payload=json.dumps(form.cleaned_data))
            messages.info(request, 'Process will run in background. You will be notified by email about the result')
        return HttpResponseRedirect('/mycontent')


@backend
def remove_descriptors_async(request, user_id, space_id):
    descriptors_cleaner = DescriptorsCleaner(user_id, space_id, json.loads(request.body))
    descriptors_cleaner.clean()
    return HttpResponse("ok")


