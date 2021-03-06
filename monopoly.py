import os
import cmd
import random
import colorlog
import locations as loc
from logging import FileHandler
import ccs
from errors import AlreadyMortgagedError, EndGame

roll = lambda: random.randint(1, 6)  # noqa: E731

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s: %(log_color)s%(message)s",
    style='%'
)
if os.path.exists('log.txt'):
    os.remove('log.txt')
fh = FileHandler('log.txt', encoding='utf-8')
handler.setFormatter(formatter)
logger = colorlog.getLogger('monopoly')
logger.setLevel('DEBUG')
logger.addHandler(fh)


def _get_max_rate(c):
    """Get the cost of the most expensive property in the colorgroup `c`."""
    props = [p for p in loc.LOCATIONS if p.color == c]
    props.sort(key=lambda x: -x.cost)
    return props[0].cost


def is_cg_developed(properties):
    """Check if a colorgroup is fully developed."""
    # check validity of colorgroup
    assert len(set([c.color for c in properties])) == 1
    return all([c.has_hotel for c in properties])


def develop_colorgroup(c):
    """Attempt to build things on colorgroup `c`."""
    # check validity of colorgroup
    props = [p for p in loc.LOCATIONS if p.color == c]
    if any([p.is_mortgaged for p in props]):
        return
    if not getattr(props[0], 'is_developable', False):
        return
    assert len(set([p.owner.name for p in props])) == 1
    owner = props[0].owner
    out_of_cash = owner.balance < props[0].house_cost
    while not(is_cg_developed(props)) and not(out_of_cash):
        for p in props:
            if owner.balance >= p.house_cost:
                p.build()
            else:
                out_of_cash = True


def sell_structures(props):
    props.sort(key=lambda x: x.cost)
    while any([c.is_developed for c in props]):
        for p in props:
            p.sell_structures()


