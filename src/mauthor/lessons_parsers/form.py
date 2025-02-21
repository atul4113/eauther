from django import forms
from django.core.exceptions import ValidationError
import re


class DynamicChoicePropertyField(forms.ChoiceField):
    def clean(self, value):
        return value


class ChangePropertiesForm(forms.Form):
    addon_name = DynamicChoicePropertyField(choices=(), required=False)
    addon_ID = forms.CharField(required=True)
    parse_all_addons = forms.BooleanField(initial=False, required=False, label="Parse all addons")
    property_name = DynamicChoicePropertyField(choices=(), required=True)
    list_row_number = forms.CharField(required=True)
    default_value = forms.CharField(required=False, label="Default Row Value")
    parse_all_rows = forms.BooleanField(initial=False, required=False, label="Parse all rows:")
    new_value = forms.CharField(required=True, widget=forms.Textarea)
    page_name = forms.CharField(required=True)
    parse_all_pages_name = forms.BooleanField(initial=False, required=False, label="Parse all pages name:")
    page_number = forms.CharField(required=True)
    parse_all_pages_numbers = forms.BooleanField(initial=False, required=False, label="Parse all pages numbers:")
    parse_commons = forms.BooleanField(initial=False, required=False, label="Parse only pages in commons")

    def clean_addon_name(self):
        addon_name = self.cleaned_data['addon_name']
        return addon_name

    def clean_list_row_number(self):
        row_number = self.cleaned_data['list_row_number']
        return self.validate_numbers(row_number)

    def clean_addon_ID(self):
        addon_id = self.cleaned_data['addon_ID']
        return self.escape_name_from_regex(addon_id)

    def clean_page_name(self):
        page_name = self.cleaned_data['page_name']
        return self.escape_name_from_regex(page_name)

    def clean_page_number(self):
        page_number = self.cleaned_data['page_number']
        return self.validate_numbers(page_number)

    def clean_property_name(self):
        property_name = self.cleaned_data['property_name']
        if property_name is None:
            raise ValidationError('Property must have name')
        return property_name

    def validate_numbers(self, value):
        if value.lower() == "all":
            return '[start-end]'

        # match: [<number_or_start>-<number_or_end>], [1-3] -> True, [afsdk;jafdas] -> Talse, [start-end] -> True
        #        [start-23] -> true, [23-end] -> true
        match = re.match("^\[(\d+|start)-(\d+|end)]$", value)
        if match:
            start = match.group(1)
            end = match.group(2)
            if start == 'start':
                start = 0

            if end == 'end':
                end = 'inf'
            if int(start) > float(end):
                raise ValidationError("First number can't be greater than second value")
            return value

        try:
            numbers = value.split(',')

            for number in numbers:
                if int(number) < 1:
                    raise ValidationError('Number must be natural number')

        except ValidationError as err:
            raise err
        except ValueError:
            raise ValidationError('Value must be in format "[<number_or_start>-<number_or_end>]" or "all" or "value1,value2,...,valueN"')

        return value

    def escape_name_from_regex(self, name):
        DISABLED_CHARS = set(["(", "*", "?", "|", "{", "+"])
        DISABLED_SEQUENCES = ["\\number", "\\A", "\\b", "\\B", "\\d", "\\D", "\\s", "\\S", "\\w", "\\W", "\\Z"]

        new_name = []
        for char in name:
            if char in DISABLED_CHARS:
                new_name.append("\\")
            new_name.append(char)

        new_name = "".join(new_name)
        for sequence in DISABLED_SEQUENCES:
            new_name = new_name.replace(sequence, "\\%s" % sequence)

        return new_name