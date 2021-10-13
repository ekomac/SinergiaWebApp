from alerts.views import DeleteAlertMixin


class ContextMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for key, value in self.context.items():
            context[key] = value
        return context


class NotEnoughAttributes(Exception):
    pass


class DeleteObjectsUtil(DeleteAlertMixin):

    REPR_MALE = 'el'
    REPR_FEMALE = 'la'

    def __init__(
            self, model=None, model_ids='', order_by=None, request=None,
            selected_tab=None, gender_repr=None) -> None:

        self.model = model
        if not self.model:
            raise NotEnoughAttributes("A model args kwarg be specified.")

        self.request = request
        if not self.request:
            raise NotEnoughAttributes(
                "The request kwarg is mandatory.")

        self.model_ids = model_ids
        if self.model_ids == '':
            raise NotEnoughAttributes(
                "At least one model id must be given as kwarg.")

        try:
            self.verbose_name = self.model._meta.verbose_name
        except AttributeError:
            raise NotEnoughAttributes(
                'The model class must have verbose name in Meta class')

        try:
            self.verbose_name_plural = self.model._meta.verbose_name_plural
        except AttributeError:
            raise NotEnoughAttributes(
                'The model class must have verbose name plural in Meta class')

        self.selected_tab = selected_tab
        if not self.selected_tab:
            raise NotEnoughAttributes(
                "A tab selected kwarg must be specified.")
        if not order_by:
            raise NotEnoughAttributes(
                "The order_by is needed to perform the database query.")

        self.objects = self.model.objects.filter(
            pk__in=self.model_ids).order_by(order_by)
        self.names = [obj.__str__() for obj in self.objects]
        self.total_count = len(self.objects)
        self.gender_repr = gender_repr if gender_repr else self.REPR_MALE

    def get_context_data(self):
        context = {}
        context['objects'] = self.objects
        context['total_count'] = self.total_count
        context['selected_tab'] = self.selected_tab
        context['what_to_delete'] = self.__get_what_to_delete()
        return context

    def __get_what_to_delete(self):
        return f'{self.total_count} {self.__get_verbose_repr()}'

    def __get_verbose_repr(self):
        if self.total_count == 1:
            return self.verbose_name
        return self.verbose_name_plural

    def delete_objects(self):
        return self.objects.delete()

    def create_alert(self):

        action_word = 'eliminó'
        what = self.verbose_name.lower()
        repr_art = self.gender_repr

        # If we are talking plural
        if self.total_count > 1:
            action_word = 'eliminaron'
            what = self.verbose_name_plural.lower()

            # If the article at the sentence's beginning is male
            if self.gender_repr == self.REPR_MALE:
                repr_art = "los"
            # If the article at the sentence's beginning is female
            elif self.gender_repr == self.REPR_FEMALE:
                repr_art = "las"
            # If the article at the sentence's beginning is neither
            else:
                repr_art = "lxs"

        repr_art = repr_art.title()

        # Join names
        names = '", "'.join(self.names)

        # Create the message
        message = '{} {} "{}" se {} correctamente.'.format(
            repr_art, what, names, action_word)

        # Distpach the alert
        self.add_alert(message)
