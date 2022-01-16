from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
import unidecode
from django.conf import settings
from django.shortcuts import render
from typing import Any, Dict, List
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


class CompleteListView(View):

    # Default results per page for pagination
    default_results_per_page = settings.DEFAULT_RESULTS_PER_PAGE

    # Default keywords for searching, ordering, filtering and pagination
    query_by_kw = 'query_by'
    order_by_kw = 'order_by'
    results_per_page_kw = 'results_per_page'
    page_kw = 'page'

    query_keywords = None
    default_order_by = None

    params_to_use = ("query", "order", "rpp", "pagination")

    paginate = False

    decoders = ()

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the view. Creates an empty context dictionary.

        Raises:
            ValueError: if the template is not specified
            ValueError: if the model is not specified.
        """
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'template_name') and type(
                self.template_name) is str:
            raise ValueError('A template_name should be specified as a str.')
        if not hasattr(self, 'model') and type(self.model) is None:
            raise ValueError('A model should be specified.')
        self.context = {}
        self.paginate = "pagination" in self.params_to_use
        self.pagination_url = ""

    def get(self, request) -> HttpResponse:
        """
        Overrides the get function which performs a get request.

        Gathers the model's objects and the context. It applies the
        filters and the ordering to the queryset when there are
        specified.

        Returns:
            HttpResponse: [description]
        """
        # Get the model's objects
        self.objects = self.model.objects.all()
        # Apply the filters and pass them to the self.context
        self.handle_filters_params(request)
        # Apply the main query as a filter and pass it to the self.context
        self.handle_query_param(request)
        # Apply the ordering and pass them to the self.context
        self.handle_order_param(request)
        # Map the objects with the queryset_map_callable and
        # pass it to the self.context
        self.objects = list(
            map(self.queryset_map_callable, self.objects.distinct()))
        # Apply the pagination and pass it to the self.context
        if self.paginate:
            self.handle_results_per_page_param(request)
            self.setup_pagination(request)
        # Return the response
        return render(request, self.template_name, self.get_context_data())

    def handle_query_param(self, request) -> None:
        """
        Apply the query param to the queryset and pass it to the self.context,
        when query_keywords is specified as a list or tuple. Also, appends
        the query param to the self.pagination_url if needed.

        Args:
            request (HttpRequest)

        Raises:
            ValueError: if a query_keywords is not a list or a
            tuple with str elements.
            ValueError: if a query_keyword is not a str.
        """
        # If the query keyword is in params to use.
        if "query" in self.params_to_use:
            # Get the query param
            query_by = request.GET.get(self.query_by_kw, None)
            # If found
            if query_by:
                print(query_by)
                # Pass is to the context
                self.context[self.query_by_kw] = query_by
                # Appends it to the self.url for pagination if needed
                if self.paginate:
                    self.pagination_url += f"{self.query_by_kw}={query_by}&"
                # Unidecode de query to remove accents
                query = unidecode.unidecode(
                    query_by.strip()) if query_by != '' else ''
                # If the query filters where specified
                # and there are a list or a tuple
                if (self.query_keywords is None or
                        not isinstance(self.query_keywords, (list, tuple))):
                    raise ValueError(
                        'query_keywords should be a list or a ' +
                        'tuple with at least one element.')
                # Create a Q object
                q_object = Q()
                # And for each kw append a Q object to the original one
                for kw in self.query_keywords:
                    # Only if the kw is a str
                    if not isinstance(kw, str):
                        err = "The query_keyword must be a str."
                        # Raise error if not
                        raise ValueError(err)
                    q_object |= Q(**{kw: query})
                # Filter the objects with the Q object
                self.objects = self.objects.filter(q_object)

    def handle_order_param(self, request) -> None:
        """
        Apply the order param to the queryset and pass it to the self.context.
        Also, appends the order param to the self.pagination_url if needed.

        Args:
            request ([type]): [description]

        Raises:
            ValueError: if order_by_kw is not a str.
        """
        # If the order keyword is in params to use.
        if "order" in self.params_to_use:
            # Get the order param
            order_by = request.GET.get(
                self.order_by_kw, self.default_order_by)
            # If found
            if order_by:
                # Raise error if not a str
                if not isinstance(self.order_by_kw, str):
                    raise ValueError("The order_by_kw must be a str.")
                # Pass is to the context
                self.context[self.order_by_kw] = order_by
                # Appends it to the self.url for pagination if needed
                if self.paginate:
                    self.pagination_url += f"{self.order_by_kw}={order_by}&"
                # Clean the order param. First, trim it
                cleaned = order_by.strip()
                # If _desc present
                if '_desc' in cleaned:
                    # Remove it and append a '-' to the start, which
                    # indicates descending order in the queryset
                    cleaned = '-' + cleaned.replace('_desc', '')
                # Orders the objects
                self.objects = self.objects.order_by(cleaned)

    def handle_results_per_page_param(self, request) -> None:
        """
        Apply the results_per_page param to the queryset and pass it to the
        self.context. Also, appends the results_per_page param to the
        self.pagination_url if needed.

        Args:
            request (HttpRequest)

        Raises:
            ValueError: if results_per_page_kw is not a str.
        """
        # If the results_per_page keyword is in params to use.
        if "rpp" in self.params_to_use:
            # Get the results_per_page param
            self.results_per_page = request.GET.get(
                self.results_per_page_kw, None)
            # If found
            if self.results_per_page:
                # Raise error if results_per_page_kw is not a str
                if not isinstance(self.results_per_page_kw, str):
                    raise ValueError(
                        "The results_per_page_kw must be a str, but " +
                        f"{type(self.results_per_page_kw)} was found.")
                # Pass is to the context
                self.context[self.results_per_page_kw] = self.results_per_page
                # Appends it to the self.url for pagination if needed
                if self.paginate:
                    rpp = self.results_per_page
                    self.pagination_url += f'{self.results_per_page_kw}={rpp}&'
            else:
                self.results_per_page = self.default_results_per_page

    def handle_filters_params(self, request) -> None:
        """
        Apply the filters params to the queryset and pass it
        to the self.context. Also, appends the filters params to the
        self.pagination_url if needed.

        Args:
            request (HttpRequest)

        Raises:
            ValueError: if decoders aren't specified as a tuple or
            list with dict elements.
            ValueError: if a filter_keyword is not a str.
        """
        # If the decoders where specified.
        if self.decoders is not None:
            # Initialize the filters dict
            filters = {}
            # Raise error if decoders isn't a tuple or list
            if (not isinstance(self.decoders, list) and
                    not isinstance(self.decoders, tuple)):
                raise ValueError(
                    "The decoders must be a list or tuple with dict elements.")
            # For each decoder
            for decoder in self.decoders:
                # For each expected kw
                for expected_key in ['key', 'filter', 'function', 'context']:
                    # Raise error if not found in decoder
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
                # Else, gets the value from the get request
                value = request.GET.get(decoder['key'], None)
                # If found
                if value is not None:
                    # Get the filter keyword
                    filter_key = call_or_it(decoder['filter'], value)
                    # Add the filter to filters with filter_key:value with
                    # the provided function applied
                    filters[filter_key] = decoder['function'](value)
                    # Add the filter to the context
                    self.context[decoder['key']] = decoder['context'](value)
                    # Appends it to the self.url for pagination if needed
                    if self.paginate:
                        self.pagination_url += f"{decoder['key']}={value}&"
            # If there are filters
            if filters:
                # Apply the filters to the queryset
                self.objects = self.objects.filter(**filters)

    def queryset_map_callable(self, obj) -> Any:
        """
        Transforms the object to whatever specified.

        Args:
            obj (Any): The object to transform, a model instance.

        Returns:
            Any: The result of the transformation.
        """
        return obj

    def setup_pagination(self, request) -> None:
        """
        Sets up the pagination for the response and triggers the passing
        of pagination data to the self.context and appends to the
        self.pagination_url str if needed.

        Args:
            request (HttpRequest)

        Raise:
            ValueError: if the page param is not an int.
        """
        # Gets the page param. If not found, use the default: 1
        page = request.GET.get(self.results_per_page_kw, 1)
        # If the page param is not a number or is strictly a str
        if not isinstance(page, int) or isinstance(page, str):
            # Try to convert it to an int
            try:
                int(page)
            # If it's not a number it raises a ValueError
            except ValueError:
                raise ValueError(
                    f"The page param must be an int, got {page}")
        # If the page param is a number or a str representing an integer
        # If the self.results_per_param exists (class level)
        if hasattr(self, 'results_per_page') and self.results_per_page is not None:
            # Update the results_per_page with the self.results_per_page
            results_per_page = self.results_per_page
        else:
            # Else, use the default
            results_per_page = self.default_results_per_page

        # Create a Paginator object with the queryset and the results_per_page
        objects_paginator = Paginator(self.objects, results_per_page)

        try:
            # Update the self.objects to contain the objects for the page
            self.objects = objects_paginator.page(page)

        # If the page param is not an int
        except PageNotAnInteger:
            # Return the page which equals the total results per page
            self.objects = objects_paginator.page(results_per_page)

        # If the page is empty
        except EmptyPage:
            # Return the last page
            num_pages = objects_paginator.num_pages
            self.objects = objects_paginator.page(num_pages)

        # Add the pagination data to the context
        self.add_pagination_data_to_context(objects_paginator)

    def add_pagination_data_to_context(self, page: Page) -> None:
        """
        Adds the pagination data to the self.context.

        Args:
            objects_paginator (Page): The page from the paginator object.
        """

        # How many objects are there?
        self.context['pagination_count'] = page.count

        # Showing first index object from total in this page
        self.context['pagination_from'] = (
            self.objects.number - 1) * page.per_page + 1

        # Showing last index object from total in this page
        if page.per_page > len(self.objects):
            what_to_sum = len(self.objects)
        else:
            what_to_sum = page.per_page
        # Showing last index object from total in this page
        self.context['pagination_to'] = self.context['pagination_from'] + \
            what_to_sum - 1

    def get_context_data(self) -> Dict[str, Any]:
        """
        Returns the context data for the get request.

        Returns:
            Dict[str, Any]: The context data.
        """
        # Add the Page or the QuerySet to the context
        self.context['objects'] = self.objects

        # Add the pagination url to the context
        if self.paginate:
            self.context['pagination_base_url'] = self.pagination_url
        # Returns the context data
        return self.context

    def get_pagination_base_url(
        self,
        query_by: str = "",
        order_by: str = "",
        results_per_page: int = None,
        **filters
    ) -> str:

        url = ""
        if query_by is not None and query_by != "":
            url += "query_by=" + query_by + "&"
        if order_by is not None and order_by != "":
            url += "order_by=" + order_by + "&"
        if (results_per_page is not None and
                results_per_page != self.default_results_per_page):
            url += "results_per_page=" + str(results_per_page) + "&"
        if filters:
            for key, value in filters.items():
                url += key + "=" + str(value) + "&"
        return url
