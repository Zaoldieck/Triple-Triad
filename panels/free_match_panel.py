import pygame
# funzione che carica le carte mantenendo l'ordine di cards.json
from game.card_loader import load_cards
# funzione che costruisce graficamente una carta
from renderers.card_renderer import render_card
# set di carte abilitati nella versione corrente
from config import ACTIVE_CARD_SETS
# pannello che conferma le cinque carte selezionate
from panels.play_confirmation_panel import PlayConfirmationPanel
from ui.animated_hand_cursor import AnimatedHandCursor # cursore animato riutilizzabile
from panels.panel import Panel
# schermata nella quale viene giocata la partita
from screens.match_screen import MatchScreen
from screens.trade_screen import TradeScreen

# pannello di preparazione della modalità Free Match
class FreeMatchPanel(Panel):

    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # fase attuale della preparazione della partita;
        # inizialmente il giocatore configura le regole
        self.current_phase = "rules"

        # massimo numero di carte utilizzabili in una partita
        self.max_selected_cards = 5

        # massimo numero di carte mostrate in ogni pagina
        self.cards_per_selection_page = 11

        # carico il catalogo mantenendo l'ordine presente in cards.json
        loaded_cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # conterrà soltanto le carte utilizzabili nella partita
        self.available_cards = []

        # filtro il catalogo in base alle quantità possedute
        for card in loaded_cards:

            # None identifica una carta posseduta in quantità infinita
            quantity = self.state.card_collection.get_quantity(
                card
            )

            # aggiungo le carte infinite e quelle con quantità da 1 a 99;
            # le carte con quantità zero non appaiono nella selezione
            if quantity is None or 1 <= quantity <= 99:
                self.available_cards.append(card)

        # carte scelte dal giocatore, conservate
        # nello stesso ordine in cui vengono selezionate
        self.selected_cards = []

        # pagina attualmente mostrata nella lista delle carte
        self.card_selection_page = 0

        # posizione della manina nella pagina corrente
        self.selected_card_row = 0

        # rettangoli delle righe mostrate nella pagina corrente;
        # serviranno per hover e click del mouse
        self.card_selection_rects = []

        # superficie contenente l'anteprima della carta indicata
        self.selection_card_preview = None

        # identificatore della carta attualmente mostrata;
        # evita di ricostruire la stessa anteprima a ogni frame
        self.selection_preview_card_id = None

        # cache delle versioni ridotte delle carte selezionate;
        # evita di ricostruirle graficamente a ogni frame
        self.selected_card_surfaces = {}

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

        # font più piccolo usato nella lista di selezione delle carte
        self.card_list_font = pygame.font.SysFont(
            "Arial",
            21
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

        # rettangolo del comando Continue;
        # servirà per tastiera e controlli del mouse
        self.continue_rect = None

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

    # cambia la pagina mostrata nella selezione delle carte
    def change_card_selection_page(self, direction):

        # calcolo dinamicamente il numero totale di pagine
        total_pages = max(
            1,
            (
                len(self.available_cards)
                + self.cards_per_selection_page
                - 1
            ) // self.cards_per_selection_page
        )

        # interrompo se esiste una sola pagina
        if total_pages <= 1:
            return

        # cambio pagina ciclicamente
        self.card_selection_page = (
            self.card_selection_page + direction
        ) % total_pages

        # calcolo quante carte contiene la nuova pagina
        start_index = (
            self.card_selection_page
            * self.cards_per_selection_page
        )

        cards_on_new_page = min(
            self.cards_per_selection_page,
            len(self.available_cards) - start_index
        )

        # mantengo la stessa riga quando esiste;
        # altrimenti riporto la manina sulla prima carta
        if self.selected_card_row >= cards_on_new_page:
            self.selected_card_row = 0

        # obbligo l'anteprima ad aggiornarsi
        self.selection_preview_card_id = None

    # seleziona oppure deseleziona la carta indicata
    def toggle_selected_card(self):

        # calcolo l'indice della carta nell'intera lista
        card_index = (
            self.card_selection_page
            * self.cards_per_selection_page
            + self.selected_card_row
        )

        # interrompo se la posizione non contiene una carta
        if card_index >= len(self.available_cards):
            return

        # recupero la carta indicata
        selected_card = self.available_cards[
            card_index
        ]

        # cerco la carta tra quelle già selezionate
        for card in self.selected_cards:

            # se era già selezionata, la rimuovo
            if card.card_id == selected_card.card_id:
                self.selected_cards.remove(card)
                return

        # non permetto di selezionare più di cinque carte
        if len(self.selected_cards) >= self.max_selected_cards:
            return

        # aggiungo la carta mantenendo l'ordine di selezione
        self.selected_cards.append(
            selected_card
        )

        # quando viene selezionata la quinta carta,
        # apro il pannello di conferma della mano
        if len(self.selected_cards) == self.max_selected_cards:
            self.state.open_panel(
                PlayConfirmationPanel(
                    self.width,
                    self.height,
                    self.state,
                    self
                )
            )

    # aggiorna l'anteprima della carta indicata nella lista
    def update_selection_card_preview(self):

        # calcolo l'indice della carta nell'intera lista
        card_index = (
            self.card_selection_page
            * self.cards_per_selection_page
            + self.selected_card_row
        )

        # se non esiste una carta in questa posizione,
        # rimuovo l'anteprima
        if card_index >= len(self.available_cards):
            self.selection_card_preview = None
            self.selection_preview_card_id = None
            return

        # recupero la carta indicata
        selected_card = self.available_cards[
            card_index
        ]

        # evito di ricostruire la stessa carta a ogni frame
        if (
            selected_card.card_id
            == self.selection_preview_card_id
        ):
            return

        # costruisco il fronte blu della carta
        self.selection_card_preview = render_card(
            selected_card,
            "blue"
        )

        # ridimensiono l'anteprima mantenendo
        # le proporzioni originali della carta
        self.selection_card_preview = (
            pygame.transform.smoothscale(
                self.selection_card_preview,
                (150, 190)
            )
        )

        # salvo l'identificatore della carta mostrata
        self.selection_preview_card_id = (
            selected_card.card_id
        )

    # attiva o disattiva una regola Extra
    # rispettando le dipendenze tra le regole
    def toggle_extra_rule(self, rule_name):

        # Combo può essere attivata soltanto se
        # almeno una tra Same e Plus è attiva
        if (
            rule_name == "Combo"
            and not self.extra_rules["Combo"]
            and not self.extra_rules["Same"]
            and not self.extra_rules["Plus"]
        ):
            return

        # inverto lo stato della regola richiesta
        self.extra_rules[rule_name] = not (
            self.extra_rules[rule_name]
        )

        # se Same viene disattivata,
        # Wall non può rimanere attiva
        if (
            rule_name == "Same"
            and not self.extra_rules["Same"]
        ):
            self.special_rules["Wall"] = False

        # se Same e Plus sono entrambe disattivate,
        # anche Combo deve essere disattivata automaticamente
        if (
            not self.extra_rules["Same"]
            and not self.extra_rules["Plus"]
        ):
            self.extra_rules["Combo"] = False

    # attiva o disattiva una regola Special
    # rispettando le sue eventuali dipendenze
    def toggle_special_rule(self, rule_name):

        # inverto lo stato della regola richiesta
        self.special_rules[rule_name] = not (
            self.special_rules[rule_name]
        )

        # Wall utilizza la meccanica di Same;
        # attivandola abilito automaticamente anche Same
        if (
            rule_name == "Wall"
            and self.special_rules["Wall"]
        ):
            self.extra_rules["Same"] = True

    # raccoglie tutte le regole attualmente configurate
    def get_match_rules(self):

        return {
            "cards": self.cards_options[
                self.selected_cards_option
            ],
            "hand": self.hand_options[
                self.selected_hand_option
            ],
            "extra": self.extra_rules.copy(),
            "special": self.special_rules.copy(),
            "trade": self.trade_rules[
                self.selected_trade_rule
            ]
        }

    # continua dalla configurazione delle regole
    def continue_from_rules(self):

        # recupero la modalità della mano selezionata
        selected_hand_rule = self.hand_options[
            self.selected_hand_option
        ]

        # con Random salto completamente
        # la selezione manuale delle carte
        if selected_hand_rule == "Random":

            match_screen = MatchScreen(
                self.width,
                self.height,
                self.state,
                [],
                self.get_match_rules()
            )

            # attivo direttamente la partita
            self.state.change_screen(
                match_screen
            )

            # chiudo il Free Match Panel
            self.state.close_panel()

        # con Choice passo normalmente
        # alla selezione manuale delle cinque carte
        else:
            self.current_phase = "card_selection"

    # gestisce gli eventi del pannello
    def handle_events(self, event):

        # gestisco separatamente gli eventi della selezione carte
        if self.current_phase == "card_selection":

            # controllo la tastiera
            if event.type == pygame.KEYDOWN:

                # ESC chiude completamente il pannello
                if event.key == pygame.K_ESCAPE:
                    self.state.close_panel()

                # calcolo quante carte sono presenti nella pagina corrente
                start_index = (
                    self.card_selection_page
                    * self.cards_per_selection_page
                )

                cards_on_page = min(
                    self.cards_per_selection_page,
                    len(self.available_cards) - start_index
                )

                # sposto la manina sulla carta precedente
                if event.key == pygame.K_UP and cards_on_page > 0:
                    self.selected_card_row = (
                        self.selected_card_row - 1
                    ) % cards_on_page

                # sposto la manina sulla carta successiva
                elif event.key == pygame.K_DOWN and cards_on_page > 0:
                    self.selected_card_row = (
                        self.selected_card_row + 1
                    ) % cards_on_page

                # freccia sinistra: pagina precedente
                elif event.key == pygame.K_LEFT:
                    self.change_card_selection_page(-1)

                # freccia destra: pagina successiva
                elif event.key == pygame.K_RIGHT:
                    self.change_card_selection_page(1)
                

                # Invio seleziona oppure deseleziona
                # la carta indicata dalla manina
                elif event.key == pygame.K_RETURN:
                    self.toggle_selected_card()

            # se il mouse si muove sopra la lista delle carte
            if event.type == pygame.MOUSEMOTION:

                # controllo tutti i rettangoli della pagina corrente
                for i, card_rect in enumerate(
                    self.card_selection_rects
                ):

                    # se il mouse si trova sopra una carta,
                    # sposto immediatamente la manina su quella riga
                    if card_rect.collidepoint(event.pos):
                        self.selected_card_row = i
                        break

            # la rotella del mouse cambia la pagina
            # della lista delle carte possedute
            if event.type == pygame.MOUSEWHEEL:

                # rotella verso l'alto: pagina precedente
                if event.y > 0:
                    self.change_card_selection_page(-1)

                # rotella verso il basso: pagina successiva
                elif event.y < 0:
                    self.change_card_selection_page(1)
            
            # controllo i click del mouse nella lista delle carte
            if event.type == pygame.MOUSEBUTTONDOWN:

                # il tasto sinistro seleziona oppure deseleziona
                # la carta presente nella riga cliccata
                if event.button == 1:

                    for i, card_rect in enumerate(
                        self.card_selection_rects
                    ):

                        if card_rect.collidepoint(event.pos):

                            # sposto la manina sulla carta cliccata
                            self.selected_card_row = i

                            # alterno lo stato selezionato/deselezionato
                            self.toggle_selected_card()
                            break

                # il tasto destro torna indietro di uno step
                elif event.button == 3:

                    # se ci sono carte selezionate,
                    # rimuovo l'ultima carta aggiunta
                    if self.selected_cards:
                        self.selected_cards.pop()

                    # se non è stata selezionata alcuna carta,
                    # torno alla configurazione delle regole
                    else:
                        self.current_phase = "rules"

            # impedisco agli eventi della seconda fase
            # di modificare le regole nascoste
            return
        
        # gestisco i controlli della tastiera
        if event.type == pygame.KEYDOWN:

            # ESC chiude il pannello
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

            # freccia su: seleziono la riga precedente
            elif event.key == pygame.K_UP:

                # navigo ciclicamente tra tutte le righe del pannello
                self.selected_row = (
                    self.selected_row - 1
                ) % len(self.navigation_rows)

            # freccia giù: seleziono la riga successiva
            elif event.key == pygame.K_DOWN:

                # navigo ciclicamente tra tutte le righe del pannello
                self.selected_row = (
                    self.selected_row + 1
                ) % len(self.navigation_rows)

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

                # modifico la regola rispettando
                # le dipendenze di Combo
                self.toggle_extra_rule(
                    selected_rule_name
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
                self.toggle_special_rule(
                    selected_rule_name
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

            # quando la manina si trova su Continue,
            # Invio passa alla fase di selezione delle carte
            elif (
                self.navigation_rows[self.selected_row] == "continue"
                and event.key == pygame.K_RETURN
            ):
                self.continue_from_rules()



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

            # se il mouse passa sopra Continue,
            # sposto la manina sul comando senza attivarlo
            if (
                self.continue_rect is not None
                and self.continue_rect.collidepoint(event.pos)
            ):
                self.selected_row = self.navigation_rows.index(
                    "continue"
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

                        # modifico la regola rispettando
                        # le dipendenze di Combo
                        self.toggle_extra_rule(
                            selected_rule_name
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
                        self.toggle_special_rule(
                            selected_rule_name
                        )

                        # sposto la manina sulla regola cliccata
                        self.selected_special_rule = i
                        self.selected_row = self.navigation_rows.index(
                            "special"
                        )
                        break

                # se clicco su Continue,
                # applico il comportamento di Choice oppure Random
                if (
                    self.continue_rect is not None
                    and self.continue_rect.collidepoint(event.pos)
                ):
                    self.continue_from_rules()
                    
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

        # scelgo il titolo in base alla fase attuale
        if self.current_phase == "rules":
            title_text = "Free Match"
        else:
            title_text = "Card Selection"

        # preparo il titolo della fase attuale
        title = self.title_font.render(
            title_text,
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(self.width // 2, y + 50)
        )

        # disegno il titolo
        screen.blit(title, title_rect)

        # nella seconda fase disegno la lista delle carte possedute
        if self.current_phase == "card_selection":

            # creo l'area che contiene la lista
            card_list_rect = pygame.Rect(
                x + 35,
                y + 90,
                390,
                420
            )

            # disegno lo sfondo della lista
            pygame.draw.rect(
                screen,
                (70, 70, 70),
                card_list_rect
            )

            # dimensioni compatte delle 11 righe
            slot_height = 32
            slot_spacing = 4

            # calcolo la prima carta della pagina corrente
            start_index = (
                self.card_selection_page
                * self.cards_per_selection_page
            )

            # recupero al massimo 11 carte
            page_cards = self.available_cards[
                start_index:
                start_index + self.cards_per_selection_page
            ]

            # svuoto i rettangoli della pagina precedente
            self.card_selection_rects = []

            # disegno soltanto le righe che contengono una carta
            for i, card in enumerate(page_cards):

                slot_rect = pygame.Rect(
                    card_list_rect.x + 10,
                    card_list_rect.y
                    + 10
                    + i * (slot_height + slot_spacing),
                    card_list_rect.width - 20,
                    slot_height
                )

                # salvo il rettangolo per i futuri controlli
                self.card_selection_rects.append(
                    slot_rect
                )

                # disegno lo sfondo della riga
                pygame.draw.rect(
                    screen,
                    (50, 50, 50),
                    slot_rect
                )

                # recupero la quantità posseduta
                quantity = self.state.card_collection.get_quantity(
                    card
                )

                # le carte di rarità 1 mostrano il simbolo infinito
                if quantity is None:
                    quantity_text = "∞"
                else:
                    quantity_text = f"x{quantity}"

                # controllo se la carta è già stata scelta
                card_is_selected = any(
                    selected_card.card_id == card.card_id
                    for selected_card in self.selected_cards
                )

                # una carta già scelta appare sbiadita
                if card_is_selected:
                    card_text_color = (120, 120, 120)
                else:
                    card_text_color = (255, 255, 255)

                # preparo il nome della carta
                card_name_surface = self.card_list_font.render(
                    card.name,
                    True,
                    card_text_color
                )

                card_name_rect = card_name_surface.get_rect(
                    midleft=(
                        slot_rect.x + 12,
                        slot_rect.centery
                    )
                )

                # preparo la quantità posseduta
                quantity_surface = self.card_list_font.render(
                    quantity_text,
                    True,
                    card_text_color
                )

                quantity_rect = quantity_surface.get_rect(
                    midright=(
                        slot_rect.right - 12,
                        slot_rect.centery
                    )
                )

                # disegno nome e quantità
                screen.blit(
                    card_name_surface,
                    card_name_rect
                )

                screen.blit(
                    quantity_surface,
                    quantity_rect
                )

            # calcolo dinamicamente il numero totale
            # delle pagine della selezione carte
            selection_total_pages = max(
                1,
                (
                    len(self.available_cards)
                    + self.cards_per_selection_page
                    - 1
                ) // self.cards_per_selection_page
            )

            # preparo il testo della pagina corrente
            selection_page_surface = self.card_list_font.render(
                (
                    f"Page {self.card_selection_page + 1}"
                    f" / {selection_total_pages}"
                ),
                True,
                (255, 255, 255)
            )

            # posiziono il testo sotto la lista delle carte
            selection_page_rect = selection_page_surface.get_rect(
                center=(
                    card_list_rect.centerx,
                    card_list_rect.bottom + 16
                )
            )

            # disegno il numero della pagina
            screen.blit(
                selection_page_surface,
                selection_page_rect
            )

            # preparo il contatore delle carte selezionate
            selected_cards_count_surface = self.card_list_font.render(
                (
                    f"Cards {len(self.selected_cards)}"
                    f" / {self.max_selected_cards}"
                ),
                True,
                (255, 255, 255)
            )

            # posiziono il contatore a destra,
            # alla stessa altezza del numero della pagina
            selected_cards_count_rect = (
                selected_cards_count_surface.get_rect(
                    center=(
                        x + 662,
                        card_list_rect.bottom + 16
                    )
                )
            )

            # disegno il contatore delle carte selezionate
            screen.blit(
                selected_cards_count_surface,
                selected_cards_count_rect
            )

            # aggiorno l'anteprima in base alla carta indicata
            self.update_selection_card_preview()

            # disegno l'anteprima nella parte destra del pannello
            if self.selection_card_preview is not None:

                selection_preview_rect = (
                    self.selection_card_preview.get_rect(
                        center=(
                            x + 662,
                            y + 186
                        )
                    )
                )

                screen.blit(
                    self.selection_card_preview,
                    selection_preview_rect
                )

                # dimensioni delle carte mostrate nella mano scelta
                selected_card_size = (130, 164)

                # posizione iniziale della prima carta scelta
                selected_cards_x = x + 460
                selected_cards_y = y + 345

                # ogni carta successiva viene spostata verso destra;
                # il valore è circa metà della larghezza della carta
                selected_card_offset = 70

                # disegno le carte nello stesso ordine di selezione
                for i, selected_card in enumerate(
                    self.selected_cards
                ):

                    # costruisco la superficie soltanto la prima volta
                    if (
                        selected_card.card_id
                        not in self.selected_card_surfaces
                    ):
                        selected_surface = render_card(
                            selected_card,
                            "blue"
                        )

                        selected_surface = pygame.transform.smoothscale(
                            selected_surface,
                            selected_card_size
                        )

                        self.selected_card_surfaces[
                            selected_card.card_id
                        ] = selected_surface

                    # recupero la superficie dalla cache
                    selected_surface = self.selected_card_surfaces[
                        selected_card.card_id
                    ]

                    # ogni nuova carta è leggermente spostata a destra
                    selected_card_position = (
                        selected_cards_x + i * selected_card_offset,
                        selected_cards_y
                    )

                    # le carte vengono disegnate in ordine;
                    # quelle nuove appaiono sopra le precedenti
                    screen.blit(
                        selected_surface,
                        selected_card_position
                    )

            # se nella pagina è presente almeno una carta,
            # disegno la manina sulla riga selezionata
            if self.card_selection_rects:

                # se la posizione precedente non esiste nella nuova pagina,
                # riporto la manina sulla prima carta
                if (
                    self.selected_card_row
                    >= len(self.card_selection_rects)
                ):
                    self.selected_card_row = 0

                # recupero il rettangolo della carta selezionata
                selected_card_rect = self.card_selection_rects[
                    self.selected_card_row
                ]

                # disegno la manina accanto alla riga
                self.hand_cursor.draw(
                    screen,
                    selected_card_rect,
                    gap=5
                )
                    
            # interrompo il disegno per non mostrare
            # anche le regole della prima fase
            return



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

        # preparo il comando per confermare le regole
        # e passare alla selezione delle carte
        continue_surface = self.option_font.render(
            "Continue",
            True,
            (255, 255, 255)
        )

        # posiziono Continue sotto Trade Rules,
        # mantenendo la stessa distanza verticale di 60 pixel
        self.continue_rect = continue_surface.get_rect(
            center=(
                self.width // 2,
                y + 500
            )
        )

        # disegno il comando Continue
        screen.blit(
            continue_surface,
            self.continue_rect
        )

        # quando Continue è selezionato,
        # disegno la manina accanto al comando
        if self.navigation_rows[self.selected_row] == "continue":
            self.hand_cursor.draw(
                screen,
                self.continue_rect,
                gap=5
            )