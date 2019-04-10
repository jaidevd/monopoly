import monopoly as mp


def start_game(handler):
    p1 = handler.get_argument('p1')
    p2 = handler.get_argument('p2')
    global players
    players = mp.start_game([p1, p2])


def roll(handler):
    from ipdb import set_trace; set_trace()  # NOQA
