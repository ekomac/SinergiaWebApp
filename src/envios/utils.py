from collections import Counter
from typing import Callable, List, Tuple
from django.db.models import Q
from places.models import Partido, ZipCode, Town


ABBREVIATIONS = {
    'GRAL': 'GENERAL',
    'GENERAL': 'GRAL',
    'CNEL': 'CORONEL',
    'CORONEL': 'CNEL',
    'PTE': 'PRESIDENTE',
    'PRESIDENTE': 'PTE',
    'TTE': 'TENIENTE',
    'TENIENTE': 'TTE',
    'SGTO': 'SARGENTO',
    'SARGENTO': 'SGTO',
    'KM': 'KILOMETRO',
    'KILOMETRO': 'KM',
    'EST': 'ESTACION',
    'ESTACION': 'EST',
}


class NothingFound(Exception):
    pass


class TooManyTowns(Exception):
    pass


class PartidoIsNotTown(Exception):
    pass


class TooManyTownsForPartidoName(Exception):
    pass


class TownResolverNothingSolved(Exception):
    pass


def town_resolver(town_name: str,
                  postal_code: str = None, partido: str = None) -> Town:
    pass


class TownSuggestionResolver:

    def __init__(self, town: str,
                 zip_code: str = None, partido: str = None):
        self.town_name = town.upper()
        self.zip_code_num = zip_code.upper()
        self.partido_name = partido.upper()
        self.found_towns = []
        self.result = None
        self.next_step = self.__query_with_cleaned_town_name
        self.attempts_left = 10
        self.continue_searching = True

    def resolve(self) -> Town:
        self.__main_loop()
        return self.__best_score_from_found()

    def __main_loop(self):
        # Buscar por nombre igual
        # Buscar reemplazando abreviaturas
        # Buscar por codigo postal
        # Localidad con más palabras coincidentes mayores a 3 letras (s/artículos)
        # Buscar por nombre con partido
        # Buscar el mejor puntaje (mas veces que aparece + coincidencia de palabras)
        # Primera localidad del partido
        while self.next_step:
            towns, self.next_step = self.next_step()
            if towns:
                if len(towns) > 1:
                    self.found_towns.extend(towns)
                else:
                    self.result = towns[0]
                    self.next_step = None

    def __query_with_cleaned_town_name(self) -> Tuple[List[Town], Callable]:
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
        towns = Town.objects.filter(name=self.town_name)
        return (towns, self.__query_replacing_abbreviations)

    def __query_replacing_abbreviations(self) -> Tuple[List[Town], Callable]:
        town = self.town_name
        for key, value in ABBREVIATIONS.items():
            if key in town:
                town.replace(key, value)
        towns = Town.objects.filter(name=town)
        return (towns, self.__query_with_postal_code)

    def __query_with_postal_code(self) -> Tuple[List[Town], Callable]:
        towns = None
        if self.zip_code_num:
            zip_code = ZipCode.objects.filter(code=self.zip_code_num).first()
            towns = zip_code.towns.all()
        # return self.__update_vars(towns, self.__query_most_matching_name)
        return (towns, self.__query_most_matching_name)

    def __query_most_matching_name(self) -> Tuple[List[Town], Callable]:
        town = self.town_name
        words = filter(lambda w: len(w) > 3, town.split(" "))
        towns = []
        for word in words:
            towns.extend(Town.objects.filter(name__contains=word))
        counted = Counter(towns)
        ordered = counted.most_common()
        most_common = ordered[0][1]
        towns.clear()
        for item, score in ordered:
            if score == most_common:
                towns.append(item)
            else:
                break
        return (towns, self.__query_with_partido_as_name)

    def __query_with_partido_as_name(self) -> Tuple[List[Town], Callable]:
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
            towns = Town.objects.filter(name=query_name)
        return (towns, self.__set_result_as_town_with_best_score)

    def __query_best_town_from_found(self):
        if self.found_towns:
            counted = Counter(self.found_towns)
            return ([counted.most_common(1)[0][0]],
                    self.__query_with_partido_as_name)

    def __query_first_town_in_partido(self):
        if self.partido_name:
            partidos = Partido.objects.filter(name=self.partido_name).first()
            if partidos:
                towns = partidos.first().town_set.all()
                if towns:
                    towns.order_by("name").first()

    def __set_result_as_town_with_best_score(self):
        if not self.found_towns:
            # ? TODO qué hacer cuando no hay nada encontrado?

            pass
        self.found_towns = Counter(self.found_towns)
        ordered = self.found_towns.most_common()
        most_found = ordered[0][0]
        pass

    def __query_first_town_from_partido(self):
        pass


def town_resolver(
        town_name: str, postal_code: str = None, partido: str = None) -> Town:

    town = None
    step = STEP_TOWN_WITH_NAME
    attempts_left = 10
    while not town and attempts_left > 0:
        try:

            # 1) Try to get a town with it's name
            if step == STEP_TOWN_WITH_NAME:
                town = town_with_name(town_name)

            # 2) Attemtp to match postal_code to a city
            elif step == STEP_TOWN_WITH_PARTIDO_AS_NAME:
                town = town_with_partido_as_name(partido)

            # 3) Attemtp to match postal_code to a city
            elif step == STEP_TOWN_WITH_PARTIDO_AS_NAME:
                town = town_with_partido_as_name(partido)

        except NothingFound:
            step = STEP_TOWN_WITH_PARTIDO_AS_NAME
        except TooManyTowns:
            # ! TODO update step
            pass
        except PartidoIsNotTown:
            # ! TODO update step
            pass
        except TooManyTownsForPartidoName:
            # ! TODO update step
            pass
        attempts_left -= 1

    print(town)

    # ? 3) Check partido is, in fact, a town

    # ? 4) Split town into parts, and get the town
    # ?    that gets best matches

    # ? 4) Split partido into parts, and get the town
    # ?    that gets best matches

    # towns = Town.objects.filter(name=cols[4].upper())
    # print(towns)
    # if not towns:
    #     error = forms.ValidationError(
    #         f"En la fila {i}, columna 4, no se encontró \
    #             la localidad con el nombre {cols[4]}")
    #     errors.append(error)
    # elif len(towns) > 1:
    #     towns = Town.objects.filter(
    #         name=cols[4].upper(), partido__name=cols[5].upper())
    #     if not towns:
    #         error = forms.ValidationError(
    #             f"En la fila {i}, columna 4, se indicó una localidad que \
    #                 pertenece a más de un partido. Tratamos de \
    #                     especificar una con el partido {cols[5]}, \
    #                         pero este partido no se encontró.")
    #         errors.append(error)
    # t = Town()


def town_with_name(town: str) -> Town:
    """Query Town's table with given town name.

    Args:
        town (str): the name we are looking for.

    Raises:
        NothingFound: if the query returns an
        empy django.db.models.query.QuerySet
        TooManyTowns: if the query returns more
        than one town.

    Returns:
        Town: the one found.
    """
    town = town.upper()
    towns = Town.objects.filter(name=town)
    if not towns:
        raise NothingFound(f"Nothing found with {town}.")
    if len(towns) > 1:
        raise TooManyTowns(f"Too many towns were found with name {town}")
    return towns[0]


def town_with_partido_as_name(partido: str) -> Town:
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
    town = partido.upper()
    towns = Town.objects.filter(name=town)
    if not towns:
        raise PartidoIsNotTown(
            f"Nothing found with partido '{partido}' as town.")
    if len(towns) > 1:
        raise TooManyTowns(f"Too many towns were found with name {town}")
    return towns[0]
