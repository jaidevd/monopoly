import random


class ChanceCommunityChest(object):

    def __init__(self, logger, players):
        self.logger = logger
        self.players = players

    def log(self, player):
        self.logger.warn(f'{player.name} drew a card:')
        self.logger.warn(self.__doc__)

    def execute(self, player):
        self.log(player)


class Chance1(ChanceCommunityChest):
    """Speeding fine: $15"""

    def execute(self, player):
        self.log(player)
        player.balance -= 15
        self.logger.warn(f'{player.name} paid $15 in speeding fine.')


class Chance2(ChanceCommunityChest):
    """Go back 3 spaces."""

    def execute(self, player):
        self.log(player)
        player.move(-3)


class Chance3(ChanceCommunityChest):
    """Advance to Mayfair"""

    def execute(self, player):
        self.log(player)
        player.move_to('Mayfair')


class Chance4(ChanceCommunityChest):
    """Bank pays dividend of 50."""

    def execute(self, player):
        self.log(player)
        player.balance += 50
        self.logger.warn(f'{player} collects dividend of $50.')


class Chance5(ChanceCommunityChest):
    """Go to Marylebone, if you pass go, collect 200"""

    def execute(self, player):
        self.log(player)
        player.move_to('Marylebone Station')


class Chance6(ChanceCommunityChest):
    """Advance to Go, collect 200"""

    def execute(self, player):
        self.log(player)
        player.move_to('Go')


class Chance7(ChanceCommunityChest):
    """Get out of Jail Free"""

    def execute(self, player):
        self.log(player)
        self.logger.warn(f'{player} gets a get out of jail free card!')
        player.has_gojf = True


class Chance8(ChanceCommunityChest):
    """Building loan matures, receive 150"""

    def execute(self, player):
        self.log(player)
        player.balance += 150
        self.logger.warn(f'{player} collects $150!')


class Chance9(ChanceCommunityChest):
    """Advance to Pall Mall, if you pass go collect 200"""

    def execute(self, player):
        self.log(player)
        player.move_to('Pall Mall')


class Chance10(ChanceCommunityChest):
    """Make general repairs - 25 per house, 100 per hotel"""

    def execute(self, player):
        self.log(player)
        n_houses = 0
        n_hotels = 0
        for p in player.properties:
            n_houses += p.n_houses
            n_hotels += p.n_hotels
        cost = (n_hotels * 100) + (n_houses * 25)
        player.balance -= cost
        self.logger.warn(f'{player} made general repairs worth ${cost}.')


class Chance11(ChanceCommunityChest):
    """Street repairs - 40 per house, 115 per hotel"""

    def execute(self, player):
        self.log(player)
        n_houses = 0
        n_hotels = 0
        for p in player.properties:
            n_houses += p.n_houses
            n_hotels += p.n_hotels
        cost = (n_hotels * 115) + (n_houses * 40)
        player.balance -= cost
        self.logger.warn(f'{player} made street repairs worth ${cost}.')


class Chance12(ChanceCommunityChest):
    """school fees 150"""

    def execute(self, player):
        self.log(player)
        player.balance -= 150
        self.logger.warn(f'{player} paid school fees of $150.')


class Chance13(ChanceCommunityChest):
    """Go to Trafalgar Square, if you pass go, collect 200"""

    def execute(self, player):
        self.log(player)
        player.move_to('Trafalgar Square')


class Chance14(ChanceCommunityChest):
    """You've won a crossword competition, collect 100."""

    def execute(self, player):
        self.log(player)
        player.balance += 100
        self.logger.warn(f'{player} won $100 in a crossword competition.')


class Chance15(ChanceCommunityChest):
    """Drunk in Change, Fine 20"""

    def execute(self, player):
        self.log(player)
        player.balance -= 20
        self.logger.warn(f'{player} fined $20 for being drunk.')


class Chance16(ChanceCommunityChest):
    """Go to jail, move directly to jail, etc"""

    def execute(self, player):
        self.log(player)
        player.go_to_jail()


