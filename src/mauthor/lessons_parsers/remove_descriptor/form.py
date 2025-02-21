from django import forms


class RemoveAddonDescriptorsForm(forms.Form):
    lesson_id = forms.CharField(required=False)
    is_process_all_lessons = forms.BooleanField(initial=False, required=False, label="Process all lessons:")
    addon_descriptor = forms.CharField(required=True, label="Addon descriptor addonId")

    def clean_lesson_id(self):
        lesson_id = self.cleaned_data['lesson_id']
        return lesson_id

    def clean_is_process_all_lessons(self):
        is_process_all_lessons = self.cleaned_data['is_process_all_lessons']
        return is_process_all_lessons

    def clean_addon_descriptor(self):
        addon_descriptor = self.cleaned_data['addon_descriptor']
        return addon_descriptor