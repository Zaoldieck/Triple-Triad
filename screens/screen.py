# classe per tutte le schermate del gioco 

class Screen:

    #gestisce gli eventi ricevuti dalla schermata
    def handle_events(self, event):
        pass # da implementare nelle sottoclassi

    # aggiorna la logica della schermata
    def update(self):
        pass # da implementare nelle sottoclassi    

    # disegna la schermata sullo schermo
    def draw(self, screen):
        pass # da implementare nelle sottoclassi

    