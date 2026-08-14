# rappresenta logicamente il tabellone 3x3 della partita
class Board:

    def __init__(self):

        # numero di righe e colonne del tabellone
        self.rows = 3
        self.columns = 3

        # creo una griglia 3x3 inizialmente vuota;
        # ogni posizione conterrà None oppure una carta piazzata
        self.grid = [
            [None for column in range(self.columns)]
            for row in range(self.rows)
        ]

    # controlla che una posizione appartenga al tabellone
    def is_valid_position(self, row, column):

        return (
            0 <= row < self.rows
            and 0 <= column < self.columns
        )

    # controlla se una casella è vuota
    def is_empty(self, row, column):

        # una posizione esterna al tabellone non è utilizzabile
        if not self.is_valid_position(row, column):
            return False

        return self.grid[row][column] is None

    # inserisce una carta in una casella vuota
    def place_card(self, card, owner, row, column):

        # impedisco di utilizzare posizioni non valide
        # oppure caselle già occupate
        if not self.is_empty(row, column):
            return False

        # salvo sia la carta sia il suo proprietario;
        # owner servirà successivamente per le catture
        self.grid[row][column] = {
            "card": card,
            "owner": owner
        }

        return True

    # restituisce il contenuto di una casella
    def get_cell(self, row, column):

        # una posizione non valida non contiene nulla
        if not self.is_valid_position(row, column):
            return None

        return self.grid[row][column]

    # svuota completamente il tabellone
    def reset(self):

        self.grid = [
            [None for column in range(self.columns)]
            for row in range(self.rows)
        ]