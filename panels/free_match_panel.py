import pygame

from ui.animated_hand_cursor import AnimatedHandCursor # cursore animato riutilizzabile
from panels.panel import Panel


# pannello di preparazione della modalità Free Match
class FreeMatchPanel(Panel):

    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # dimensioni del pannello
        self.panel_width = 900
        self.panel_height = 550

        # colore temporaneo del pannello
        self.color = (100, 100, 100)

        # font del titolo
        self.title_font = pygame.font.SysFont(
            "Arial",
            40
        )

        # font delle opzioni delle regole
        self.option_font = pygame.font.SysFont(
            "Arial",
            30
        )

        # opzioni esclusive relative alla visibilità delle carte
        self.cards_options = [
            "Face Up",
            "Face Down"
        ]

        # Face Up è la scelta predefinita
        self.selected_cards_option = 0

        # rettangoli delle opzioni Face Up e Face Down;
        # servono per rilevare il passaggio e il click del mouse
        self.cards_option_rects = []

        # opzioni esclusive relative alla mano del giocatore
        self.hand_options = [
            "Choice",
            "Random"
        ]

        # Choice è la scelta predefinita
        self.selected_hand_option = 0

        # regole Extra attivabili indipendentemente
        self.extra_rules = {
            "Same": False,
            "Plus": False,
            "Combo": False,
            "Elemental": False
        }

        # regole Special attivabili indipendentemente
        self.special_rules = {
            "Wall": False,
            "Sudden Death": False
        }

        # Trade Rules disponibili; una sola può essere selezionata
        self.trade_rules = [
            "One",
            "Difference",
            "Direct",
            "All"
        ]

        # One è la Trade Rule predefinita
        self.selected_trade_rule = 0

        # righe navigabili del pannello
        self.navigation_rows = [
            "cards",
            "hand",
            "extra",
            "special",
            "randomize",
            "trade",
            "continue"
        ]

        # riga attualmente evidenziata
        self.selected_row = 0

        # opzione evidenziata nelle righe con più regole indipendenti
        self.selected_extra_rule = 0
        self.selected_special_rule = 0

        # manina animata usata per la navigazione
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

    # gestisce gli eventi del pannello
    def handle_events(self, event):

        # ESC chiude il pannello
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()
            # se mi trovo sulla riga Cards, cambio la scelta
            # usando le frecce sinistra e destra
            elif (
                self.navigation_rows[self.selected_row] == "cards"
                and event.key == pygame.K_LEFT
            ):
                self.selected_cards_option = (
                    self.selected_cards_option - 1
                ) % len(self.cards_options)

            elif (
                self.navigation_rows[self.selected_row] == "cards"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_cards_option = (
                    self.selected_cards_option + 1
                ) % len(self.cards_options)

        # la rotella cambia la scelta Cards soltanto quando
        # il mouse si trova sopra Face Up oppure Face Down
        if event.type == pygame.MOUSEWHEEL:

            # MOUSEWHEEL non contiene la posizione del cursore,
            # quindi recupero la posizione attuale del mouse
            mouse_position = pygame.mouse.get_pos()

            # controllo se il mouse si trova sopra una delle due scelte
            mouse_over_cards_option = any(
                option_rect.collidepoint(mouse_position)
                for option_rect in self.cards_option_rects
            )

            if mouse_over_cards_option:

                # rotella verso l'alto: scelta precedente
                if event.y > 0:
                    self.selected_cards_option = (
                        self.selected_cards_option - 1
                    ) % len(self.cards_options)

                # rotella verso il basso: scelta successiva
                elif event.y < 0:
                    self.selected_cards_option = (
                        self.selected_cards_option + 1
                    ) % len(self.cards_options)
                    
        # tasti del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # con il tasto sinistro seleziono una delle opzioni Cards
            if event.button == 1:

                # controllo se è stata cliccata Face Up oppure Face Down
                for i, option_rect in enumerate(
                    self.cards_option_rects
                ):

                    if option_rect.collidepoint(event.pos):

                        # attivo l'opzione cliccata;
                        # colore e manina si aggiorneranno automaticamente
                        self.selected_cards_option = i
                        break

            # il tasto destro chiude il pannello
            elif event.button == 3:
                self.state.close_panel()

    # aggiorna la logica del pannello
    def update(self):
        pass

    # disegna il pannello
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

        # disegno il pannello
        pygame.draw.rect(
            screen,
            self.color,
            panel_rect
        )

        # preparo il titolo temporaneo
        title = self.title_font.render(
            "Free Match",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(self.width // 2, y + 50)
        )

        # disegno il titolo
        screen.blit(title, title_rect)

        # preparo il testo che identifica la prima riga
        cards_label = self.option_font.render(
            "Cards:",
            True,
            (255, 255, 255)
        )

        # posiziono l'etichetta della riga
        cards_label_rect = cards_label.get_rect(
            midleft=(x + 100, y + 140)
        )

        # disegno l'etichetta
        screen.blit(
            cards_label,
            cards_label_rect
        )

        # posizione iniziale delle opzioni della riga Cards
        option_x = cards_label_rect.right + 80

        # conterrà i rettangoli delle due opzioni
        self.cards_option_rects = []

        # disegno Face Up e Face Down
        for i, option in enumerate(self.cards_options):

            # la scelta attiva appare bianca, quella inattiva sbiadita
            if i == self.selected_cards_option:
                option_color = (255, 255, 255)
            else:
                option_color = (120, 120, 120)

            option_surface = self.option_font.render(
                option,
                True,
                option_color
            )

            option_rect = option_surface.get_rect(
                midleft=(option_x, cards_label_rect.centery)
            )

            # salvo il rettangolo per i controlli del mouse
            self.cards_option_rects.append(option_rect)

            # disegno l'opzione
            screen.blit(
                option_surface,
                option_rect
            )

            # preparo la posizione dell'opzione successiva
            option_x = option_rect.right + 90

        # la manina indica sempre la scelta attualmente attiva
        if self.navigation_rows[self.selected_row] == "cards":

            # recupero il rettangolo di Face Up oppure Face Down
            selected_option_rect = self.cards_option_rects[
                self.selected_cards_option
            ]

            # disegno la manina accanto alla scelta attiva
            self.hand_cursor.draw(
                screen,
                selected_option_rect,
                gap=5
            )