class Player(object):
    def __init__(self, name):
        self.name = name
        self.in_jail = False
        self.balance = 1500
        self.properties = []
        self.rolls = []
        self.current_pos = 0
        self.has_gojf = False
        self.goj_droll_attempt = 0
        self.greedy = True

    def serialize(self):
        return {
          'name': self.name,
          'in_jail': self.in_jail,
          'balance': self.balance,
          'properties': [p.serialize() for p in self.properties],
          'has_gojf': self.has_gojf,
          'colorgroups': self.get_owned_colorgroups()
        }

    def __repr__(self):
        return self.name

    def roll(self):
        x, y = roll(), roll()
        self.rolls.append((x, y))

    def move(self, n):
        self.current_pos += n
        if self.current_pos > 39:
            self.current_pos -= 40
            if n > 0:
                self.collect_salary()
        location = loc.LOCATIONS[self.current_pos]
        logger.info(f'{self.name} moved {n} spaces to {location}.')
        self.transact(location)

    def collect_salary(self):
        self.balance += 200
        logger.info(f'{self.name} collected $200 salary! 🤑')

    def move_to(self, location):
        if isinstance(location, str):
            location = [l for l in loc.LOCATIONS if l.name == location][0]
            n = location.index - self.current_pos
            if n < 0:
                n = 40 + n
            self.move_to(n)
        elif isinstance(location, int):
            self.move(location)

    def try_get_out_of_jail(self):
        if self.has_gojf:
            self.has_gojf = False
            self.in_jail = False
            logger.warning(f'{self} used a GOJF card to GOJF!')
            self._play_turn()
        else:
            # choose between paying a fine and staying
            if random.choice([True, False]):
                # pay fine
                self.balance -= 50
                logger.warning(f'{self} paid a $50 fine to GOJ!')
                self.in_jail = False
                self._play_turn()
            else:
                self.goj_droll_attempt += 1
                if self.goj_droll_attempt < 4:
                    logger.info(f'{self} attempts to roll doubles to GOJ.')
                    x, y = roll(), roll()
                    if x == y:
                        self.in_jail = False
                        logger.warning(f'{self} rolled doubles and GOJF!')
                        self._play_turn(x, y)
                else:
                    logger.warning(
                        f'{self} failed to get out of jail for 3 turns.')
                    self.balance -= 50
                    logger.warning(f'{self} paid a $50 fine to GOJ!')
                    self.in_jail = False
                    self._play_turn()

    def _play_turn(self, *args):
        # self.attempt_building()
        if self.in_jail:
            self.try_get_out_of_jail()
        if len(args) == 2:
            x, y = args
        else:
            x, y = roll(), roll()
        logger.info(f'{self.name} rolled {x} + {y} = {x + y}. 🎲')
        self.rolls.append((x, y))
        # check if this is the third doubles.
        if len(self.rolls) > 2:
            (x1, y1), (x2, y2) = self.rolls[-3:-1]
            if x1 == y1 and x2 == y2 and (x == y):
                logger.critical(f'{self.name} rolled doubles thrice! 💩')
                self.go_to_jail()
        self.move(x + y)
        logger.info(f'{self}\'s balance: ${self.balance}')
        if self.balance < 0:
            logger.critical(f'{self} is bankrupt! 😰')
            self.resolve_bankruptcy()
        if x == y:
            self._play_turn()

    def resolve_bankruptcy(self):
        self.attempt_mortgages()
        if self.balance < 0:
            self.attempt_sales()
        if self.balance < 0:
            try:
                assert len([c for c in self.properties if not c.is_mortgaged]) == 0
            except AssertionError:
                from ipdb import set_trace; set_trace()  # NOQA
            logger.critical(f'{self} is still bankrupt.  {self} loses. 💀')
            raise EndGame()

    def attempt_sales(self):
        if self.balance < 0:
            # look for utility companies
            ucs = [p for p in self.properties if isinstance(p, loc.UtilityCompany)]
            for p in ucs:
                p.sell()
                if self.balance >= 0:
                    break
        if self.balance < 0:
            # look for railway stations
            rls = [p for p in self.properties if isinstance(p, loc.RailwayStation)]
            for p in rls:
                p.sell()
                if self.balance >= 0:
                    break
        if self.balance < 0:
            # look for undeveloped properties
            properties = [p for p in self.properties if not p.is_developed]
            for p in properties:
                p.sell()
                if self.balance >= 0:
                    break
        if self.balance < 0:
            # sell houses - find the cheapest property left
            saleable_props = [p for p in self.properties if p.is_developed]
            if len(saleable_props) == 0:
                logger.critical(f'{self} has nothing left to mortgage or sell.')
            else:
                sell_structures(saleable_props)
        if self.balance < 0:
            # Attempt mortgages one last time
            self.attempt_mortgages()

    def attempt_mortgages(self):
        """Attempt to mortgage properties one by one until bankruptcy is resolved."""
        if self.balance < 0:
            # look for utility companies
            ucs = [p for p in self.properties if isinstance(p, loc.UtilityCompany)]
            self.mortgage_properties(ucs)
        if self.balance < 0:
            # look for railway stations
            rls = [p for p in self.properties if isinstance(p, loc.RailwayStation)]
            self.mortgage_properties(rls)
        if self.balance < 0:
            # look for undeveloped locations
            properties = [p for p in self.properties if isinstance(p, loc.Property)]
            properties = [p for p in properties if not p.is_developed]
            self.mortgage_properties(properties)

    def mortgage_properties(self, properties):
        """Mortgage properties until either bankruptcy is resolved or all are mortgaged."""
        properties.sort(key=lambda x: x.mortgage_value)
        for p in properties:
            try:
                p.mortgage()
                if self.balance >= 0:
                    break
            except AlreadyMortgagedError:
                continue

    def go_to_jail(self):
        logger.critical(f'{self} went to Jail! 👮')
        self.current_pos = 30
        self.in_jail = True

    def pay_rent(self, location, to='owner'):
        rent = location.rent
        self.balance -= rent
        if to == 'owner':
            location.owner.balance += rent
            logger.warning(
                f'{self.name} paid ${rent} for {location} to {location.owner}. 💰')
        else:
            logger.warning(
                f'{self.name} paid ${rent} for {location}. 💰')

    def transact(self, location):
        if location.name == "Jail":
            self.in_jail = True
            logger.critical(f'{self} went to Jail! 👮')
        elif location.for_sale:
            if not location.owner:
                if location.cost <= self.balance:
                    if self.greedy:
                        self.purchase(location)
            elif location.owner != self:
                self.pay_rent(location)
        else:
            # not for sale locations may have rents too
            if location.rent:
                self.pay_rent(location, None)
            elif location.name in ('Chance', 'Community Chest'):
                if location.name == 'Chance':
                    self.draw_card(self.chances)
                else:
                    self.draw_card(self.cs)

    def purchase(self, location):
        self.balance -= location.cost
        location.owner = self
        self.properties.append(location)
        logger.warning(
            f'{self.name} purchased {location.name} for ${location.cost}! 💵')
        if self.has_colorgroup(location):
            logger.critical(f'{self} owns the {location.color} group! 🎩')

    def has_colorgroup(self, location):
        """Check if the `color` group belongs to the player."""
        cg = location.get_colorgroup()
        if isinstance(location, loc.DevelopableProperty):
            if location.color in ('blue', 'brown'):
                return len(cg) == 2
            return len(cg) == 3
        if isinstance(location, loc.UtilityCompany):
            utilities_owned = [c for c in self.properties if isinstance(c, loc.UtilityCompany)]
            return len(utilities_owned) == 2
        if isinstance(location, loc.RailwayStation):
            utilities_owned = [c for c in self.properties if isinstance(c, loc.RailwayStation)]
            return len(utilities_owned) == 4
        return False

    def get_owned_colorgroups(self):
        owned_colorgroups = set()
        for p in self.properties:
            if p.color not in owned_colorgroups:
                if self.has_colorgroup(p):
                    owned_colorgroups.add(p.color)
        return list(owned_colorgroups)

    def attempt_building(self):
        owned_cg = self.get_owned_colorgroups()
        if len(owned_cg) == 0:
            return
        if self.greedy:
            owned_cg.sort(key=lambda x: -_get_max_rate(x))
        else:
            random.shuffle(owned_cg)
        for c in owned_cg:
            develop_colorgroup(c)

    def draw_card(self, deck):
        card = deck.pop(0)
        deck.append(card)
        card.execute(self)


