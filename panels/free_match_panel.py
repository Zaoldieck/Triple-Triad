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

        # rettangoli delle opzioni Choice e Random;
        # serviranno successivamente per i controlli del mouse
        self.hand_option_rects = []

        # regole Extra attivabili indipendentemente
        self.extra_rules = {
            "Same": False,
            "Plus": False,
            "Combo": False,
            "Elemental": False
        }

        # rettangoli delle regole Extra;
        # serviranno per la navigazione e i controlli del mouse
        self.extra_rule_rects = []

        # regole Special attivabili indipendentemente
        self.special_rules = {
            "Wall": False,
            "Sudden Death": False
        }

        # rettangoli delle regole Special;
        # serviranno per la navigazione e i controlli del mouse
        self.special_rule_rects = []

        # Trade Rules disponibili; una sola può essere selezionata
        self.trade_rules = [
            "One",
            "Difference",
            "Direct",
            "All"
        ]

        # One è la Trade Rule predefinita
        self.selected_trade_rule = 0

        # rettangolo della Trade Rule mostrata;
        # servirà per i controlli del mouse
        self.trade_rule_rect = None

        # righe navigabili del pannello
        self.navigation_rows = [
            "cards",
            "hand",
            "extra",
            "special",
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

        # gestisco i controlli della tastiera
        if event.type == pygame.KEYDOWN:

            # ESC chiude il pannello
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

            # freccia su: seleziono la riga precedente
            elif event.key == pygame.K_UP:

                # per ora sono navigabili Cards, Hand, Extra, Special e Trade
                self.selected_row = (
                    self.selected_row - 1
                ) % 5

            # freccia giù: seleziono la riga successiva
            elif event.key == pygame.K_DOWN:

                # per ora sono navigabili Cards, Hand, Extra, Special e Trade
                self.selected_row = (
                    self.selected_row + 1
                ) % 5

            # sulla riga Cards, la freccia sinistra
            # seleziona l'opzione precedente
            elif (
                self.navigation_rows[self.selected_row] == "cards"
                and event.key == pygame.K_LEFT
            ):
                self.selected_cards_option = (
                    self.selected_cards_option - 1
                ) % len(self.cards_options)

            # sulla riga Cards, la freccia destra
            # seleziona l'opzione successiva
            elif (
                self.navigation_rows[self.selected_row] == "cards"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_cards_option = (
                    self.selected_cards_option + 1
                ) % len(self.cards_options)

            # sulla riga Hand, la freccia sinistra
            # seleziona l'opzione precedente
            elif (
                self.navigation_rows[self.selected_row] == "hand"
                and event.key == pygame.K_LEFT
            ):
                self.selected_hand_option = (
                    self.selected_hand_option - 1
                ) % len(self.hand_options)

            # sulla riga Hand, la freccia destra
            # seleziona l'opzione successiva
            elif (
                self.navigation_rows[self.selected_row] == "hand"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_hand_option = (
                    self.selected_hand_option + 1
                ) % len(self.hand_options)

            # sulla riga Extra, la freccia sinistra sposta
            # la manina sulla regola precedente senza attivarla
            elif (
                self.navigation_rows[self.selected_row] == "extra"
                and event.key == pygame.K_LEFT
            ):
                self.selected_extra_rule = (
                    self.selected_extra_rule - 1
                ) % len(self.extra_rules)

            # sulla riga Extra, la freccia destra sposta
            # la manina sulla regola successiva senza attivarla
            elif (
                self.navigation_rows[self.selected_row] == "extra"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_extra_rule = (
                    self.selected_extra_rule + 1
                ) % len(self.extra_rules)

            # sulla riga Extra, Invio attiva oppure
            # disattiva la regola indicata dalla manina
            elif (
                self.navigation_rows[self.selected_row] == "extra"
                and event.key == pygame.K_RETURN
            ):

                # recupero il nome della regola evidenziata
                selected_rule_name = list(
                    self.extra_rules.keys()
                )[self.selected_extra_rule]

                # inverto lo stato della regola:
                # False diventa True e True diventa False
                self.extra_rules[selected_rule_name] = not (
                    self.extra_rules[selected_rule_name]
                )

            # sulla riga Special, la freccia sinistra sposta
            # la manina sulla regola precedente senza attivarla
            elif (
                self.navigation_rows[self.selected_row] == "special"
                and event.key == pygame.K_LEFT
            ):
                self.selected_special_rule = (
                    self.selected_special_rule - 1
                ) % len(self.special_rules)

            # sulla riga Special, la freccia destra sposta
            # la manina sulla regola successiva senza attivarla
            elif (
                self.navigation_rows[self.selected_row] == "special"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_special_rule = (
                    self.selected_special_rule + 1
                ) % len(self.special_rules)

            # sulla riga Special, Invio attiva oppure
            # disattiva la regola indicata dalla manina
            elif (
                self.navigation_rows[self.selected_row] == "special"
                and event.key == pygame.K_RETURN
            ):

                # recupero il nome della regola evidenziata
                selected_rule_name = list(
                    self.special_rules.keys()
                )[self.selected_special_rule]

                # inverto lo stato della regola:
                # False diventa True e True diventa False
                self.special_rules[selected_rule_name] = not (
                    self.special_rules[selected_rule_name]
                )

            # sulla riga Trade Rules, la freccia sinistra
            # seleziona la regola precedente
            elif (
                self.navigation_rows[self.selected_row] == "trade"
                and event.key == pygame.K_LEFT
            ):
                self.selected_trade_rule = (
                    self.selected_trade_rule - 1
                ) % len(self.trade_rules)

            # sulla riga Trade Rules, la freccia destra
            # seleziona la regola successiva
            elif (
                self.navigation_rows[self.selected_row] == "trade"
                and event.key == pygame.K_RIGHT
            ):
                self.selected_trade_rule = (
                    self.selected_trade_rule + 1
                ) % len(self.trade_rules)



        # il mouse sposta la manina soltanto quando passa
        # sopra un'opzione attualmente attiva e bianca
        if event.type == pygame.MOUSEMOTION:

            # recupero il rettangolo della scelta Cards attiva
            active_cards_rect = self.cards_option_rects[
                self.selected_cards_option
            ]

            # se il mouse è sopra la scelta Cards attiva,
            # sposto la manina sulla riga Cards
            if active_cards_rect.collidepoint(event.pos):
                self.selected_row = self.navigation_rows.index(
                    "cards"
                )

            # recupero il rettangolo della scelta Hand attiva
            active_hand_rect = self.hand_option_rects[
                self.selected_hand_option
            ]

            # se il mouse è sopra la scelta Hand attiva,
            # sposto la manina sulla riga Hand
            if active_hand_rect.collidepoint(event.pos):
                self.selected_row = self.navigation_rows.index(
                    "hand"
                )

            # controllo tutti i rettangoli delle regole Extra
            for i, rule_rect in enumerate(
                self.extra_rule_rects
            ):

                # se il mouse passa sopra una regola Extra,
                # sposto la manina su quella regola senza attivarla
                if rule_rect.collidepoint(event.pos):
                    self.selected_extra_rule = i
                    self.selected_row = self.navigation_rows.index(
                        "extra"
                    )
                    break

            # controllo tutti i rettangoli delle regole Special
            for i, rule_rect in enumerate(
                self.special_rule_rects
            ):

                # se il mouse passa sopra una regola Special,
                # sposto la manina senza attivare la regola
                if rule_rect.collidepoint(event.pos):
                    self.selected_special_rule = i
                    self.selected_row = self.navigation_rows.index(
                        "special"
                    )
                    break

            # se il mouse passa sopra la Trade Rule mostrata,
            # sposto la manina sulla riga Trade Rules
            if (
                self.trade_rule_rect is not None
                and self.trade_rule_rect.collidepoint(event.pos)
            ):
                self.selected_row = self.navigation_rows.index(
                    "trade"
                )

            





            

        # la rotella cambia una scelta soltanto quando
        # il mouse si trova sopra le opzioni della relativa riga
        if event.type == pygame.MOUSEWHEEL:

            # MOUSEWHEEL non contiene la posizione del cursore,
            # quindi recupero la posizione attuale del mouse
            mouse_position = pygame.mouse.get_pos()

            # controllo se il mouse si trova sopra
            # Face Up oppure Face Down
            mouse_over_cards_option = any(
                option_rect.collidepoint(mouse_position)
                for option_rect in self.cards_option_rects
            )

            # controllo se il mouse si trova sopra
            # Choice oppure Random
            mouse_over_hand_option = any(
                option_rect.collidepoint(mouse_position)
                for option_rect in self.hand_option_rects
            )

            # controllo se il mouse si trova sopra
            # una delle regole della riga Extra
            mouse_over_extra_rule = any(
                rule_rect.collidepoint(mouse_position)
                for rule_rect in self.extra_rule_rects
            )

            # controllo se il mouse si trova sopra
            # una delle regole della riga Special
            mouse_over_special_rule = any(
                rule_rect.collidepoint(mouse_position)
                for rule_rect in self.special_rule_rects
            )

            # controllo se il mouse si trova sopra
            # l'area compresa tra le frecce della Trade Rule
            mouse_over_trade_rule = (
                self.trade_rule_rect is not None
                and self.trade_rule_rect.collidepoint(
                    mouse_position
                )
            )

            # cambio la scelta della riga Cards
            if mouse_over_cards_option:

                if event.y > 0:
                    self.selected_cards_option = (
                        self.selected_cards_option - 1
                    ) % len(self.cards_options)

                elif event.y < 0:
                    self.selected_cards_option = (
                        self.selected_cards_option + 1
                    ) % len(self.cards_options)

                # porto la manina sulla scelta Cards appena modificata
                self.selected_row = self.navigation_rows.index(
                    "cards"
                )

            # cambio la scelta della riga Hand
            elif mouse_over_hand_option:

                if event.y > 0:
                    self.selected_hand_option = (
                        self.selected_hand_option - 1
                    ) % len(self.hand_options)

                elif event.y < 0:
                    self.selected_hand_option = (
                        self.selected_hand_option + 1
                    ) % len(self.hand_options)

                # porto la manina sulla scelta Hand appena modificata
                self.selected_row = self.navigation_rows.index(
                    "hand"
                )

            # sposto la manina tra le regole Extra
            # senza modificare il loro stato
            elif mouse_over_extra_rule:

                # rotella verso l'alto: regola precedente
                if event.y > 0:
                    self.selected_extra_rule = (
                        self.selected_extra_rule - 1
                    ) % len(self.extra_rules)

                # rotella verso il basso: regola successiva
                elif event.y < 0:
                    self.selected_extra_rule = (
                        self.selected_extra_rule + 1
                    ) % len(self.extra_rules)

                # porto la manina sulla riga Extra
                self.selected_row = self.navigation_rows.index(
                    "extra"
                )

            # sposto la manina tra le regole Special
            # senza modificare il loro stato
            elif mouse_over_special_rule:

                # rotella verso l'alto: regola precedente
                if event.y > 0:
                    self.selected_special_rule = (
                        self.selected_special_rule - 1
                    ) % len(self.special_rules)

                # rotella verso il basso: regola successiva
                elif event.y < 0:
                    self.selected_special_rule = (
                        self.selected_special_rule + 1
                    ) % len(self.special_rules)

                # porto la manina sulla riga Special
                self.selected_row = self.navigation_rows.index(
                    "special"
                )

            # cambio la Trade Rule quando la rotella
            # viene usata sopra la relativa area
            elif mouse_over_trade_rule:

                # rotella verso l'alto: Trade Rule precedente
                if event.y > 0:
                    self.selected_trade_rule = (
                        self.selected_trade_rule - 1
                    ) % len(self.trade_rules)

                # rotella verso il basso: Trade Rule successiva
                elif event.y < 0:
                    self.selected_trade_rule = (
                        self.selected_trade_rule + 1
                    ) % len(self.trade_rules)

                # porto la manina sulla riga Trade Rules
                self.selected_row = self.navigation_rows.index(
                    "trade"
                )

                
        # tasti del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # con il tasto sinistro seleziono una delle opzioni Cards
            if event.button == 1:

                # controllo se è stata cliccata Face Up oppure Face Down
                for i, option_rect in enumerate(
                    self.cards_option_rects
                ):

                    if option_rect.collidepoint(event.pos):

                        # attivo l'opzione Cards cliccata
                        self.selected_cards_option = i

                        # sposto la manina sulla riga Cards
                        self.selected_row = self.navigation_rows.index(
                            "cards"
                        )
                        break

                # controllo se è stata cliccata Choice oppure Random
                for i, option_rect in enumerate(
                    self.hand_option_rects
                ):

                    if option_rect.collidepoint(event.pos):

                        # attivo l'opzione Hand cliccata
                        self.selected_hand_option = i

                        # sposto la manina sulla riga Hand
                        self.selected_row = self.navigation_rows.index(
                            "hand"
                        )
                        break

                # controllo se è stata cliccata una regola Extra
                for i, rule_rect in enumerate(
                    self.extra_rule_rects
                ):

                    if rule_rect.collidepoint(event.pos):

                        # recupero il nome della regola cliccata
                        selected_rule_name = list(
                            self.extra_rules.keys()
                        )[i]

                        # attivo la regola se era disattivata,
                        # oppure la disattivo se era attiva
                        self.extra_rules[selected_rule_name] = not (
                            self.extra_rules[selected_rule_name]
                        )

                        # sposto la manina sulla regola cliccata
                        self.selected_extra_rule = i
                        self.selected_row = self.navigation_rows.index(
                            "extra"
                        )
                        break

                # controllo se è stata cliccata una regola Special
                for i, rule_rect in enumerate(
                    self.special_rule_rects
                ):

                    if rule_rect.collidepoint(event.pos):

                        # recupero il nome della regola cliccata
                        selected_rule_name = list(
                            self.special_rules.keys()
                        )[i]

                        # attivo la regola se era disattivata,
                        # oppure la disattivo se era attiva
                        self.special_rules[selected_rule_name] = not (
                            self.special_rules[selected_rule_name]
                        )

                        # sposto la manina sulla regola cliccata
                        self.selected_special_rule = i
                        self.selected_row = self.navigation_rows.index(
                            "special"
                        )
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

        # preparo il testo che identifica la riga Hand
        hand_label = self.option_font.render(
            "Hand:",
            True,
            (255, 255, 255)
        )

        # posiziono Hand sotto la riga Cards
        hand_label_rect = hand_label.get_rect(
            midleft=(x + 100, y + 200)
        )

        # disegno l'etichetta della riga
        screen.blit(
            hand_label,
            hand_label_rect
        )

        # lascio spazio per la manina prima della prima scelta
        option_x = hand_label_rect.right + 80

        # svuoto i vecchi rettangoli prima di ricrearli
        self.hand_option_rects = []

        # disegno Choice e Random
        for i, option in enumerate(self.hand_options):

            # la scelta attiva appare bianca, quella inattiva sbiadita
            if i == self.selected_hand_option:
                option_color = (255, 255, 255)
            else:
                option_color = (120, 120, 120)

            option_surface = self.option_font.render(
                option,
                True,
                option_color
            )

            option_rect = option_surface.get_rect(
                midleft=(option_x, hand_label_rect.centery)
            )

            # salvo il rettangolo per i futuri controlli del mouse
            self.hand_option_rects.append(option_rect)

            # disegno l'opzione
            screen.blit(
                option_surface,
                option_rect
            )

            # lascio spazio sufficiente per la manina
            # davanti all'opzione successiva
            option_x = option_rect.right + 90

        # quando la riga Hand sarà selezionata,
        # la manina indicherà sempre la scelta attiva
        if self.navigation_rows[self.selected_row] == "hand":

            selected_option_rect = self.hand_option_rects[
                self.selected_hand_option
            ]

            self.hand_cursor.draw(
                screen,
                selected_option_rect,
                gap=5
            )

        # preparo il testo che identifica la riga Extra
        extra_label = self.option_font.render(
            "Extra:",
            True,
            (255, 255, 255)
        )

        # posiziono Extra sotto la riga Hand
        extra_label_rect = extra_label.get_rect(
            midleft=(x + 100, y + 260)
        )

        # disegno l'etichetta della riga
        screen.blit(
            extra_label,
            extra_label_rect
        )

        # lascio spazio per la manina prima della prima regola
        option_x = extra_label_rect.right + 80

        # svuoto i vecchi rettangoli prima di ricrearli
        self.extra_rule_rects = []

        # disegno tutte le regole Extra
        for rule_name, rule_active in self.extra_rules.items():

            # una regola attiva appare bianca;
            # una regola disattivata appare sbiadita
            if rule_active:
                rule_color = (255, 255, 255)
            else:
                rule_color = (120, 120, 120)

            rule_surface = self.option_font.render(
                rule_name,
                True,
                rule_color
            )

            rule_rect = rule_surface.get_rect(
                midleft=(option_x, extra_label_rect.centery)
            )

            # salvo il rettangolo per i futuri controlli
            self.extra_rule_rects.append(rule_rect)

            # disegno il nome della regola
            screen.blit(
                rule_surface,
                rule_rect
            )

            # preparo la posizione della regola successiva
            option_x = rule_rect.right + 65

        # quando la riga Extra è selezionata,
        # la manina indica la regola attualmente evidenziata
        if self.navigation_rows[self.selected_row] == "extra":

            selected_rule_rect = self.extra_rule_rects[
                self.selected_extra_rule
            ]

            self.hand_cursor.draw(
                screen,
                selected_rule_rect,
                gap=5
            )

        # preparo il testo che identifica la riga Special
        special_label = self.option_font.render(
            "Special:",
            True,
            (255, 255, 255)
        )

        # posiziono Special sotto la riga Extra
        special_label_rect = special_label.get_rect(
            midleft=(x + 100, y + 320)
        )

        # disegno l'etichetta della riga
        screen.blit(
            special_label,
            special_label_rect
        )

        # lascio spazio per la manina prima della prima regola
        option_x = special_label_rect.right + 80

        # svuoto i vecchi rettangoli prima di ricrearli
        self.special_rule_rects = []

        # disegno tutte le regole Special
        for rule_name, rule_active in self.special_rules.items():

            # una regola attiva appare bianca;
            # una regola disattivata appare sbiadita
            if rule_active:
                rule_color = (255, 255, 255)
            else:
                rule_color = (120, 120, 120)

            rule_surface = self.option_font.render(
                rule_name,
                True,
                rule_color
            )

            rule_rect = rule_surface.get_rect(
                midleft=(option_x, special_label_rect.centery)
            )

            # salvo il rettangolo per i futuri controlli
            self.special_rule_rects.append(rule_rect)

            # disegno il nome della regola
            screen.blit(
                rule_surface,
                rule_rect
            )

            # preparo la posizione della regola successiva
            option_x = rule_rect.right + 65

        # quando la riga Special è selezionata,
        # la manina indica la regola attualmente evidenziata
        if self.navigation_rows[self.selected_row] == "special":

            selected_rule_rect = self.special_rule_rects[
                self.selected_special_rule
            ]

            self.hand_cursor.draw(
                screen,
                selected_rule_rect,
                gap=5
            )

        # preparo il testo che identifica la riga Trade Rules
        trade_label = self.option_font.render(
            "Trade Rules:",
            True,
            (255, 255, 255)
        )

        # posiziono Trade Rules sotto la riga Special
        trade_label_rect = trade_label.get_rect(
            midleft=(x + 100, y + 380)
        )

        # disegno l'etichetta della riga
        screen.blit(
            trade_label,
            trade_label_rect
        )

        # recupero il nome della Trade Rule attualmente selezionata
        selected_trade_name = self.trade_rules[
            self.selected_trade_rule
        ]

        # definisco uno spazio fisso per la Trade Rule;
        # in questo modo le due frecce non cambiano posizione
        trade_area_x = trade_label_rect.right + 80
        trade_area_width = 220

        # preparo separatamente la freccia sinistra,
        # il nome della regola e la freccia destra
        left_arrow_surface = self.option_font.render(
            "<",
            True,
            (255, 255, 255)
        )

        trade_name_surface = self.option_font.render(
            selected_trade_name,
            True,
            (255, 255, 255)
        )

        right_arrow_surface = self.option_font.render(
            ">",
            True,
            (255, 255, 255)
        )

        # la freccia sinistra rimane sempre nella stessa posizione
        left_arrow_rect = left_arrow_surface.get_rect(
            midleft=(
                trade_area_x,
                trade_label_rect.centery
            )
        )

        # il nome della regola rimane centrato
        # nello spazio compreso tra le due frecce
        trade_name_rect = trade_name_surface.get_rect(
            center=(
                trade_area_x + trade_area_width // 2,
                trade_label_rect.centery
            )
        )

        # la freccia destra rimane sempre nella stessa posizione
        right_arrow_rect = right_arrow_surface.get_rect(
            midright=(
                trade_area_x + trade_area_width,
                trade_label_rect.centery
            )
        )

        # creo un rettangolo unico che comprende frecce e nome;
        # servirà per la manina e per i controlli del mouse
        self.trade_rule_rect = left_arrow_rect.union(
            right_arrow_rect
        )

        # disegno le due frecce e la regola selezionata
        screen.blit(
            left_arrow_surface,
            left_arrow_rect
        )

        screen.blit(
            trade_name_surface,
            trade_name_rect
        )

        screen.blit(
            right_arrow_surface,
            right_arrow_rect
        )

        # quando la riga Trade Rules è selezionata,
        # la manina indica la regola attualmente mostrata
        if self.navigation_rows[self.selected_row] == "trade":
            self.hand_cursor.draw(
                screen,
                self.trade_rule_rect,
                gap=5
            )