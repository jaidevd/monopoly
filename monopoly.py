import random
import coloredlogs
import logging
import locations as loc
import ccs

roll = lambda: random.randint(1, 6)  # noqa: E731
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
coloredlogs.install(level='INFO', logger=logger)


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

    def __repr__(self):
        return self.name

    def move(self, n):
        self.current_pos += n
        if self.current_pos > 39:
            self.current_pos -= 40
            self.balance += 200
            logger.info(f'{self.name} collected $200 salary.')
        location = loc.LOCATIONS[self.current_pos]
        logger.info(f'{self.name} moved {n} spaces to {location}.')
        self.transact(location)

    def move_to(self, location):
        if isinstance(location, str):
            location = [l for l in loc.LOCATIONS if l.name == location][0]
            n = location.index - self.current_pos
            if n < 0:
                n = 40 + n
            self.move_to(n)
        elif isinstance(location, int):
            self.move(location)

    def owns_group(self, color):
        siblings = get_siblings(color)
        return all([c.owner == self for c in siblings])

    def try_get_out_of_jail(self):
        if self.has_gojf:
            self.has_gojf = False
            self.in_jail = False
            logger.warning(f'{self} used a GOJF card to GOJF!')
        else:
            # choose between paying a fine and staying
            if random.choice([True, False]):
                # pay fine
                self.balance -= 50
                logger.warning(f'{self} paid a $50 fine to GOJ!')
                self.in_jail = False
                self.play_turn()
            else:
                self.goj_droll_attempt += 1
                if self.goj_droll_attempt < 4:
                    x, y = roll(), roll()
                    if x == y:
                        self.in_jail = False
                        logger.warning(f'{self} rolled doubles and GOJF!')
                        self.play_turn(x, y)
                else:
                    logger.warning(
                        f'{self} failed to get out of jail for 3 turns.')
                    self.balance -= 50
                    logger.warning(f'{self} paid a $50 fine to GOJ!')
                    self.in_jail = False
                    self.play_turn()

    def play_turn(self, *args):
        if self.in_jail:
            self.try_get_out_of_jail()
        if len(args) == 2:
            x, y = args
        else:
            x, y = roll(), roll()
        logger.info(f'{self.name} rolled {x} + {y} = {x + y}.')
        self.rolls.append((x, y))
        # check if this is the third doubles.
        if len(self.rolls) > 2:
            (x1, y1), (x2, y2) = self.rolls[-3:-1]
            if x1 == y1 and x2 == y2 and (x == y):
                logger.error(f'{self.name} rolled doubles thrice!')
                self.go_to_jail()
                logger.error(f'{self.name} went to jail!')
        self.move(x + y)
        if x == y:
            self.play_turn()

    def go_to_jail(self):
        logger.error(f'{self} went to Jail!')
        self.current_pos = 30
        self.in_jail = True

    def pay_rent(self, location, to='owner'):
        rent = location.rent
        self.balance -= rent
        if to == 'owner':
            location.owner.balance += rent
            logger.warning(
                (f'{self.name} paid ${rent} for ',
                 f'{location.name} to {location.owner.name}.'))
        else:
            logger.warning(
                f'{self.name} paid ${rent} for {location}.')

    def transact(self, location):
        if location.name == "Jail":
            self.in_jail = True
            logger.error(f'{self} went to jail!')
        elif location.for_sale:
            if not location.owner:
                if location.cost <= self.balance:
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
        self.check_colorgroup(location)
        logger.warning(
            f'{self.name} purchased {location.name} for ${location.cost}!')

    def check_colorgroup(self, location):
        color = getattr(location, 'color', False)
        if color:
            if color in ('blue', 'brown'):
                n_siblings = 2
            else:
                n_siblings = 3
            siblings = [c for c in self.properties if getattr(c, 'color', False) == color]
            if len(siblings) == n_siblings:
                logger.error(f'{self.name} owns the {color} group!')

    def draw_card(self, deck):
        card = deck.pop(0)
        deck.append(card)
        card.execute(self)


def get_siblings(color):
    return [c for c in loc.LOCATIONS if c.color == color]


def pick_starter(players):
    logger.info('Picking the first player...')
    maxRoll = 0
    currentPlayer = None
    for p in players:
        x, y = roll(), roll()
        logger.info(f'{p.name} rolled {x + y}.')
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


if __name__ == "__main__":
    n_turns = 100
    players = start_game('Alice Bob'.split())
    currentPlayer = pick_starter(players)
    while n_turns:
        currentPlayer.play_turn()
        currentPlayer = pick_next_player(currentPlayer, players)
        n_turns -= 1
