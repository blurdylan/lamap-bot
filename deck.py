from random import shuffle
import logging


# LaMap's 31 playing cards
LAMAP_CARDS = [
    'h_3', 'h_4', 'h_5', 'h_6', 'h_7', 'h_8', 'h_9', 'h_10',
    'c_3', 'c_4', 'c_5', 'c_6', 'c_7', 'c_8', 'c_9', 'c_10',
    'd_3', 'd_4', 'd_5', 'd_6', 'd_7', 'd_8', 'd_9', 'd_10',
    's_3', 's_4', 's_5', 's_6', 's_7', 's_8', 's_9', 's_10'
]

# ? Test cards - input any set to test with only that set
# ? Do not forget to remove shuffle and know the cards are taken from the right to the left
''' LAMAP_CARDS = ['h_4', 'd_7', 'd_6', 'd_5', 'd_4', 'd_3', 'h_3', 'h_8', 'h_9',
               'h_10', 's_3', 'c_3', 'c_4', 'c_5', 'c_10'] '''


class Deck(object):
    """This class represents a shuffled deck of card"""

    def __init__(self):
        self.cards = list()  # create game cards
        self.graveyard = list()
        self.cards_dealt = 0
        self.logger = logging.getLogger(__name__)

    def fill_cards(self):
        """ fill 31 game cards and shuffle them """
        self.cards = LAMAP_CARDS.copy()
        self.shuffle()

    def shuffle(self):
        """shuffles the deck"""
        # ? remove shuffle when testing cards
        # shuffle(self.cards)
