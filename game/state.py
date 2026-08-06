# classe che contiene lo stato globale del gioco
class GameState:

    def __init__(self):

        #schermata attualmente attiva
        self.current_screen = None  # schermata attualmente attiva (None se nessuna schermata è attiva)

        # eventuale pannello aperto sopra una schermata
        self.current_panel = None  # pannello attualmente aperto (None se nessun pannello è aperto)

        
    def change_screen(self, new_screen):
        # cambia la schermata attiva attualmente
        self.current_screen = new_screen