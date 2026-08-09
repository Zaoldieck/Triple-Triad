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


        # associo il nome di ogni lato al relativo valore
        card_values = {
            "top": top,
            "right": right,
            "bottom": bottom,
            "left": left
        }

        # controllo che tutti i valori siano numeri interi da 1 a 10
        for side, value in card_values.items():

            if (
                not isinstance(value, int)
                or not 1 <= value <= 10
            ):
                raise ValueError(
                    f"Invalid {side} value for "
                    f"{card_id}: {value}"
                )

        # controllo che la rarità sia un numero intero da 1 a 10
        if (
            not isinstance(rarity, int)
            or not 1 <= rarity <= 10
        ):
            raise ValueError(
                f"Invalid rarity for {card_id}: {rarity}"
            )

        # elementi validi del Triple Triad di FFVIII
        valid_elements = {
            None,
            "earth",
            "fire",
            "holy",
            "ice",
            "poison",
            "thunder",
            "water",
            "wind"
        }

        # controllo che l'elemento sia valido
        if element not in valid_elements:
            raise ValueError(
                f"Invalid element for {card_id}: {element}"
            )

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