class CommunityChest1(ChanceCommunityChest):
    """Pay 10 fine or take chance card."""

    def execute(self, player):
        self.log(player)
        if random.choice([True, False]):
            player.draw_card(player.chances)
        else:
            player.balance -= 10
            self.logger.warn(
                f'{player} paid $10 fine instead of drawing Chance.')


class CommunityChest2(ChanceCommunityChest):
    """go to jail, move directly, etc"""

    def execute(self, player):
        self.log(player)
        player.go_to_jail()


class CommunityChest3(ChanceCommunityChest):
    """won 2nd prize beauty contest - collect 10"""

    def execute(self, player):
        self.log(player)
        player.balance += 10
        self.logger.warn(f'{player} wins 2nd prize of $10 in beauty contest!')


class CommunityChest4(ChanceCommunityChest):
    """Bank error in favour collect 200"""

    def execute(self, player):
        self.log(player)
        player.balance += 200
        self.logger.warn(f'{player} gets $200 due to bank error!')


class CommunityChest5(ChanceCommunityChest):
    """drs fee, pay 50"""

    def execute(self, player):
        self.log(player)
        player.balance -= 50
        self.logger.warn(f'{player} pays doctor\'s fees of $50.')


class CommunityChest6(ChanceCommunityChest):
    """go back to old kent road"""

    def execute(self, player):
        self.log(player)
        n = player.current_pos - 1
        if n < 0:
            n = 1
        player.move(n)


class CommunityChest7(ChanceCommunityChest):
    """receive interest 25"""

    def execute(self, player):
        self.log(player)
        player.balance += 25
        self.logger.warn(f'{player} gets $25 in interest!')


class CommunityChest8(ChanceCommunityChest):
    """annuity matures collect 100"""

    def execute(self, player):
        self.log(player)
        player.balance += 100
        self.logger.warn(f'{player} gets $100 in annuity!')


class CommunityChest9(ChanceCommunityChest):
    """inherit 100"""

    def execute(self, player):
        self.log(player)
        player.balance += 100
        self.logger.warn(f'{player} inherits $100!')


class CommunityChest10(ChanceCommunityChest):
    """pay hospital 100"""

    def execute(self, player):
        self.log(player)
        player.balance -= 100
        self.logger.warn(f'{player} pays hospital $100.')


class CommunityChest11(ChanceCommunityChest):
    """pay insurance premium 50"""

    def execute(self, player):
        self.log(player)
        player.balance -= 50
        self.logger.warn(f'{player} pays insurance premium of $50.')


class CommunityChest12(ChanceCommunityChest):
    """IT refund collect  20"""

    def execute(self, player):
        self.log(player)
        player.balance += 20
        self.logger.warn(f'{player} gets IT refund of $20.')


class CommunityChest13(ChanceCommunityChest):
    """sale of stock get 50"""

    def execute(self, player):
        self.log(player)
        player.balance += 50
        self.logger.warn(f'{player} gets $50 from sale of stock!')


class CommunityChest14(ChanceCommunityChest):
    """birthday, collect 10 from each player"""

    def execute(self, player):
        self.log(player)
        for p in self.players:
            p.balance -= 10
            player.balance += 10
        self.logger.warn(f'{player} collects $10 from each player.')


class CommunityChest15(ChanceCommunityChest):
    """advance to go, collect 200"""

    def execute(self, player):
        self.log(player)
        player.move_to('Go')


class CommunityChest16(ChanceCommunityChest):
    """get out of jail free, etc"""

    def execute(self, player):
        self.log(player)
        self.logger.warn(f'{player} gets a get out of jail free card!')
        player.has_gojf = True


def init(logger, players):
    chances = []
    for i in range(16):
        klass = globals().get('Chance{}'.format(i + 1))
        chances.append(klass(logger, players))
    random.shuffle(chances)
    cs = []
    for i in range(16):
        klass = globals().get('CommunityChest{}'.format(i + 1))
        cs.append(klass(logger, players))
    random.shuffle(cs)
    return chances, cs
