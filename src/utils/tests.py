from django.db.models.query import QuerySet
from django.db import models
from typing import Dict
from django.test import TestCase


class SampledDataTestCase(TestCase):

    SAMPLE_DATA = {}

    def setUp(self):
        if not self.SAMPLE_DATA:
            raise ValueError('SAMPLE_DATA must be defined')
        create_from_sample_data(self.SAMPLE_DATA)


def create_from_sample_data(sample: dict):
    """Create instances objects from sample data.
    Sample data needs to be in the following format for this to work:

    {
        <Class>: {
            'values': (
                {'property': <value>, 'property2': <value>, ...},
                ...
            ),
            'relations': {
                <property name in parent class>: <related Class>,
                ...
            },
        },
        ...
    }

    Args:
        sample (dict): the data needed to create the instances.
    """

    def replace_class_with_instance(
        relations: Dict[str, models.Model]
    ) -> Dict[str, QuerySet]:
        """Replaces the class model with an instance.

        Args:
            relations (Dict[str, models.Model]): key-value pairs containg
            property names and related classes.

        Returns:
            Dict[str, QuerySet]: key-value pairs containg property names
            and related instances.
        """
        result = {}
        for key, value_class in relations.items():
            result[key] = value_class.objects.first()
        return result

    for model_name, dict_data in sample.items():
        relations_dict = {}
        if relations := dict_data.get('relations', None):
            relations_dict = replace_class_with_instance(relations)
        for values_dict in dict_data.get('values'):
            model_class = model_name
            values_dict.update(relations_dict)
            model_class.objects.create(**values_dict)
    return True
