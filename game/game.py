import pygame

from screens.main_menu import MainMenu
from game.state import GameState
from game.save_manager import save_card_collection


# gestisce inizializzazione e loop principale del gioco
class Game:

    def __init__(self):

        # inizializzo Pygame
        pygame.init()

        # creo lo stato globale del gioco
        self.state = GameState()

        # disabilito la ripetizione automatica dei tasti
        pygame.key.set_repeat(0)

        # dimensioni fisse della finestra
        self.width = 1280
        self.height = 720

        # creo la finestra di gioco
        self.screen = pygame.display.set_mode(
            (
                self.width,
                self.height
            )
        )

        # limito il loop a 60 fotogrammi al secondo
        self.clock = pygame.time.Clock()
        self.target_fps = 60

        # creo e attivo il menu principale
        self.state.change_screen(
            MainMenu(
                self.width,
                self.height,
                self.state
            )
        )

    # mantiene attivo il loop principale
    def run(self):

        while self.state.running:

            # gestisco gli eventi
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.state.running = False
                    continue

                # un pannello aperto riceve gli eventi
                # al posto della schermata sottostante
                if self.state.current_panel:
                    self.state.current_panel.handle_events(
                        event
                    )
                else:
                    self.state.current_screen.handle_events(
                        event
                    )

            # evito un ultimo aggiornamento
            # dopo la richiesta di chiusura
            if not self.state.running:
                break

            # aggiorno la schermata attiva
            self.state.current_screen.update()

            # aggiorno anche l'eventuale pannello
            if self.state.current_panel:
                self.state.current_panel.update()

            # disegno la schermata attiva
            self.state.current_screen.draw(
                self.screen
            )

            # disegno l'eventuale pannello in primo piano
            if self.state.current_panel:
                self.state.current_panel.draw(
                    self.screen
                )

            # mostro il nuovo fotogramma
            pygame.display.flip()

            # mantengo il gioco a un massimo di 60 FPS
            self.clock.tick(
                self.target_fps
            )

        # salvo nuovamente la collezione
        # come protezione prima della chiusura
        save_card_collection(
            self.state.card_collection
        )

        pygame.quit()