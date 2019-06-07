import random
import colorlog
import json
import errors

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s: %(log_color)s%(message)s",
    style='%'
)
handler.setFormatter(formatter)
logger = colorlog.getLogger('monopoly')
logger.addHandler(handler)
logger.setLevel('DEBUG')


BS_COLORS = {
    "brown": "",
    "lightblue": "info",
    "pink": "",
    "orange": "",
    "red": "danger",
    "yellow": "warning",
    "green": "success",
    "blue": "primary"
}


class BaseLocation(object):
    for_sale = False
    owner = None
    color = ''

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
    for_sale = True
    owner = None

    def __init__(self, index, name, **kwargs):
        super(Property, self).__init__(index, name, **kwargs)
        self.is_mortgaged = False
        self.n_houses = 0
        self.has_hotel = False
        self.owner = None

    def serialize(self):
        return {
            'name': self.name,
            'owner': self.owner.name,
            'for_sale': self.for_sale,
            'n_houses': self.n_houses,
            'has_hotel': self.has_hotel,
            'is_mortgaged': self.is_mortgaged,
            'color': self.color,
            'rent': self.rent
        }

    def sell(self, to='bank'):
        if self.is_mortgaged:
            return
        if getattr(self, 'is_developed', False):
            logger.warning(f'Attempting to sell {self} which is developed.')
            return
        self.owner.balance += self.cost
        prev_owner = self.owner
        if to == 'bank':
            self.owner = None
        else:
            self.owner = to
            self.owner.balance -= self.cost
        logger.warning(f'{prev_owner} sold {self} to {to} for ${self.cost}!')

    def __repr__(self):
        return "{} owned by {} with {} houses and {} hotel".format(
            self.name, self.owner, self.n_houses, "a" if self.has_hotel else "no"
        )

    @property
    def is_developed(self):
        return self.has_hotel or self.n_houses

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
                siblings = self.get_colorgroup()
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
        if self.is_developed:
            logger.warning(f'Cannot mortgage developed property {self}!')
            return
        if not self.is_mortgaged:
            self.is_mortgaged = True
            self.owner.balance += self.mortgage_value
            logger.warning(f'{self.owner} mortgaged {self} for ${self.mortgage_value}! 💸')
        else:
            raise errors.AlreadyMortgagedError('Property already mortgaged!')

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

    def get_colorgroup(self):
        """Get a list of properties belonging to this colorgroup."""
        if self.owner:
            return [c for c in self.owner.properties if getattr(c, 'color', False) == self.color]
        return []


class DevelopableProperty(Property):
    is_developable = True

    @property
    def can_build_house(self):
        if self.has_hotel:
            return False
        if self.n_houses >= 4:
            return False
        # can build a house if self has the least number of houses on the block
        return self.n_houses == min([p.n_houses for p in self.get_colorgroup()])

    @property
    def can_build_hotel(self):
        if self.has_hotel or self.n_houses < 4:
            return False
        # each sibling should have either four houses or a hotel
        can_build = True
        for p in self.get_colorgroup():
            if p.name != self.name:
                if not(p.has_hotel or p.n_houses == 4):
                    can_build = False
                    break
        return can_build

    def build(self):
        if not self.has_hotel:
            if self.n_houses < 4:
                self.build_house()
            else:
                self.build_hotel()

    def build_house(self):
        built = False
        if self.is_mortgaged:
            from ipdb import set_trace; set_trace()  # NOQA
            logger.critical(f'Cannot build house as {self} is mortgaged!')
            return False
        if self.can_build_house:
            if self.owner.balance >= self.house_cost:
                self.n_houses += 1
                logger.warning(f'{self.owner.name} built a house on {self.name}! 🏠')
                self.owner.balance -= self.house_cost
                built = True
        return built

    def build_hotel(self):
        built = False
        if self.is_mortgaged:
            logger.critical(f'Cannot build house as {self} is mortgaged!')
            return False
        if self.can_build_hotel:
            self.has_hotel = True
            logger.warning(f'{self.owner.name} built a hotel on {self.name}! 🏨')
            self.n_houses = 0
            built = True
        return built

    def sell_structures(self):
        if self.has_hotel:
            self.sell_hotel()
        elif self.n_houses > 0:
            self.sell_house()

    def sell_hotel(self):
        self.has_hotel = False
        self.owner.balance += self.house_cost
        logger.warning(f'{self.owner} sold the hotel on {self.name} for ${self.house_cost}!')

    def sell_house(self):
        self.n_houses -= 1
        self.owner.balance += self.house_cost
        logger.warning(f'{self.owner} sold a house on {self.name} for ${self.house_cost}!')


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


class RailwayStation(Property):

    RENTS = [25, 50, 100, 200]
    cost = 200
    mortgage_value = 100
    color = 'railway'

    def __repr__(self):
        return "{} owned by {}.".format(self.name, self.owner)

    def get_colorgroup(self):
        siblings = []
        if self.owner:
            for p in self.owner.properties:
                if isinstance(p, RailwayStation):
                    siblings.append(p)
        return siblings

    @property
    def rent(self):
        siblings = self.get_colorgroup()
        if len(siblings):
            return self.RENTS[len(siblings) - 1]


class UtilityCompany(Property):

    cost = 150
    mortgage_value = 75
    color = 'utilityco'

    def get_colorgroup(self):
        siblings = []
        if self.owner:
            for p in self.owner.properties:
                if isinstance(p, UtilityCompany):
                    siblings.append(p)
        return siblings

    @property
    def rent(self):
        siblings = self.get_colorgroup()
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
LOCATIONS.extend([DevelopableProperty(**kwargs) for kwargs in properties])
LOCATIONS.sort(key=lambda x: x.index)
