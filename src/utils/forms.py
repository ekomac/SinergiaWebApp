from django import forms
from django.forms.models import model_to_dict


class OnlyUpdatesError(Exception):
    pass


class CleanerMixin(forms.ModelForm):

    def clean_unique_or_error(self, key, error_msg):
        value = self.cleaned_data.get(key)
        if isinstance(value, str):
            value = value.strip()
        if self.Meta.model.objects.filter(**{key: value}).exists():
            error = error_msg
            if '{' in error_msg or '}' in error_msg:
                error = error_msg.format(value)
            raise forms.ValidationError(error)
        return value

    def clean_unique_beyond_instance_or_error(self, key, error_msg):
        # Cause we are updating, we need id
        # If there isn't, this isn't an update
        if id := self.instance.pk:
            # Get value for given key
            value = self.cleaned_data.get(key)
            if isinstance(value, str):
                value = value.strip()
            # If there isn't any database object with that value
            # for given property (given by the key)
            if self.Meta.model.objects.filter(**{key: value}).exists():
                # If value exists beyond the instance, it's because
                # it belongs to another instance.
                dict_model = model_to_dict(
                    self.Meta.model.objects.get(id=id))[key]
                if value != dict_model:
                    # So raise error
                    error = error_msg
                    if '{}' in error_msg:
                        error = error_msg.format(value)
                    raise forms.ValidationError(error)
            return value
        else:
            raise OnlyUpdatesError("This method only works for updating!")
