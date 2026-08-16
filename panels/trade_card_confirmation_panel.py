import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello che conferma le carte scelte
# nelle Trade Rules con selezione manuale
class TradeCardConfirmationPanel(Panel):

    def __init__(
        self,
        width,
        height,
        state,
        trade_screen
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # conservo la schermata dello scambio;
        # riceverà la risposta Yes oppure No
        self.trade_screen = trade_screen

        # dimensioni del pannello
        self.panel_width = 520
        self.panel_height = 200

        # colori del pannello
        self.panel_color = (
            70,
            70,
            70
        )

        self.border_color = (
            255,
            255,
            255
        )

        # font del messaggio e delle opzioni
        self.message_font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.option_font = pygame.font.SysFont(
            "Arial",
            28
        )

        # opzioni disponibili
        self.options = [
            "Yes",
            "No"
        ]

        # No è selezionato inizialmente
        self.selected_option = 1

        # rettangoli per hover e click
        self.option_rects = []

        # manina animata del pannello
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

    # applica la scelta Yes oppure No
    def confirm_selected_option(self):

        # chiudo prima il pannello
        self.state.close_panel()

        # Yes conferma definitivamente
        # tutte le carte selezionate
        if self.selected_option == 0:
            self.trade_screen.confirm_trade_card()

        # No annulla la selezione e avvia
        # il flip inverso da blu a rosso
        else:
            self.trade_screen.cancel_trade_card()

    # gestisce tastiera e mouse
    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:

            # ESC equivale alla scelta No
            if event.key == pygame.K_ESCAPE:
                self.selected_option = 1
                self.confirm_selected_option()

            # sinistra e destra cambiano scelta
            elif event.key in (
                pygame.K_LEFT,
                pygame.K_RIGHT
            ):
                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.options)

            # Invio conferma la scelta
            elif event.key == pygame.K_RETURN:
                self.confirm_selected_option()

        # la rotella cambia scelta
        if event.type == pygame.MOUSEWHEEL:

            if event.y > 0:
                self.selected_option = (
                    self.selected_option - 1
                ) % len(self.options)

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
                    break

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

            # il click destro equivale a No
            elif event.button == 3:
                self.selected_option = 1
                self.confirm_selected_option()

    # nessuna logica aggiuntiva
    def update(self):
        pass

    # disegna il pannello
    def draw(self, screen):

        # posizione centrale del pannello
        x = (
            self.width - self.panel_width
        ) // 2

        y = (
            self.height - self.panel_height
        ) // 2

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

        # adatto la domanda al numero
        # di carte attualmente selezionate
        selected_card_count = len(
            self.trade_screen.chosen_trade_cards
        )

        if selected_card_count == 1:
            confirmation_message = (
                "Confirm selected card?"
            )
        else:
            confirmation_message = (
                "Confirm selected cards?"
            )

        message_surface = self.message_font.render(
            confirmation_message,
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

        # ricreo i rettangoli delle opzioni
        self.option_rects = []

        for i, option in enumerate(self.options):

            if i == self.selected_option:
                option_color = (
                    255,
                    255,
                    255
                )
            else:
                option_color = (
                    140,
                    140,
                    140
                )

            option_surface = self.option_font.render(
                option,
                True,
                option_color
            )

            option_rect = option_surface.get_rect(
                center=(
                    self.width // 2
                    - 80
                    + i * 160,
                    y + 140
                )
            )

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