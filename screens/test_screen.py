import pygame

from screens.screen import Screen # serve per importare la classe Screen dal file screen.py

class TestScreen(Screen):
    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height
    
        # stato globale del gioco
        self.state = state

        #creo un font di prova
        self.font = pygame.font.SysFont("Arial", 45)  # font Arial, dimensione 45



    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # se premo ESC torno al menu principale
                from screens.main_menu import MainMenu
                self.state.change_screen(MainMenu(self.width, self.height, self.state))

    def update(self):
        pass

    def draw(self, screen):

        # colore sfondo di prova
        screen.fill((0, 0, 0))  # riempio lo sfondo

        # testo di prova
        text = self.font.render("Test Screen - Press ESC", True, (255, 255, 255))  # testo bianco

        #posizione testo al centro
        x = (self.width - text.get_width()) // 2
        y = (self.height - text.get_height()) // 2

        screen.blit(text, (x, y))  # disegno il testo