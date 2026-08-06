# classe base per tutti i pannelli del gioco

class Panel:

    # gestisce gli eventi ricevuti dal pannello
    def handle_events(self, event):
        pass # da implementare nelle sottoclassi

    # aggiorna la logica del pannello
    def update(self):
        pass # da implementare nelle sottoclassi    

    # disegna il pannello sullo schermo
    def draw(self, screen):
        pass # da implementare nelle sottoclassi
    