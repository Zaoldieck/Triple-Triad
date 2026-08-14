import pygame

from screens.main_menu import MainMenu # serve per importare la classe MainMenu dal file main_menu.py
from game.state import GameState # serve per importare la classe GameState dal file state.py
# salva la collezione del giocatore
from game.save_manager import save_card_collection

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

        # titolo mostrato nella barra della finestra
        pygame.display.set_caption(
            "Simo Game - Playable Demo v0.1"
        )

        # creo il menu principale
        self.state.change_screen(MainMenu(self.width, self.height, self.state))  # creo un'istanza della classe MainMenu

    def run(self): # loop per tenere aperta la finestra di gioco
        
        while self.state.running:
            # 1 EVENTI
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False

                # inoltro gli eventi al menu principale
                if self.state.current_panel:
                    self.state.current_panel.handle_events(event)
                else:
                    self.state.current_screen.handle_events(event)

            # 2 LOGICA
            self.state.current_screen.update()

            if self.state.current_panel:
                self.state.current_panel.update()

            # 3 DISEGNO
            self.state.current_screen.draw(self.screen)

            if self.state.current_panel:
                self.state.current_panel.draw(self.screen)

            pygame.display.flip() # disegna tutto quello che sta nel buffer


        # salvo la collezione prima di chiudere il gioco
        save_card_collection(
            self.state.card_collection
        )

        # chiudo Pygame
        pygame.quit()