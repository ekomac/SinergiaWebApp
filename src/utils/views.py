from django.db.models import Q
from multiprocessing import context
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import unidecode
from django.conf import settings
from django.shortcuts import render
from django.db import models
from typing import List
from django.views import View
from utils.alerts.views import SuccessfulDeletionAlertMixin
from utils.helpers import call_or_it


class ContextMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for key, value in self.context.items():
            context[key] = value
        return context


class NotEnoughAttributes(Exception):
    pass


class DeleteObjectsUtil(SuccessfulDeletionAlertMixin):

    REPR_MALE = 'el'
    REPR_FEMALE = 'la'

    def __init__(
        self,
        model=None,
        model_ids: List[int] = None,
        order_by=None,
        request=None,
        selected_tab=None,
        repr_as=None
    ) -> None:

        self.model = model
        if not self.model:
            raise NotEnoughAttributes("A model arg must be specified.")

        self.request = request
        if self.request is None:
            raise NotEnoughAttributes(
                "The request kwarg is mandatory.")

        self.model_ids = model_ids
        if self.model_ids is None:
            raise NotEnoughAttributes(
                "At least one model id must be given as kwarg.")
        if type(self.model_ids) is str or type(self.model_ids) is int:
            self.model_ids = [self.model_ids]

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
        self.gender_repr = repr_as if repr_as else self.REPR_MALE

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


def truncate_start(s: str, max_length=30) -> str:
    """Truncates the given string to the last <max_length> characters,
    unless it contains a slash, in which case it truncates to the last.

    Args:
        s (str): the string to be truncated.
        max_length (int): max chars in the resulting str. Defaults to 30.

    Returns:
        str: the truncated string.
    """
    if '/' in s:
        return ".../" + s[s.rfind('/') + 1:]
    elif len(s) > max_length:
        return "..." + s[-max_length:]
    return s


class ComplexListView(View):

    default_results_per_page = settings.DEFAULT_RESULTS_PER_PAGE
    query_by_kw = 'query_by'
    query_keywords = None
    order_by_kw = 'order_by'
    default_order_by = None
    results_per_page_kw = 'results_per_page'
    page_kw = 'page'
    params_to_use = ("query", "order", "rpp", "extras", "pagination")
    decoders = ()
    optional_context = None

    def __init__(self, *args, **kwargs) -> None:
        if not hasattr(self, 'template_name') and type(
                self.template_name) is str:
            raise ValueError('A template_name should be specified as a str.')
        if not hasattr(self, 'model') and type(self.model) is None:
            raise ValueError('A model should be specified.')
        self.context = {}

    def get(self, request, *args, **kwargs):
        self.objects = self.model.objects.all()
        self.handle_filters_params(request)
        self.handle_query_param(request)
        self.handle_order_param(request)
        self.objects = list(
            map(self.queryset_map_callable, self.objects.distint()))
        if "pagination" in self.params_to_use:
            self.handle_results_per_page_param(request)
            self.setup_pagination()
        return render(request, self.template_name, self.get_context_data())

    def handle_query_param(self, request):
        if "query" in self.params_to_use:
            query_by = request.GET.get(self.query_by_kw, None)
            if query_by:
                self.context[self.query_by_kw] = query_by
                query = unidecode.unidecode(query_by) if query_by != '' else ''
                # And the query filters where specified
                # and there are a list or a tuple
                if self.query_keywords is not None and (
                    isinstance(self.query_keywords, list) or
                        isinstance(self.query_keywords, tuple)):
                    # Create a Q object
                    q_object = Q()
                    # And for each kw append a Q object to the original one
                    for kw in self.query_keywords:
                        if not isinstance(kw, str):
                            err = "The query_keywords must be " +\
                                "a list or tuple of strs."
                            raise ValueError(err)
                        q_object |= Q(**{kw: query})
                    self.objects.filter(q_object)

    def handle_order_param(self, request):
        if "order" in self.params_to_use:
            order_by = request.GET.get(
                self.order_by_kw, self.default_order_by)
            if order_by:
                self.context[self.order_by_kw] = order_by
                self.objects = self.objects.order_by(order_by)

    def handle_results_per_page_param(self, request):
        if "rpp" in self.params_to_use:
            self.results_per_page = request.GET.get(
                self.results_per_page_kw, None)
            if self.results_per_page:
                self.context[self.results_per_page_kw] = self.results_per_page

    def handle_filters_params(self, request):
        if self.decoders is not None:
            filters = {}
            for decoder in self.decoders:
                for expected_key in ['key', 'filter', 'function', 'context']:
                    if expected_key not in decoder:
                        raise ValueError(
                            f"""
                            The decoder {decoder} must contain the
                            key '{expected_key}'.

                            The expected dict should be:
                            'key': str,
                            'filter': str or Callable[Any, Any],
                            'function': Callable[Any, Any],
                            'context': Callable[Any, str],
                            """)
                value = request.GET.get(decoder['key'], None)
                if value is not None:
                    filter_key = call_or_it(decoder['filter'], value)
                    filters[filter_key] = decoder['function'](value)
                    self.context[decoder['key']] = decoder['context'](value)
            if filters:
                self.objects = self.objects.filter(**filters)

    def queryset_map_callable(self, obj):
        return obj

    def end_model_queryset(self):
        self.objects = self.objects.distinct()
        return self.objects

    def setup_pagination(self, request):
        page = request.GET.get(self.results_per_page_kw, 1)
        if hasattr(self, 'results_per_page'):
            rpp = self.results_per_page
        else:
            rpp = self.default_results_per_page

        objects_paginator = Paginator(self.objects, rpp)

        try:
            self.objects = objects_paginator.page(page)
        except PageNotAnInteger:
            self.objects = objects_paginator.page(rpp)
        except EmptyPage:
            num_pages = objects_paginator.num_pages
            self.objects = objects_paginator.page(num_pages)

        self.add_paginator_to_context(objects_paginator)

    def add_paginator_to_context(self, objects_paginator):
        # How many objects are there?
        self.context['pagination_count'] = objects_paginator.count

        # Showing first index object from total in this page
        self.context['pagination_from'] = (
            self.objects.number - 1) * objects_paginator.per_page + 1

        # Showing last index object from total in this page
        if objects_paginator.per_page > len(self.objects):
            what_to_sum = len(self.objects)
        else:
            what_to_sum = objects_paginator.per_page
        self.context['pagination_to'] = self.context['paginaton_from'] + \
            what_to_sum - 1

    def get_context_data(self):
        self.context['objects'] = self.objects
        if self.query_by:
            self.context[self.query_by_kw] = self.query_by
        if self.order_by:
            self.context[self.order_by_kw] = self.order_by
        if self.results_per_page:
            self.context[self.results_per_page_kw] = self.results_per_page
        return self.context
