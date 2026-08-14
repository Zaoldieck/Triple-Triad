import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello mostrato al termine di una partita
class PlayAgainPanel(Panel):

    def __init__(
        self,
        width,
        height,
        state,
        player_cards,
        match_rules
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # conservo le carte e le regole della partita appena terminata;
        # serviranno per avviare un'eventuale rivincita
        self.player_cards = list(player_cards)
        self.match_rules = match_rules

        # dimensioni del pannello
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

        # manina animata usata per la scelta
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # opzioni disponibili
        self.options = [
            "Yes",
            "No"
        ]

        # No è la scelta iniziale
        self.selected_option = 1

        # rettangoli usati successivamente
        # per mouseover e click
        self.option_rects = []

    # gestisce gli eventi del pannello
        # conferma l'opzione attualmente selezionata
    def confirm_selected_option(self):

        # Yes crea una nuova partita con le stesse
        # carte e regole, ma con una nuova mano avversaria
        if self.selected_option == 0:

            # import locale per evitare dipendenze circolari
            from screens.match_screen import MatchScreen

            new_match_screen = MatchScreen(
                self.width,
                self.height,
                self.state,
                self.player_cards,
                self.match_rules
            )

            # chiudo il pannello e avvio la nuova partita
            self.state.close_panel()
            self.state.change_screen(
                new_match_screen
            )

        # No torna al menu principale
        else:

            # import locale per evitare dipendenze circolari
            from screens.main_menu import MainMenu

            main_menu = MainMenu(
                self.width,
                self.height,
                self.state
            )

            # chiudo il pannello e torno al menu
            self.state.close_panel()
            self.state.change_screen(
                main_menu
            )

    # gestisce gli eventi del pannello
    def handle_events(self, event):

        # controllo tastiera
        if event.type == pygame.KEYDOWN:

            # ESC equivale alla scelta No
            if event.key == pygame.K_ESCAPE:
                self.selected_option = 1
                self.confirm_selected_option()

            # entrambe le frecce cambiano scelta
            elif event.key in (
                pygame.K_LEFT,
                pygame.K_RIGHT
            ):
                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.options)

            # confermo la scelta attualmente indicata
            elif event.key == pygame.K_RETURN:
                self.confirm_selected_option()

        # cambio scelta con la rotella del mouse
        if event.type == pygame.MOUSEWHEEL:

            # rotella verso l'alto
            if event.y > 0:
                self.selected_option = (
                    self.selected_option - 1
                ) % len(self.options)

            # rotella verso il basso
            elif event.y < 0:
                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.options)

        # il mouseover sposta la manina
        if event.type == pygame.MOUSEMOTION:

            for i, option_rect in enumerate(
                self.option_rects
            ):

                if option_rect.collidepoint(event.pos):
                    self.selected_option = i

        # controllo i click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # il click sinistro conferma
            # l'opzione effettivamente cliccata
            if event.button == 1:

                for i, option_rect in enumerate(
                    self.option_rects
                ):

                    if option_rect.collidepoint(event.pos):
                        self.selected_option = i
                        self.confirm_selected_option()
                        break

            # il click destro equivale alla scelta No
            elif event.button == 3:
                self.selected_option = 1
                self.confirm_selected_option()

    # aggiorna la logica del pannello
    def update(self):
        pass

    # disegna il pannello
    def draw(self, screen):

        # centro il pannello nella finestra
        x = (
            self.width
            - self.panel_width
        ) // 2

        y = (
            self.height
            - self.panel_height
        ) // 2

        panel_rect = pygame.Rect(
            x,
            y,
            self.panel_width,
            self.panel_height
        )

        # disegno lo sfondo e il bordo
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

        # preparo il messaggio principale
        message_surface = self.message_font.render(
            "Do you want to play again?",
            True,
            (255, 255, 255)
        )

        message_rect = message_surface.get_rect(
            center=(
                self.width // 2,
                y + 65
            )
        )

        screen.blit(
            message_surface,
            message_rect
        )

        # ricreo i rettangoli di Yes e No
        self.option_rects = []

        for i, option in enumerate(self.options):

            # la scelta attiva appare bianca
            if i == self.selected_option:
                option_color = (255, 255, 255)

            # la scelta inattiva appare sbiadita
            else:
                option_color = (140, 140, 140)

            option_surface = self.option_font.render(
                option,
                True,
                option_color
            )

            option_rect = option_surface.get_rect(
                center=(
                    self.width // 2 - 80 + i * 160,
                    y + 140
                )
            )

            # salvo il rettangolo per i controlli
            self.option_rects.append(
                option_rect
            )

            screen.blit(
                option_surface,
                option_rect
            )

            # la manina indica la scelta attiva
            if i == self.selected_option:
                self.hand_cursor.draw(
                    screen,
                    option_rect,
                    gap=5
                )