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

    # cambia il proprietario di una carta già piazzata
    def change_owner(
        self,
        row,
        column,
        new_owner
    ):

        # recupero il contenuto della casella
        cell = self.get_cell(
            row,
            column
        )

        # interrompo se la casella non contiene una carta
        if cell is None:
            return False

        # assegno il nuovo proprietario
        cell["owner"] = new_owner

        return True

    # restituisce True quando tutte
    # le nove caselle sono occupate
    def is_full(self):

        # controllo tutte le righe del tabellone
        for row in self.grid:

            # se trovo almeno una casella vuota,
            # la partita non è ancora terminata
            if None in row:
                return False

        # nessuna casella è rimasta vuota
        return True
