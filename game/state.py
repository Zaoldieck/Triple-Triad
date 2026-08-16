# gestisce le carte possedute dal giocatore
from game.card_collection import CardCollection
# carica la collezione salvata dal giocatore
from game.save_manager import load_card_collection


# classe che contiene lo stato globale del gioco
class GameState:

    def __init__(self):

        # schermata attualmente attiva
        self.current_screen = None

        # eventuale pannello aperto sopra la schermata
        self.current_panel = None

        # collezione delle carte possedute dal giocatore
        self.card_collection = CardCollection()

        # carico l'eventuale collezione salvata
        load_card_collection(
            self.card_collection
        )

        # indica se il gioco deve rimanere aperto
        self.running = True

    # sostituisce la schermata attualmente attiva
    def change_screen(self, new_screen):
        
        self.current_screen = new_screen

    def open_panel(self, panel):

        # apre un pannello sopra la schermata attiva
        self.current_panel = panel

    def close_panel(self):

        # chiude il pannello attualmente aperto
        self.current_panel = None