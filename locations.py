import logging
import random
import coloredlogs
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
coloredlogs.install(level='INFO', logger=logger)


class BaseLocation(object):
    for_sale = True
    owner = None

    def __init__(self, index, name, **kwargs):
        self.name = name
        self.index = index
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return self.name

    @property
    def rent(self):
        return 0


class Property(BaseLocation):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.is_mortgaged = False
        self.n_houses = self.n_hotels = 0
        self.owner = None

    def __repr__(self):
        return "{} owned by {} with {} houses and {} hotels".format(
            self.name, self.owner, self.n_houses, self.n_hotels
        )

    @property
    def is_developed(self):
        return self.n_hotels or self.n_houses

    def build_house(self):
        if self.n_houses < 4:
            self.n_houses += 1
            logger.warning(f'{self.owner.name} built a house on {self.name}!')
        else:
            raise Exception('Can\'t build more houses on {}'.format(self.name))

    def build_hotel(self):
        if self.n_hotels == 0:
            if self.n_houses == 4:
                self.n_hotels = 1
                logger.warning(
                    f'{self.owner.name} built a hotel on {self.name}!')
                self.n_houses = 0
            else:
                raise Exception('Need more houses.')
        else:
            raise Exception('Already have a hotel.')

    @property
    def rent(self):
        if self.owner:
            # calculate rent
            if self.is_mortgaged:
                rent = 0
            elif self.is_developed:
                if self.n_houses:
                    rent = self.house_rents[self.n_houses - 1]
                else:
                    rent = self.hotel_rent
            else:
                # is color group owned?
                siblings = self.get_siblings()
                if self.color in ('brown', 'blue'):
                    is_cg_owned = len(siblings) == 2
                else:
                    is_cg_owned = len(siblings) == 3
                if is_cg_owned:
                    rent = self.base_rent * 2
                else:
                    rent = self.base_rent
        else:
            rent = 0
        return rent

    def mortgage(self):
        if not self.is_mortgaged:
            self.is_mortgaged = True
            self.owner.balance += self.mortgage_value
            logger.warning(
                (f'{self.owner.name} mortgaged {self.name} ',
                 'for ${self.mortgage_value}!'))
        else:
            raise Exception('Property already mortgaged.')

    def unmortgage(self):
        if self.is_mortgaged:
            self.is_mortgaged = False
            unmortgage_cost = self.mortgage_value * 1.1
            self.owner.balance -= unmortgage_cost
            logger.warning(
                (f'{self.owner.name} unmortgaged {self.name} ',
                 'for ${unmortgage_cost}!'))
        else:
            raise Exception('Property not mortgaged!')

    def get_siblings(self):
        if self.owner:
            return [c for c in self.owner.properties if getattr(c, 'color', False) == self.color]
        return []


class IncomeTax(BaseLocation):
    for_sale = False

    @property
    def rent(self):
        return 200


class LuxuryTax(BaseLocation):
    for_sale = False

    @property
    def rent(self):
        return 100


class RailwayStation(BaseLocation):

    RENTS = [25, 50, 100, 200]
    cost = 200
    n_houses = 0
    n_hotels = 0

    def __repr__(self):
        return "{} owned by {}.".format(self.name, self.owner)

    def get_siblings(self):
        siblings = []
        if self.owner:
            for p in self.owner.properties:
                if isinstance(p, RailwayStation):
                    siblings.append(p)
        return siblings

    @property
    def rent(self):
        siblings = self.get_siblings()
        if len(siblings):
            return self.RENTS[len(siblings) - 1]


class UtilityCompany(BaseLocation):

    cost = 150
    n_houses = 0
    n_hotels = 0

    def get_siblings(self):
        siblings = []
        if self.owner:
            for p in self.owner.properties:
                if isinstance(p, UtilityCompany):
                    siblings.append(p)
        return siblings

    @property
    def rent(self):
        siblings = self.get_siblings()
        if len(siblings) == 1:
            rent = 4 * (random.randint(1, 7) + random.randint(1, 7))
        elif len(siblings) == 2:
            rent = 10 * (random.randint(1, 7) + random.randint(1, 7))
        else:
            raise Exception('This should not happen!')
        return rent


class Jail(BaseLocation):
    for_sale = False


class FreeParking(BaseLocation):
    for_sale = False

    @property
    def rent(self):
        return 0


class VisitingInJail(BaseLocation):
    for_sale = False

    @property
    def rent(self):
        return 0


class Card(BaseLocation):
    for_sale = False

    @property
    def rent(self):
        return 0


LOCATIONS = [
    BaseLocation(0, 'Go', for_sale=False),
    Card(2, 'Community Chest'),
    IncomeTax(4, 'Income Tax'),
    RailwayStation(5, 'King\'s Cross'),
    Card(7, 'Chance'),
    VisitingInJail(10, 'Visiting in Jail.'),
    UtilityCompany(12, 'Electric Company'),
    RailwayStation(15, 'Marylebone Station'),
    Card(17, 'Community Chest'),
    FreeParking(20, 'Free Parking'),
    Card(22, 'Chance'),
    RailwayStation(25, 'Fenchurch Station'),
    UtilityCompany(28, 'Water Works'),
    Jail(30, 'Jail'),
    Card(33, 'Community Chest'),
    RailwayStation(35, 'Liverpool Station'),
    Card(36, 'Chance'),
    LuxuryTax(38, 'Luxury Tax')
]

with open('locations.json', 'r') as fout:
    properties = json.load(fout)
LOCATIONS.extend([Property(**kwargs) for kwargs in properties])
LOCATIONS.sort(key=lambda x: x.index)
