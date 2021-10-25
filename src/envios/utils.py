from collections import Counter
from typing import Callable, List, Tuple
from places.models import Partido, Town


ABBREVIATIONS = {
    "GRAL": "GENERAL",
    "GENERAL": "GRAL",
    "CNEL": "CORONEL",
    "CORONEL": "CNEL",
    "PTE": "PRESIDENTE",
    "PRESIDENTE": "PTE",
    "TTE": "TENIENTE",
    "TENIENTE": "TTE",
    "SGTO": "SARGENTO",
    "SARGENTO": "SGTO",
    "KM": "KILOMETRO",
    "KILOMETRO": "KM",
    "EST": "ESTACION",
    "ESTACION": "EST",
}


class NoSuggestionsAvailable(Exception):
    pass


def town_resolver(
        town: str, partido: str = None, zip_code: str = None) -> Town:
    resolver = TownSuggestionResolver(town, partido, zip_code)
    result = resolver.resolve()
    if not result:
        raise NoSuggestionsAvailable("Nothing found")
    return result
    #             la localidad con el nombre {cols[4]}


class TownSuggestionResolver:

    def __init__(self, town: str, zip_code: str = None, partido: str = None):
        self.town_name = town.upper()
        self.zip_code_num = zip_code.upper() if zip_code else None
        self.partido_name = partido.upper() if partido else None
        self.found_towns = []
        self.result = None
        self.next_step = self.__query_town_name

    def resolve(self) -> Town:
        self.__main_loop()
        return self.result

    def __main_loop(self):
        while self.next_step:
            towns, self.next_step = self.next_step()
            if towns:
                if len(towns) > 1:
                    self.found_towns.extend(towns)
                else:
                    self.result = towns[0]
                    self.next_step = None

    def __query_town_name(self) -> Tuple[List[Town], Callable]:
        towns = list(Town.objects.filter(name=self.town_name))
        print("Query town name with towns:", towns)
        return (towns, self.__query_town_name_and_partido)

    def __query_town_name_and_partido(self) -> Tuple[List[Town], Callable]:
        towns = list(
            Town.objects.filter(name=self.town_name,
                                partido__name=self.partido_name)
        )
        print("Query town name and partido with towns:", towns)
        return (towns, self.__query_cleaned_town_name)

    def __query_cleaned_town_name(self) -> Tuple[List[Town], Callable]:
        """Query Town's table with given town name.

        Args:
            town (str): the name we are looking for.

        Raises:
            NothingFound: if the query returns an
            empy django.db.models.query.QuerySet
            TooManyTowns: if the query returns more
            than one town.

        Returns:
            Town: the one found. Also, sets
            self.continue_searching to False, so
            the main loop stops.
        """
        self.town_name = self.town_name.replace(
            ".", "").replace("-", "").upper()
        towns = list(Town.objects.filter(name=self.town_name))
        print("Query cleaned town name:", towns)
        return (towns, self.__query_replacing_abbreviations)

    def __query_replacing_abbreviations(self) -> Tuple[List[Town], Callable]:
        town = self.town_name
        for key, value in ABBREVIATIONS.items():
            if key in town:
                town.replace(key, value)
        towns = list(Town.objects.filter(name=town))
        print("Query replacing abbreviations:", towns)
        return (towns, self.__query_postal_code)

    def __query_postal_code(self) -> Tuple[List[Town], Callable]:
        towns = None
        if self.zip_code_num:
            towns = list(Town.objects.filter(zip_code__code=self.zip_code_num))
        print("Query postal code:", towns)
        return (towns, self.__query_most_matching_name)

    def __query_most_matching_name(self) -> Tuple[List[Town], Callable]:
        town = self.town_name
        words = filter(lambda w: len(w) > 3, town.split(" "))
        towns = []
        for word in words:
            towns.extend(list(Town.objects.filter(name__contains=word)))
        if towns:
            counted = Counter(towns)
            ordered = counted.most_common()
            print(ordered)
            most_common = counted.most_common(1)[0][1]
            towns.clear()
            for item, score in ordered:
                if score == most_common:
                    towns.append(item)
                else:
                    break
        print("Query most matching name:", towns)
        return (towns, self.__query_found_towns_most_matching_name)

    def __query_found_towns_most_matching_name(
            self) -> Tuple[List[Town], Callable]:
        counted = Counter(self.found_towns)
        ordered = counted.most_common()
        most_common = counted.most_common(1)[0][1]
        self.found_towns.clear()
        for item, score in ordered:
            if score == most_common:
                self.found_towns.append(item)
            else:
                break
        print("Query found towns most matching name:", self.found_towns)
        return (self.found_towns, self.__query_partido_as_name)

    def __query_partido_as_name(self) -> Tuple[List[Town], Callable]:
        """Query Town's table with given partido name.

        Args:
            partido (str): the name of a partido, which
            we use to look for a town with that name.

        Raises:
            NothingFound: if the query returns an
            empy django.db.models.query.QuerySet
            TooManyTowns: if the query returns more
            than one town.

        Returns:
            Town: the one found.
        """
        towns = None
        if self.partido_name:
            query_name = self.partido_name.upper()
            towns = list(Town.objects.filter(name=query_name))
        print("Query partido as name:", towns)
        return (towns, self.__query_first_town_in_partido)

    def __query_first_town_in_partido(self):
        towns = []
        print("Query first town in partido:", towns)
        if self.partido_name:
            partidos = Partido.objects.filter(name=self.partido_name)
            if partidos:
                towns = partidos[0].town_set
                if towns:
                    towns.order_by("name")
        return (towns, None)