def pick_starter(players):
    logger.info('Picking the first player...')
    maxRoll = 0
    currentPlayer = None
    x = y = 0
    for p in players:
        x, y = roll(), roll()
        logger.info(f'{p.name} rolled {x + y}. 🎲')
        if x + y > maxRoll:
            currentPlayer = p
            maxRoll = x + y
    logger.warning(f'{currentPlayer.name} starts the game!')
    return currentPlayer


def pick_next_player(current_player, players):
    for i, p in enumerate(players):
        if p.name == current_player.name:
            break
    try:
        nextPlayer = players[i + 1]
    except IndexError:
        nextPlayer = players[0]
    return nextPlayer


def start_game(players):
    players = [Player(n) for n in players]
    chances, cs = ccs.init(logger, players)
    for p in players:
        p.chances = chances
        p.cs = cs
    return players


class Console(cmd.Cmd):
    intro = """Welcome to the Monopoly console. Start the game by typing:
    start player1 player2
    """
    prompt = '🎩 > '

    def show_player_options(self):
        if loc.for_sale:
            print(f'{loc.name} is for sale!')

    def do_exit(self, arg):
        return True

    do_EOF = do_exit

    def do_start(self, arg):
        """Start the game by adding a list of players."""
        self.players = start_game(arg.split())
        for p in self.players:
            p.greedy = False
        self.pdict = {c.name: c for c in self.players}
        self.current_player = pick_starter(self.players)
        print(f'Type play to continue.')

    def do_buy(self, *args):
        """Buy a property."""
        p = self.current_player
        location = loc.LOCATIONS[p.current_pos]
        p.purchase(location)

    def do_play(self, *args):
        """Move a player by rolling dice and see other options."""
        p = self.current_player
        x, y = roll(), roll()
        p.rolls.append((x, y))
        if x == y:
            logger.warning(f'{p} rolled doubles!')
            # check if this is the third roll:
            if len(p.rolls) > 2:
                (x1, y1), (x2, y2) = self.rolls[-3:-1]
                if x1 == y1 and x2 == y2:
                    logger.critical(f'{p} rolled doubles thrice! 💩')
                    p.go_to_jail()
                    return
            p.move(x + y)

            self.current_player = p
            return
        self.current_player.move(x + y)
        self.current_player = pick_next_player(self.current_player, self.players)
        print(f'{self.current_player} goes next.')
        print(f'Type play {self.current_player} continue.')

    do_p = do_play


class Game(object):

    def __init__(self):
        self.players = {}

    def add_player(self, p):
        self.players[p.name] = p

    def add_players(self, *args):
        for p in args:
            self.add_player(p)

    def play(self, player):
        self.players[player]._play_turn()

    def pick_next_player(self, player):
        return pick_next_player(self.players[player], list(self.players.values())).name


if __name__ == "__main__":
    # Console().cmdloop()
    max_turns = 100
    current_turn = 1
    players = start_game('Alice Bob'.split())
    currentPlayer = pick_starter(players)
    while current_turn <= max_turns:
        logger.debug('Turn {} starts.'.format(current_turn))
        currentPlayer._play_turn()
        currentPlayer = pick_next_player(currentPlayer, players)
        logger.debug('Turn {} ends.'.format(current_turn))
        current_turn += 1
