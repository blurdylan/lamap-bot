from errors import DifferentSuitError

# Colors
HEART = 'h'  # coeurs
CLUB = 'c'  # arachide
DIAMOND = 'd'  # biscuit
SPADE = 's'  # macabo
SPECIAL = 'x'

COLORS = (HEART, CLUB, DIAMOND, SPADE, SPECIAL)

CARD_ICONS = {
    HEART: '♥',  # coeurs
    CLUB: '♣',  # arachide
    DIAMOND: '♦',  # biscuit
    SPADE: '♠',  # macabo
    SPECIAL: '✳'  # special
}

# Values
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
TEN = '10'

VALUES = (THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN)

SPECIALS = ('x_21', 'x_333', 'x_777', 'x_0', 'x_5555')

STICKERS = {
    'h_3': 'CAACAgQAAxkBAAOzXqbjq88jyiRYK0HCxnuHVAtKL40AAtEAA2FKVA1dSx3Iy3IK3xkE',
    'h_4': 'CAACAgQAAxkBAAO5XqbjrcNTX8H3UH19_wNC31XGLh8AAtQAA2FKVA0OOiS308BPOhkE',
    'h_5': 'CAACAgQAAxkBAAPBXqbjtC13p5rH_2IwiSvuInaV_nsAAtgAA2FKVA2Lgtx6_jM1NhkE',
    'h_6': 'CAACAgQAAxkBAAPJXqbju1Kz8-UX-ytsVYPmgynIMZ4AAtwAA2FKVA3C5Pfy9dX4-xkE',
    'h_7': 'CAACAgQAAxkBAAPRXqbjxP3Qxh-wEunyS4pgwm1TSgUAAuAAA2FKVA3rXOVIcwPleBkE',
    'h_8': 'CAACAgQAAxkBAAPZXqbjyWKKDEQ1DApejMEz6l_wRfMAAuQAA2FKVA0Trw4HumgfPRkE',
    'h_9': 'CAACAgQAAxkBAAPhXqbjzZyczpeVCGk06K_IMYOG_94AAugAA2FKVA3KYooFSMGB7RkE',
    'h_10': 'CAACAgQAAxkBAAPpXqbj0oQ05f9Ar3H_09X3sFVKvJoAAuwAA2FKVA3_65EfKjenVBkE',

    'c_3': 'CAACAgQAAxkBAAOtXqbjpA1sAStT8uCtGhcSEJtxXJwAAs4AA2FKVA39aBG2r0XL_hkE',
    'c_4': 'CAACAgQAAxkBAAO1XqbjrHk4GYylWn5xMkWWQwFrmukAAtIAA2FKVA2hPaFq6AurSRkE',
    'c_5': 'CAACAgQAAxkBAAO9XqbjsoPI2GdedcNwaNQuomS4u-cAAtYAA2FKVA13zcXRptFBiBkE',
    'c_6': 'CAACAgQAAxkBAAPFXqbjuL5SlCQrb_OeSUnBoSzE5rMAAtoAA2FKVA1rzd9kfh2M_BkE',
    'c_7': 'CAACAgQAAxkBAAPNXqbjv3puRGjOIJMmB1sy3L4CjtgAAt4AA2FKVA39w-bYtCjLdRkE',
    'c_8': 'CAACAgQAAxkBAAPVXqbjxr4eEDYqCF8jY_s-v-fma_wAAuIAA2FKVA3mbu8th2EhAhkE',
    'c_9': 'CAACAgQAAxkBAAPdXqbjy6EPmmRZLpbYDzCvndUVrf0AAuYAA2FKVA2vNZqUMsER_xkE',
    'c_10': 'CAACAgQAAxkBAAPlXqbj0O2hfo-nSSXW8Qfqs63xWCgAAuoAA2FKVA1yjlRwq6Zt7hkE',

    'd_3': 'CAACAgQAAxkBAAOvXqbjp28wNLAmxxsSJpXilgwwV2gAAs8AA2FKVA2iw15nVG2rtRkE',
    'd_4': 'CAACAgQAAxkBAAO3XqbjrVNuIi6ZlOvQ1DYQqrW9HB4AAtMAA2FKVA12zqu3bxhQJBkE',
    'd_5': 'CAACAgQAAxkBAAO_XqbjswaKyXPrJynXySiWstQNgv0AAtcAA2FKVA28NhXmJg3BKRkE',
    'd_6': 'CAACAgQAAxkBAAPHXqbjuelHyqVPNiZpDmv5C76e_FgAAtsAA2FKVA3FbRkFAhwb5RkE',
    'd_7': 'CAACAgQAAxkBAAPPXqbjwj_DDleTmOpKLNW7GTFVxA0AAt8AA2FKVA0437M2GEFBoRkE',
    'd_8': 'CAACAgQAAxkBAAPXXqbjxyCAp2X42L-C34B2kLG4rhsAAuMAA2FKVA3NHCgpAiICKhkE',
    'd_9': 'CAACAgQAAxkBAAPfXqbjzMo8PsT0Kq3apg7PGBjc5SgAAucAA2FKVA0qpC-x0GJHihkE',
    'd_10': 'CAACAgQAAxkBAAPnXqbj0UnjdzWhc87_pM97BFXdDLUAAusAA2FKVA2u-e29eLE3ORkE',

    's_3': 'CAACAgQAAxkBAAOxXqbjqmlh_Xd8hA2oLjI7UwQ9_9IAAtAAA2FKVA1pm0eMORTzLRkE',
    's_4': 'CAACAgQAAxkBAAO7XqbjrjY0VjFsVHHwmMBgfz39br0AAtUAA2FKVA0rN3HXg8KPRhkE',
    's_5': 'CAACAgQAAxkBAAPDXqbjtr_H3dOCL9tpKDcfjCJgpMIAAtkAA2FKVA30DBmF6vkG7RkE',
    's_6': 'CAACAgQAAxkBAAPLXqbjvLAhVBmNy0ACnIbzrvdc5vIAAt0AA2FKVA2JJvqbjb3gWhkE',
    's_7': 'CAACAgQAAxkBAAPTXqbjxfjrMz4qJnEZYHZfKVxuQ4gAAuEAA2FKVA1p2eHNwT4LhxkE',
    's_8': 'CAACAgQAAxkBAAPbXqbjykUPcGREf1CGGUIdiJD06G4AAuUAA2FKVA2I14xWSxqhRxkE',
    's_9': 'CAACAgQAAxkBAAPjXqbjzrYR86ufjQZM_WwQicvDghgAAukAA2FKVA2s71__-M8nghkE',
    's_10': 'CAACAgQAAx0CR2WNiQACKjZgYfsExbIsXtdNJ6SayGLuw9HH4AAC7QADYUpUDTOCwg0VQzVSHgQ',

    'x_21': 'CAACAgQAAxkBAAMNXuLPGA6r1loi2c8EPix80dSsRLQAAu4AA2FKVA3qDTAidx882BoE',
    'x_333': 'CAACAgQAAxkBAAMPXuLPMo_m6LJtBCoJEKQCZbPK9wcAAu8AA2FKVA2_-eKiP4VxnhoE',
    'x_777': 'CAACAgQAAxkBAAMRXuLPUL3O4bkGxyRvO9FDI5ItDiMAAvAAA2FKVA3j7_ZjyANyTBoE',
    'x_0': 'CAACAgQAAxkBAAMTXuLPafqGPSd5xjX3oxfzb_iG3cwAAvEAA2FKVA10r_2_FR2UFxoE',
    'x_5555': 'CAACAgQAAxkBAAPOYCftEAHQA0w6D65PncTmh3_-2HAAAvQAA2FKVA0drR6hxMFu7B4E'
}


class Card(object):
    """This class represents a card"""

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f'{self.suit}_{self.value}'

    def __repr__(self):
        return '%s%s' % (CARD_ICONS[self.suit], self.value.capitalize())

    def __eq__(self, other):
        """Needed for sorting the cards"""
        return str(self) == str(other)

    def __lt__(self, other):
        """Needed for sorting the cards"""
        return str(self) < str(other)


def from_str(string):
    suit, value = string.split('_')
    return Card(suit, value)
