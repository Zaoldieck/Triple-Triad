import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello che chiede conferma prima
# di abbandonare una partita in corso
class LeaveMatchConfirmationPanel(Panel):

    def __init__(
        self,
        width,
        height,
        state,
        match_rules
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # conservo le regole della partita
        # per mostrarle nel riepilogo del pannello
        self.match_rules = match_rules

        # dimensioni del pannello
        self.panel_width = 620
        self.panel_height = 400

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

        # font usato per il riepilogo delle regole
        self.rules_font = pygame.font.SysFont(
            "Arial",
            25
        )

        # opzioni disponibili
        self.options = [
            "Yes",
            "No"
        ]

        # No è selezionato inizialmente
        # per evitare uscite accidentali
        self.selected_option = 1

        # rettangoli usati da hover e click
        self.option_rects = []

        # manina animata del pannello
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

    # conferma l'opzione selezionata
    def confirm_selected_option(self):

        # Yes abbandona la partita
        # e torna al menu principale
        if self.selected_option == 0:

            # import locale per evitare
            # dipendenze circolari
            from screens.main_menu import MainMenu

            main_menu = MainMenu(
                self.width,
                self.height,
                self.state
            )

            self.state.close_panel()
            self.state.change_screen(
                main_menu
            )

        # No chiude soltanto il pannello
        # e lascia la partita invariata
        else:
            self.state.close_panel()

    # gestisce tastiera e mouse
    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:

            # ESC equivale a No
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

        # controllo i click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # click sinistro conferma
            # l'opzione cliccata
            if event.button == 1:

                for i, option_rect in enumerate(
                    self.option_rects
                ):
                    if option_rect.collidepoint(event.pos):
                        self.selected_option = i
                        self.confirm_selected_option()
                        break

            # click destro equivale a No
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

        # recupero soltanto le regole Extra attive
        active_extra_rules = [
            rule_name
            for rule_name, enabled
            in self.match_rules["extra"].items()
            if enabled
        ]

        # recupero soltanto le regole Special attive
        active_special_rules = [
            rule_name
            for rule_name, enabled
            in self.match_rules["special"].items()
            if enabled
        ]

        # se non ci sono regole attive mostro None
        extra_text = (
            ", ".join(active_extra_rules)
            if active_extra_rules
            else "None"
        )

        special_text = (
            ", ".join(active_special_rules)
            if active_special_rules
            else "None"
        )

        # preparo le tre righe del riepilogo
        rules_summary = [
            f"Extra: {extra_text}",
            f"Special: {special_text}",
            f"Trade: {self.match_rules['trade']}"
        ]

        # disegno il riepilogo allineato a sinistra
        for i, rule_text in enumerate(rules_summary):

            rule_surface = self.rules_font.render(
                rule_text,
                True,
                (255, 255, 255)
            )

            rule_rect = rule_surface.get_rect(
                midleft=(
                    x + 45,
                    y + 55 + i * 50
                )
            )

            screen.blit(
                rule_surface,
                rule_rect
            )

        # disegno una linea di separazione
        pygame.draw.line(
            screen,
            (180, 180, 180),
            (x + 35, y + 205),
            (x + self.panel_width - 35, y + 205),
            2
        )

        # preparo la domanda di conferma
        message_surface = self.message_font.render(
            "Return to the main menu?",
            True,
            (255, 255, 255)
        )

        message_rect = message_surface.get_rect(
            center=(
                self.width // 2,
                y + 260
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
                option_color = (255, 255, 255)
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
                    y + 340
                )
            )

            self.option_rects.append(
                option_rect
            )

            screen.blit(
                option_surface,
                option_rect
            )

            # la manina indica Yes oppure No
            if i == self.selected_option:
                self.hand_cursor.draw(
                    screen,
                    option_rect,
                    gap=5
                )