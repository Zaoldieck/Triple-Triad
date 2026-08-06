import pygame

from screens.main_menu import MainMenu # serve per importare la classe MainMenu dal file main_menu.py
from game.state import GameState # serve per importare la classe GameState dal file state.py

class Game:
    def __init__(self):

        #inizializzo py game
        pygame.init()
        self.state = GameState() # creo lo stato globale del gioco

        # disabilito la ripetizione dei tasti in modo che non scorre velocissimo il menu
        pygame.key.set_repeat(0)

        # dimensioni della finestra
        self.width = 1280
        self.height = 720

        # creo la finestra di gioco
        self.screen = pygame.display.set_mode((self.width, self.height))

        # creo il menu principale
        self.current_screen = MainMenu(self.width, self.height, self.state)  # creo un'istanza della classe MainMenu

    def run(self): # loop per tenere aperta la finestra di gioco
        running = True 
        while running:
            # 1 EVENTI
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # inoltro gli eventi al menu principale
                self.current_screen.handle_events(event)

            # 2 LOGICA
            self.current_screen.update()

            # 3 DISEGNO
            self.current_screen.draw(self.screen)

            pygame.display.flip() # disegna tutto quello che sta nel buffer


        #chiude pygame
        pygame.quit()