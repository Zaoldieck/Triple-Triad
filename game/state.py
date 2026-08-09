# gestisce le carte possedute dal giocatore
from game.card_collection import CardCollection

# classe che contiene lo stato globale del gioco
class GameState:

    def __init__(self):

        #schermata attualmente attiva
        self.current_screen = None  # schermata attualmente attiva (None se nessuna schermata è attiva)

        # eventuale pannello aperto sopra una schermata
        self.current_panel = None  # pannello attualmente aperto (None se nessun pannello è aperto)

        # collezione delle carte possedute dal giocatore
        self.card_collection = CardCollection()


        # TEST TEMPORANEO: Zell è stato scoperto, ma non è posseduto
        #self.card_collection.discovered_card_ids.add(
        #    "ff8_zell"
        #)


        #indica se il gioco deve rimanere aperto
        self.running = True
        
    def change_screen(self, new_screen):
        # cambia la schermata attiva attualmente
        self.current_screen = new_screen

    def open_panel(self, panel):

        # apre un pannello sopra la schermata attiva
        self.current_panel = panel

    def close_panel(self):

        # chiude il pannello attualmente aperto
        self.current_panel = None