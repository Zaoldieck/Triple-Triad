import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello che chiede conferma prima di iniziare la partita
class PlayConfirmationPanel(Panel):

    def __init__(
        self,
        width,
        height,
        state,
        free_match_panel
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # conservo il Free Match Panel;
        # servirà per mostrarlo sotto la conferma
        # e per tornarci selezionando No
        self.free_match_panel = free_match_panel

        # dimensioni del pannello di conferma
        self.panel_width = 520
        self.panel_height = 200

        # colori del pannello
        self.panel_color = (70, 70, 70)
        self.border_color = (255, 255, 255)

        # font del messaggio e delle opzioni
        self.message_font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.option_font = pygame.font.SysFont(
            "Arial",
            28
        )

        # creo la manina animata della conferma
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # opzioni disponibili
        self.options = [
            "Yes",
            "No"
        ]

        # seleziono No come scelta iniziale per sicurezza
        self.selected_option = 1

        # rettangoli delle opzioni Yes e No
        self.option_rects = []

    # annulla la conferma e torna alla selezione delle carte
    def cancel_confirmation(self):

        # rimuovo la quinta e ultima carta selezionata
        if self.free_match_panel.selected_cards:
            self.free_match_panel.selected_cards.pop()

        # ripristino il Free Match Panel precedente
        self.state.open_panel(
            self.free_match_panel
        )

    # conferma l'opzione attualmente selezionata
    def confirm_selected_option(self):

        # Yes avvierà la partita;
        # questa azione verrà implementata successivamente
        if self.selected_option == 0:
            pass

        # No annulla la quinta carta e torna indietro
        else:
            self.cancel_confirmation()

    # gestisce gli eventi del pannello
    def handle_events(self, event):

        # controllo tastiera
        if event.type == pygame.KEYDOWN:

            # ESC equivale a selezionare No
            if event.key == pygame.K_ESCAPE:
                self.cancel_confirmation()

            # cambio opzione con le frecce sinistra e destra
            elif event.key in (
                pygame.K_LEFT,
                pygame.K_RIGHT
            ):
                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.options)

            # confermo l'opzione selezionata
            elif event.key == pygame.K_RETURN:
                self.confirm_selected_option()

        # cambio opzione usando la rotella del mouse
        if event.type == pygame.MOUSEWHEEL:

            # rotella verso l'alto: opzione precedente
            if event.y > 0:
                self.selected_option = (
                    self.selected_option - 1
                ) % len(self.options)

            # rotella verso il basso: opzione successiva
            elif event.y < 0:
                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.options)

        # sposto la manina sopra l'opzione indicata dal mouse
        if event.type == pygame.MOUSEMOTION:

            for i, option_rect in enumerate(
                self.option_rects
            ):

                if option_rect.collidepoint(event.pos):
                    self.selected_option = i

        # controllo i click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # il clic sinistro conferma Yes oppure No
            if event.button == 1:

                for i, option_rect in enumerate(
                    self.option_rects
                ):

                    if option_rect.collidepoint(event.pos):
                        self.selected_option = i
                        self.confirm_selected_option()
                        break

            # il clic destro equivale a selezionare No
            elif event.button == 3:
                self.cancel_confirmation()

    # aggiorna la logica del pannello
    def update(self):
        pass

    # disegna il pannello di conferma
    def draw(self, screen):

        # ridisegno sotto la selezione delle carte
        self.free_match_panel.draw(screen)

        # calcolo la posizione centrale della conferma
        x = (self.width - self.panel_width) // 2
        y = (self.height - self.panel_height) // 2

        # creo il rettangolo della conferma
        panel_rect = pygame.Rect(
            x,
            y,
            self.panel_width,
            self.panel_height
        )

        # disegno sfondo e bordo
        pygame.draw.rect(
            screen,
            self.panel_color,
            panel_rect
        )

        pygame.draw.rect(
            screen,
            self.border_color,
            panel_rect,
            2
        )

        # preparo il messaggio
        message = self.message_font.render(
            "Play with these cards?",
            True,
            (255, 255, 255)
        )

        message_rect = message.get_rect(
            center=(
                self.width // 2,
                y + 65
            )
        )

        screen.blit(
            message,
            message_rect
        )

        # ricreo i rettangoli delle opzioni
        self.option_rects = []

        # disegno Yes e No
        for i, option in enumerate(self.options):

            # l'opzione selezionata appare bianca
            if i == self.selected_option:
                color = (255, 255, 255)
            else:
                color = (140, 140, 140)

            option_surface = self.option_font.render(
                option,
                True,
                color
            )

            option_rect = option_surface.get_rect(
                center=(
                    self.width // 2 - 80 + i * 160,
                    y + 140
                )
            )

            # salvo il rettangolo per hover e click
            self.option_rects.append(
                option_rect
            )

            screen.blit(
                option_surface,
                option_rect
            )

            # disegno la manina accanto alla scelta attiva
            if i == self.selected_option:
                self.hand_cursor.draw(
                    screen,
                    option_rect,
                    gap=5
                )