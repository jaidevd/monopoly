from unittest import TestCase, main
import random
import monopoly as mp


class TestMonopoly(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.alice, cls.bob = mp.start_game('Alice Bob'.split())

    def setUp(self):
        self.alice.current_pos = self.bob.current_pos = 0
        self.alice.properties = self.bob.properties = []
        self.alice.balance = self.bob.balance = 1500
        self.alice.has_gojf = self.bob.has_gojf = 1500
        for p in mp.loc.LOCATIONS:
            p.owner = None

    def test_go_back_card(self):
        # make alice go to a card index
        pos = random.choice([2, 7, 17, 22, 33, 36])
        self.alice.current_pos = pos
        self.alice.greedy = False
        balance = self.alice.balance
        # pick a go back card at random: Chance2 or CommunityChest6
        card = random.choice([mp.ccs.Chance2([self.alice, self.bob]),
                              mp.ccs.CommunityChest6([self.alice, self.bob])])
        card.execute(self.alice)
        # check if the player is at the right position, they should not have collected salary
        if card.__class__.__name__ == 'Chance2':
            self.assertEqual(pos - self.alice.current_pos, 3)
        else:
            self.assertEqual(self.alice.current_pos, 1)
        self.assertEqual(self.alice.balance, balance)

    def test__split_houses_blank(self):
        properties = [c for c in mp.loc.LOCATIONS if c.color == 'brown']
        division = mp._split_houses(properties, 8)
        self.assertListEqual(division, [4, 4])

        division = mp._split_houses(properties, 2)
        self.assertListEqual(division, [1, 1])

    def test__split_houses_developed(self):
        p = [c for c in mp.loc.LOCATIONS if c.color == 'brown']
        p[0].n_houses = 1
        p[0].n_houses = 0
        division = mp._split_houses(p, 1)
        self.assertListEqual(division, [0, 1])

        p[0].n_houses = 2
        p[0].n_houses = 1
        division = mp._split_houses(p, 4)
        self.assertListEqual(division, [2, 2])


if __name__ == "__main__":
    main()
