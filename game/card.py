# rappresentazione della carta del gioco

class Card: 

    def __init__(self, name, top, right, bottom, left, rarity):

        # nome della carta
        self.name = name

        # valori presenti sulla carta
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

        # livello rarita della carta da 1 a 10
        self.rarity = rarity



        
