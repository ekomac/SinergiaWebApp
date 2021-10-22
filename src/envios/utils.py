from collections import Counter
from typing import Callable
from django.db.models import Q
from places.models import ZipCode, Town


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
        self.town_name = town
        self.zip_code_num = zip_code
        self.partido_name = partido
        self.found_towns = []
        self.result = None
        self.next_step = self.__query_with_town_name
        self.attempts_left = 10
        self.continue_searching = True

    def resolve(self) -> Town:
        self.__main_loop()
        return self.__best_score_from_found()

    def __main_loop(self):
        # Buscar por nombre
        # Buscar por codigo postal
        # Buscar por nombre con partido
        # Buscar el mejor puntaje (mas veces que aparece + coincidencia de palabras)
        while self.next_step:
            self.next_step()

    def __update_vars(self, towns: list, next_step: Callable) -> None:
        self.next_step = next_step
        if towns:
            if len(towns) > 1:
                self.found_towns.extend(towns)
            else:
                self.result = towns[0]
                self.next_step = None

    def __query_with_town_name(self) -> None:
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
        self.__clean_town_name()
        town = self.town_name.upper()
        towns = Town.objects.filter(name=town)
        self.__update_vars(towns, self.__query_with_postal_code,
                           self.__query_with_partido_as_name)

    def __clean_town_name(self):
        self.town_name = self.town_name.replace(".", "")
        self.town_name = self.town_name.replace("-", "")
        self.next_step = self.__query_with_town_name
        return

    def __query_with_postal_code(self):
        towns = None
        if self.zip_code_num:
            zip_code = ZipCode.objects.filter(code=self.zip_code_num).first()
            towns = zip_code.towns.all()
        return self.__update_vars(towns, self.__query_with_partido_as_name)

    def __query_with_partido_as_name(self):
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
        return self.__update_vars(
            towns, self.__set_result_as_town_with_best_score)
        # towns = Town.objects.filter(name=town)
        # if not towns:
        #     raise PartidoIsNotTown(
        #         f"Nothing found with partido '{self.partido}' as town.")
        # if len(towns) > 1:
        #     raise TooManyTownsForPartidoName(
        #         f"Too many towns were found with name {town}")
        # return towns[0]

    def __set_result_as_town_with_best_score(self):
        if not self.found_towns:
            # ? TODO qué hacer cuando no hay nada encontrado?
            pass
        self.found_towns = Counter(self.found_towns)
        ordered = self.found_towns.most_common()
        most_found = ordered[0][0]
        pass

    def __set_points_for_matches(self):
        pass

    def __best_score_from_found(self):
        if self.result:
            return self.result
        if not self.found_towns:
            raise TownResolverNothingSolved(
                "Nothing found after trying everything.")
        counter = Counter(self.found_towns)
        return counter.most_common()[0][0]

    def perform_next_step(self, town_name: str,
                          postal_code: str = None, partido: str = None):
        # 1) Try to get a town with it's name
        if self.next_step == self.STEP_TOWN_WITH_NAME:
            town = self.town_with_name(town_name)

        # 2) Attemtp to match postal_code to a city
        elif self.next_step == self.STEP_TOWN_WITH_PARTIDO_AS_NAME:
            town = self.town_with_partido_as_name(partido)

        # 3) Attemtp to match postal_code to a city
        elif self.next_step == self.STEP_TOWN_WITH_PARTIDO_AS_NAME:
            town = self.town_with_partido_as_name(partido)
            self.found_towns.append(town)
        self.attempts_left -= 1

    def best_score_towns(self):
        self.__clean_town_name()
        town = self.town_name
        found = []
        for letter in town.split(" "):
            towns = Town.object.filter(Q(name__icontains=letter))
            if towns:
                found.extend(towns)
        if found:
            counter = Counter(found).most_common(1)
            as_list = counter.most_common()
            most_common = as_list[0][1]
            for key, value in counter:
                if value == most_common:
                    found.append(key)
                else:
                    break
            return found
        return None


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
