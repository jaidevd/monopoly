import monopoly as mp


def start_game(handler):
    p1 = handler.get_argument('p1')
    p2 = handler.get_argument('p2')
    players = mp.start_game([p1, p2])


def roll(handler):
    p = handler.get_argument('player')
    return {p: (mp.roll(), mp.roll())}


def pick_starter(handler):
    global players
    return mp.pick_starter(players).name
