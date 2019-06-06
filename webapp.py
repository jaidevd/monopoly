import monopoly as mp

game = mp.Game()


def _read_log():
    with open('log.txt', 'r') as fin:
        data = fin.readlines()
    return ''.join([f'<p>{i}</p>' for i in data])


def start_game(handler):
    p1 = handler.get_argument('p1')
    p2 = handler.get_argument('p2')
    p1 = mp.Player(p1)
    p2 = mp.Player(p2)
    chances, cs = mp.ccs.init(mp.logger, [p1, p2])
    p1.chances = chances
    p2.chances = chances
    p1.cs = cs
    p2.cs = cs
    game.add_players(p1, p2)


def play_turn(handler):
    p = handler.get_argument('p1')
    game.play(p)
    return _read_log()


def pick_next_player(handler):
    p = handler.get_argument('player')
    return game.pick_next_player(p)


def get_balance(handler):
    pl = handler.path_args[0]
    return str(game.players[pl].balance)
