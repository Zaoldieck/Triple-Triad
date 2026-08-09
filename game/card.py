# rappresentazione della carta del gioco

class Card: 

    def __init__(
        self,
        card_id,
        name,
        image_path,
        top,
        right,
        bottom,
        left,
        rarity,
        element,
        card_sets
    ):

        # identificatore unico e permanente della carta
        self.card_id = card_id

        # nome della carta
        self.name = name

        # percorso dell'immagine della carta
        self.image_path = image_path

        # valori presenti sulla carta
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

        # livello rarita della carta da 1 a 10
        self.rarity = rarity

        # elemento della carta; None indica che non possiede un elemento
        self.element = element

        # lista dei set ai quali appartiene la carta
        self.card_sets = card_sets

