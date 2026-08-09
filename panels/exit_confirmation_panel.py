import pygame
# cursore animato riutilizzabile
from ui.animated_hand_cursor import AnimatedHandCursor
from panels.panel import Panel


# pannello che chiede conferma prima di chiudere il gioco
class ExitConfirmationPanel(Panel):

    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # dimensioni del pannello di conferma
        self.panel_width = 520
        self.panel_height = 200

        # colori del pannello
        self.panel_color = (70, 70, 70)
        self.border_color = (255, 255, 255)

        # font del messaggio e delle opzioni
        self.message_font = pygame.font.SysFont("Arial", 30)
        self.option_font = pygame.font.SysFont("Arial", 28)

        # creo la manina animata della conferma di uscita
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

    # conferma l'opzione attualmente selezionata
    def confirm_selected_option(self):

        # Yes chiude il gioco
        if self.selected_option == 0:
            self.state.running = False

        # No chiude soltanto il pannello
        else:
            self.state.close_panel()

    # gestisce gli eventi del pannello
    def handle_events(self, event):

        # controllo tastiera
        if event.type == pygame.KEYDOWN:

            # ESC chiude soltanto il pannello
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

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

                # confermo l'opzione selezionata
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

        # sposto la manina quando il mouse passa sopra un'opzione
        if event.type == pygame.MOUSEMOTION:

            # controllo i rettangoli di Yes e No
            for i, option_rect in enumerate(self.option_rects):

                # seleziono l'opzione sotto il cursore
                if option_rect.collidepoint(event.pos):
                    self.selected_option = i

        # controllo i click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # il click sinistro conferma Yes oppure No
            if event.button == 1:

                # controllo quale opzione è stata cliccata
                for i, option_rect in enumerate(self.option_rects):

                    if option_rect.collidepoint(event.pos):
                        self.selected_option = i
                        self.confirm_selected_option()
                        break

            # il click destro annulla e chiude il pannello
            elif event.button == 3:
                self.state.close_panel()

    # aggiorna la logica del pannello
    def update(self):
        pass

    # disegna il pannello di conferma
    def draw(self, screen):

        # calcolo la posizione centrale del pannello
        x = (self.width - self.panel_width) // 2
        y = (self.height - self.panel_height) // 2

        # creo il rettangolo del pannello
        panel_rect = pygame.Rect(
            x,
            y,
            self.panel_width,
            self.panel_height
        )

        # disegno sfondo e bordo del pannello
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

        # preparo il messaggio di conferma
        message = self.message_font.render(
            "Do you want to exit the game?",
            True,
            (255, 255, 255)
        )

        message_rect = message.get_rect(
            center=(self.width // 2, y + 65)
        )

        screen.blit(message, message_rect)

        # svuoto la lista prima di ricreare i rettangoli
        self.option_rects = []

        # disegno le opzioni Yes e No
        for i, option in enumerate(self.options):

            # evidenzio l'opzione selezionata
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

            # salvo il rettangolo per hover e click del mouse
            self.option_rects.append(option_rect)

            screen.blit(option_surface, option_rect)

            # disegno la manina accanto all'opzione selezionata
            if i == self.selected_option:

                # disegno la manina animata accanto all'opzione selezionata
                self.hand_cursor.draw(
                    screen,
                    option_rect,
                    gap=5
                )