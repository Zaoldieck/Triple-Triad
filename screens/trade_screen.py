import pygame
import random

from screens.screen import Screen
from renderers.card_renderer import render_card
from ui.animated_hand_cursor import AnimatedHandCursor
from config import CARD_BACK_PATH
from game.save_manager import save_card_collection
from panels.trade_card_confirmation_panel import (
    TradeCardConfirmationPanel
)
from panels.play_again_panel import PlayAgainPanel

# schermata che gestisce lo scambio
# delle carte al termine della partita
class TradeScreen(Screen):

    def __init__(
        self,
        width,
        height,
        state,
        player_cards,
        opponent_cards,
        match_rules,
        match_result,
        player_score,
        opponent_score,
        player_card_final_owners=None,
        opponent_card_final_owners=None
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # conservo le mani utilizzate nella partita
        self.player_cards = list(
            player_cards
        )

        self.opponent_cards = list(
            opponent_cards
        )

        # se i proprietari finali non sono stati forniti,
        # mantengo i colori originali delle due mani
        if player_card_final_owners is None:
            player_card_final_owners = [
                "player"
                for card in self.player_cards
            ]

        if opponent_card_final_owners is None:
            opponent_card_final_owners = [
                "opponent"
                for card in self.opponent_cards
            ]

        # conservo il proprietario finale
        # di ogni carta delle due mani originali
        self.player_card_final_owners = list(
            player_card_final_owners
        )

        self.opponent_card_final_owners = list(
            opponent_card_final_owners
        )

        # conservo regole, risultato e punteggi;
        # serviranno per le diverse Trade Rules
        self.match_rules = match_rules
        self.match_result = match_result
        self.player_score = player_score
        self.opponent_score = opponent_score

        # Trade Rule utilizzata nella partita
        self.trade_rule = self.match_rules[
            "trade"
        ]

        # numero di carte che devono essere trasferite
        # secondo la Trade Rule e il risultato
        if self.trade_rule == "One":
            self.trade_card_count = 1

        elif self.trade_rule == "Difference":
            self.trade_card_count = min(
                abs(
                    self.player_score
                    - self.opponent_score
                ),
                5
            )

        elif self.trade_rule == "All":
            self.trade_card_count = 5

        # Direct verrà gestita separatamente,
        # perché non utilizza una quantità di selezioni
        else:
            self.trade_card_count = 0

        # sfondo temporaneo uniforme
        self.background_color = (
            35,
            35,
            40
        )

        # font del titolo che ricorda
        # la Trade Rule e il numero di selezioni
        self.title_font = pygame.font.SysFont(
            "Arial",
            32
        )

        # dimensioni del pannello inferiore
        # che mostra il nome della carta indicata
        self.card_name_panel_width = 390
        self.card_name_panel_height = 64

        # colori uguali al pannello
        # utilizzato durante la partita
        self.card_name_panel_color = (
            70,
            70,
            70
        )

        self.card_name_panel_border_color = (
            255,
            255,
            255
        )

        # font del nome della carta
        self.card_name_panel_font = pygame.font.SysFont(
            "Arial",
            28
        )

        # dimensioni delle carte nella schermata
        self.trade_card_size = (
            150,
            190
        )

        # distanza orizzontale tra le carte
        self.card_spacing = 15

        # superfici rosse delle carte avversarie
        self.opponent_card_surfaces = []

        # versioni blu delle carte avversarie;
        # vengono mostrate dopo la selezione
        self.selected_opponent_card_surfaces = []

        # superfici blu delle carte del giocatore
        self.player_card_surfaces = []

        # versioni rosse mostrate quando
        # l'avversario prende le carte del giocatore
        self.lost_player_card_surfaces = []

        # preparo le cinque carte avversarie
        for card in self.opponent_cards:

            card_surface = render_card(
                card,
                "red"
            )

            card_surface = pygame.transform.smoothscale(
                card_surface,
                self.trade_card_size
            )

            self.opponent_card_surfaces.append(
                card_surface
            )

            # preparo anche la versione blu
            # della stessa carta
            selected_card_surface = render_card(
                card,
                "blue"
            )

            selected_card_surface = pygame.transform.smoothscale(
                selected_card_surface,
                self.trade_card_size
            )

            self.selected_opponent_card_surfaces.append(
                selected_card_surface
            )

        # preparo le cinque carte del giocatore
        for card in self.player_cards:

            card_surface = render_card(
                card,
                "blue"
            )

            card_surface = pygame.transform.smoothscale(
                card_surface,
                self.trade_card_size
            )

            self.player_card_surfaces.append(
                card_surface
            )

            # preparo anche la versione rossa
            # della stessa carta
            lost_card_surface = render_card(
                card,
                "red"
            )

            lost_card_surface = pygame.transform.smoothscale(
                lost_card_surface,
                self.trade_card_size
            )

            self.lost_player_card_surfaces.append(
                lost_card_surface
            )

        # carico il retro utilizzato
        # durante il centro del flip
        self.trade_card_back_surface = pygame.image.load(
            CARD_BACK_PATH
        ).convert_alpha()

        self.trade_card_back_surface = (
            pygame.transform.smoothscale(
                self.trade_card_back_surface,
                self.trade_card_size
            )
        )

        # rettangoli delle due righe;
        # serviranno successivamente per mouse e selezione
        self.opponent_card_rects = []
        self.player_card_rects = []

        # la manina parte dalla prima carta
        # a sinistra della riga avversaria
        self.focused_trade_card = 0

        # cursore animato utilizzato
        # per scegliere la carta da vincere
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # indice della carta coinvolta nel flip corrente;
        # None significa che nessuna carta sta flippando
        self.chosen_trade_card = None

        # indici delle carte selezionate dal giocatore,
        # conservati nello stesso ordine di selezione
        self.chosen_trade_cards = []

        # indice della carta attualmente mostrata
        # nell'animazione di acquisizione
        self.current_acquisition_card = None

        # posizione della prossima carta da mostrare
        # dentro chosen_trade_cards
        self.acquisition_queue_position = 0

        # indica se tutte le carte avversarie
        # devono essere selezionate automaticamente
        self.automatic_win_selection = (
            self.match_result == "win"
            and self.trade_card_count == 5
            and self.trade_rule in (
                "Difference",
                "All"
            )
        )

        # posizione della prossima carta
        # da flippare automaticamente
        self.automatic_win_selection_position = 0

        # breve attesa prima del primo flip
        self.automatic_win_selection_delay = 1000

        self.automatic_win_selection_start_time = (
            pygame.time.get_ticks()
        )

        # indici delle carte che hanno completato
        # l'animazione e non devono più apparire nella riga
        self.removed_opponent_card_indices = set()

        # fase corrente del flip della carta scelta
        self.trade_flip_phase = None

        # momento iniziale della fase corrente
        self.trade_flip_start_time = 0

        # durata di ogni quarto del flip
        self.trade_flip_phase_duration = 120

        # fase dell'animazione della carta vinta:
        # leaving_top, entering_center,
        # waiting_at_center oppure leaving_bottom
        self.acquisition_phase = None

        # momento iniziale della fase corrente
        self.acquisition_phase_start_time = 0

        # durata di ogni movimento delle carte
        # vinte o perse durante la presentazione
        self.acquisition_move_duration = 350

        # dimensioni della carta ingrandita
        self.acquisition_card_size = (
            280,
            354
        )

        # posizione corrente del centro della carta
        self.acquisition_card_center = None

        # posizione originale nella prima riga
        self.acquisition_origin_center = None

        # carta del giocatore coinvolta
        # nel flip automatico corrente
        self.chosen_lost_card = None

        # carte scelte automaticamente dall'avversario,
        # ordinate secondo la sequenza di presentazione
        self.chosen_lost_cards = []

        # carte che hanno completato il flip
        # automatico dal blu al rosso
        self.flipped_lost_card_indices = set()

        # posizione della prossima carta persa
        # da mostrare nella sequenza
        self.loss_queue_position = 0

        # attesa prima della scelta automatica
        self.loss_selection_delay = 1000

        # momento iniziale dell'attesa
        self.loss_selection_start_time = (
            pygame.time.get_ticks()
        )

        # fase del flip blu verso rosso
        self.loss_flip_phase = None

        # momento iniziale della fase del flip
        self.loss_flip_start_time = 0

        # fase del movimento della carta persa:
        # leaving_bottom, entering_center,
        # waiting_at_center oppure leaving_top
        self.loss_movement_phase = None

        # momento iniziale della fase corrente
        self.loss_movement_start_time = 0

        # posizione corrente della carta persa
        self.loss_card_center = None

        # posizione originale nella seconda riga
        self.loss_origin_center = None

        # slot che devono rimanere vuoti
        # dopo la perdita della carta
        self.removed_player_card_indices = set()

        # carte originariamente avversarie
        # diventate blu durante la partita
        self.direct_gained_card_indices = [
            card_index
            for card_index, final_owner in enumerate(
                self.opponent_card_final_owners
            )
            if final_owner == "player"
        ]

        # carte originariamente del giocatore
        # diventate rosse durante la partita
        self.direct_lost_card_indices = [
            card_index
            for card_index, final_owner in enumerate(
                self.player_card_final_owners
            )
            if final_owner == "opponent"
        ]

        # indica se la sequenza di Direct
        # è già stata avviata
        self.direct_trade_started = False

        # breve attesa prima del primo movimento
        self.direct_trade_delay = 1000

        self.direct_trade_start_time = (
            pygame.time.get_ticks()
        )

    # salva la collezione aggiornata
    # e apre il pannello Play Again
    def finish_trade(self):

        save_card_collection(
            self.state.card_collection
        )

        self.state.open_panel(
            PlayAgainPanel(
                self.width,
                self.height,
                self.state,
                self.player_cards,
                self.match_rules
            )
        )

    # avvia le animazioni della Trade Rule Direct
    # senza eseguire nuovi flip
    def start_direct_trade(self):

        if self.direct_trade_started:
            return

        self.direct_trade_started = True

        # mostro prima tutte le carte
        # vinte dal giocatore
        if self.direct_gained_card_indices:

            self.chosen_trade_cards = list(
                self.direct_gained_card_indices
            )

            self.acquisition_queue_position = 0
            self.start_next_acquisition_card()
            return

        # se non sono state vinte carte,
        # passo direttamente a quelle perse
        if self.direct_lost_card_indices:

            self.chosen_lost_cards = list(
                self.direct_lost_card_indices
            )

            self.loss_queue_position = 0
            self.start_next_loss_movement()
            return

        self.finish_trade()

    # avvia il flip automatico della prossima
    # carta quando devono essere trasferite tutte
    def start_next_automatic_win_flip(self):

        # tutte le cinque carte sono già state scelte
        if (
            self.automatic_win_selection_position
            >= len(self.opponent_cards)
        ):
            return

        card_index = (
            self.automatic_win_selection_position
        )

        self.chosen_trade_card = card_index

        self.chosen_trade_cards.append(
            card_index
        )

        # avvio il flip dal fronte rosso
        # verso il nuovo fronte blu
        self.trade_flip_phase = "red_shrinking"

        self.trade_flip_start_time = (
            pygame.time.get_ticks()
        )

    # seleziona oppure deseleziona
    # la carta indicata dalla manina
    def select_trade_card(self):

        # durante un flip non posso agire
        # contemporaneamente su un'altra carta
        if self.chosen_trade_card is not None:
            return

        # conservo la carta sulla quale
        # il giocatore sta agendo
        self.chosen_trade_card = (
            self.focused_trade_card
        )

        # se era già selezionata,
        # avvio il flip inverso verso il rosso
        if (
            self.focused_trade_card
            in self.chosen_trade_cards
        ):
            self.trade_flip_phase = "blue_shrinking"

            self.trade_flip_start_time = (
                pygame.time.get_ticks()
            )

            return

        # impedisco nuove selezioni quando
        # è già stato raggiunto il limite
        if (
            len(self.chosen_trade_cards)
            >= self.trade_card_count
        ):
            self.chosen_trade_card = None
            return

        # aggiungo la nuova carta mantenendo
        # l'ordine della selezione
        self.chosen_trade_cards.append(
            self.focused_trade_card
        )

        # avvio il flip dal rosso al blu
        self.trade_flip_phase = "red_shrinking"

        self.trade_flip_start_time = (
            pygame.time.get_ticks()
        )

    # conferma definitivamente tutte
    # le carte selezionate dal giocatore
    def confirm_trade_card(self):

        if not self.chosen_trade_cards:
            return

        # la presentazione deve rispettare
        # l'ordine usato durante la selezione
        self.acquisition_queue_position = 0

        self.start_next_acquisition_card()

    # avvia l'animazione della prossima
    # carta presente nella coda di acquisizione
    def start_next_acquisition_card(self):

        # se la coda è terminata,
        # non rimangono altre carte da mostrare
        if (
            self.acquisition_queue_position
            >= len(self.chosen_trade_cards)
        ):
            return

        # recupero l'indice della prossima carta
        self.current_acquisition_card = (
            self.chosen_trade_cards[
                self.acquisition_queue_position
            ]
        )

        # mantengo aggiornato anche il riferimento
        # utilizzato dal disegno e dal pannello del nome
        self.chosen_trade_card = (
            self.current_acquisition_card
        )

        selected_card = self.opponent_cards[
            self.current_acquisition_card
        ]

        # aggiungo una copia alla collezione;
        # quantità infinite e limite x99
        # sono gestiti da CardCollection
        self.state.card_collection.add_card(
            selected_card,
            1
        )

        # recupero la posizione originale
        # della carta nella riga avversaria
        self.acquisition_origin_center = (
            self.opponent_card_rects[
                self.current_acquisition_card
            ].center
        )

        self.acquisition_card_center = (
            self.acquisition_origin_center
        )

        # la carta comincia uscendo
        # dal bordo superiore
        self.acquisition_phase = "leaving_top"

        self.acquisition_phase_start_time = (
            pygame.time.get_ticks()
        )

    def cancel_trade_card(self):

        if self.chosen_trade_card is None:
            return

        # con No avvio il flip inverso
        # partendo dal fronte blu
        self.trade_flip_phase = "blue_shrinking"

        self.trade_flip_start_time = (
            pygame.time.get_ticks()
        )

    # gestisce input, conferme e navigazione
    # delle diverse Trade Rules
    def handle_events(self, event):

        if self.loss_movement_phase is not None:

            if self.loss_movement_phase == "waiting_at_center":

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                ):
                    self.continue_loss_animation()

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.continue_loss_animation()

            return

        # quando la carta è ferma al centro,
        # Invio oppure click sinistro la fanno proseguire
        if self.acquisition_phase is not None:

            if self.acquisition_phase == "waiting_at_center":

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                ):
                    self.continue_acquisition_animation()

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.continue_acquisition_animation()

            # durante tutte le fasi blocco
            # la normale selezione delle carte
            return

        # durante il flip non accetto
        # altri comandi dalla schermata
        if self.trade_flip_phase is not None:
            return

        # la selezione manuale è disponibile
        # quando il giocatore vince con One
        # oppure con Difference sotto le cinque carte
        player_selects_card = (
            self.match_result == "win"
            and self.trade_rule in (
                "One",
                "Difference"
            )
            and self.trade_card_count < 5
        )

        if not player_selects_card:
            return

        # controllo la tastiera
        if event.type == pygame.KEYDOWN:

            # sposto la manina a sinistra,
            # fermandomi sulla prima carta
            if event.key == pygame.K_LEFT:
                self.focused_trade_card = max(
                    0,
                    self.focused_trade_card - 1
                )

            # sposto la manina a destra,
            # fermandomi sull'ultima carta
            elif event.key == pygame.K_RIGHT:
                self.focused_trade_card = min(
                    len(self.opponent_cards) - 1,
                    self.focused_trade_card + 1
                )

            # Invio seleziona la carta indicata
            elif event.key == pygame.K_RETURN:
                self.select_trade_card()

        # il mouseover sposta immediatamente
        # la manina sulla carta indicata
        if event.type == pygame.MOUSEMOTION:

            for i, card_rect in enumerate(
                self.opponent_card_rects
            ):

                if card_rect.collidepoint(event.pos):
                    self.focused_trade_card = i
                    break

        # il click sinistro seleziona
        # la carta avversaria cliccata
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            for i, card_rect in enumerate(
                self.opponent_card_rects
            ):

                if card_rect.collidepoint(event.pos):
                    self.focused_trade_card = i
                    self.select_trade_card()
                    break

    # continua l'animazione dopo che la carta
    # si è fermata al centro dello schermo
    def continue_acquisition_animation(self):

        if self.acquisition_phase != "waiting_at_center":
            return

        # nascondo il pannello del nome
        # e faccio uscire la carta dal basso
        self.acquisition_phase = "leaving_bottom"

        self.acquisition_phase_start_time = (
            pygame.time.get_ticks()
        )

    # aggiorna il movimento della carta vinta
    def update_acquisition_animation(self):

        current_time = pygame.time.get_ticks()

        # al centro la carta rimane ferma
        # finché il giocatore non conferma
        if self.acquisition_phase == "waiting_at_center":
            return

        elapsed_time = (
            current_time
            - self.acquisition_phase_start_time
        )

        progress = (
            elapsed_time
            / self.acquisition_move_duration
        )

        progress = max(
            0.0,
            min(1.0, progress)
        )

        # la carta originale sale fino
        # a uscire dal bordo superiore
        if self.acquisition_phase == "leaving_top":

            start_y = (
                self.acquisition_origin_center[1]
            )

            hidden_y = -(
                self.trade_card_size[1] // 2
            )

            current_y = int(
                start_y
                + (hidden_y - start_y)
                * progress
            )

            self.acquisition_card_center = (
                self.acquisition_origin_center[0],
                current_y
            )

            if progress >= 1.0:

                # mentre è invisibile la ingrandisco
                # e la centro orizzontalmente
                self.acquisition_phase = "entering_center"

                self.acquisition_card_center = (
                    self.width // 2,
                    -self.acquisition_card_size[1] // 2
                )

                self.acquisition_phase_start_time = (
                    current_time
                )

        # la carta ingrandita entra dall'alto
        # e raggiunge il centro dello schermo
        elif self.acquisition_phase == "entering_center":

            start_y = -(
                self.acquisition_card_size[1] // 2
            )

            target_y = self.height // 2

            current_y = int(
                start_y
                + (target_y - start_y)
                * progress
            )

            self.acquisition_card_center = (
                self.width // 2,
                current_y
            )

            if progress >= 1.0:
                self.acquisition_phase = (
                    "waiting_at_center"
                )

                self.acquisition_card_center = (
                    self.width // 2,
                    self.height // 2
                )

        # dopo la conferma la carta
        # scende oltre il bordo inferiore
        elif self.acquisition_phase == "leaving_bottom":

            start_y = self.height // 2

            # faccio scendere la carta oltre il punto
            # strettamente necessario per nasconderla;
            # così Play Again non appare troppo presto
            hidden_y = (
                self.height
                + self.acquisition_card_size[1] // 2
                + 400
            )

            current_y = int(
                start_y
                + (hidden_y - start_y)
                * progress
            )

            self.acquisition_card_center = (
                self.width // 2,
                current_y
            )

            if progress >= 1.0:

                # la carta corrente ha lasciato
                # definitivamente la riga avversaria
                self.removed_opponent_card_indices.add(
                    self.current_acquisition_card
                )

                self.acquisition_phase = None
                self.acquisition_card_center = None

                # passo alla posizione successiva
                # nella coda delle carte selezionate
                self.acquisition_queue_position += 1

                # se rimangono altre carte,
                # avvio immediatamente la successiva
                if (
                    self.acquisition_queue_position
                    < len(self.chosen_trade_cards)
                ):
                    self.start_next_acquisition_card()
                    return

                # l'intera sequenza delle carte vinte
                # è terminata
                self.current_acquisition_card = None
                self.chosen_trade_card = None

                # con Direct, dopo le carte vinte
                # mostro tutte le eventuali carte perse
                if (
                    self.trade_rule == "Direct"
                    and self.direct_lost_card_indices
                ):
                    self.chosen_lost_cards = list(
                        self.direct_lost_card_indices
                    )

                    self.loss_queue_position = 0
                    self.start_next_loss_movement()
                    return

                self.finish_trade()

    # sceglie le carte che il giocatore perderà,
    # dando priorità assoluta alle rarità maggiori
    def prepare_lost_card_selection(self):

        card_indices = list(
            range(len(self.player_cards))
        )

        # mescolo prima dell'ordinamento:
        # a parità di rarità la scelta resta casuale
        random.shuffle(
            card_indices
        )

        # l'ordinamento stabile conserva l'ordine casuale
        # tra carte aventi la stessa rarità
        card_indices.sort(
            key=lambda card_index: (
                self.player_cards[
                    card_index
                ].rarity
            ),
            reverse=True
        )

        # conservo soltanto il numero di carte
        # richiesto dalla Trade Rule
        self.chosen_lost_cards = card_indices[
            :self.trade_card_count
        ]

        # la sequenza partirà dalla prima carta
        # con priorità maggiore
        self.loss_queue_position = 0

    # aggiorna la scelta automatica dell'avversario
    # e il flip blu verso rosso
    # aggiorna la selezione automatica dell'avversario
    # e i flip consecutivi dal blu al rosso
    def update_loss_selection(self):

        current_time = pygame.time.get_ticks()

        # preparo la selezione soltanto una volta,
        # dopo il ritardo iniziale
        if not self.chosen_lost_cards:

            elapsed_time = (
                current_time
                - self.loss_selection_start_time
            )

            if elapsed_time < self.loss_selection_delay:
                return

            self.prepare_lost_card_selection()

            if not self.chosen_lost_cards:
                return

            # comincio dalla prima carta scelta
            self.loss_queue_position = 0

            self.chosen_lost_card = (
                self.chosen_lost_cards[
                    self.loss_queue_position
                ]
            )

            self.loss_flip_phase = "blue_shrinking"
            self.loss_flip_start_time = current_time
            return

        # se tutti i flip sono terminati,
        # questo metodo non deve avanzare ulteriormente
        if self.loss_flip_phase is None:
            return

        elapsed_time = (
            current_time
            - self.loss_flip_start_time
        )

        if elapsed_time < self.trade_flip_phase_duration:
            return

        if self.loss_flip_phase == "blue_shrinking":
            self.loss_flip_phase = (
                "loss_back_expanding"
            )

        elif (
            self.loss_flip_phase
            == "loss_back_expanding"
        ):
            self.loss_flip_phase = (
                "loss_back_shrinking"
            )

        elif (
            self.loss_flip_phase
            == "loss_back_shrinking"
        ):
            self.loss_flip_phase = "red_expanding"

        elif self.loss_flip_phase == "red_expanding":

            # la carta corrente rimane definitivamente rossa
            self.flipped_lost_card_indices.add(
                self.chosen_lost_card
            )

            self.loss_flip_phase = None
            self.loss_queue_position += 1

            # se rimangono carte da flippare,
            # avvio immediatamente la successiva
            if (
                self.loss_queue_position
                < len(self.chosen_lost_cards)
            ):
                self.chosen_lost_card = (
                    self.chosen_lost_cards[
                        self.loss_queue_position
                    ]
                )

                self.loss_flip_phase = (
                    "blue_shrinking"
                )

                self.loss_flip_start_time = current_time
                return

            # tutti i flip sono terminati;
            # preparo la presentazione della prima carta
            self.loss_queue_position = 0
            self.start_next_loss_movement()
            return

        # ogni nuova fase parte dal momento corrente
        self.loss_flip_start_time = current_time

    # avvia la presentazione della prossima
    # carta scelta automaticamente dall'avversario
    def start_next_loss_movement(self):

        if (
            self.loss_queue_position
            >= len(self.chosen_lost_cards)
        ):
            return

        self.chosen_lost_card = (
            self.chosen_lost_cards[
                self.loss_queue_position
            ]
        )

        # recupero la posizione originale
        # della carta nella seconda riga
        self.loss_origin_center = (
            self.player_card_rects[
                self.chosen_lost_card
            ].center
        )

        self.loss_card_center = (
            self.loss_origin_center
        )

        # rimuovo una copia dalla collezione;
        # le carte infinite rimangono invariate
        lost_card = self.player_cards[
            self.chosen_lost_card
        ]

        self.state.card_collection.remove_card(
            lost_card,
            1
        )

        # la carta persa comincia uscendo
        # dal bordo inferiore
        self.loss_movement_phase = (
            "leaving_bottom"
        )

        self.loss_movement_start_time = (
            pygame.time.get_ticks()
        )

    def update_loss_movement(self):

        current_time = pygame.time.get_ticks()

        if self.loss_movement_phase == "waiting_at_center":
            return

        elapsed_time = (
            current_time
            - self.loss_movement_start_time
        )

        progress = (
            elapsed_time
            / self.acquisition_move_duration
        )

        progress = max(
            0.0,
            min(1.0, progress)
        )

        if self.loss_movement_phase == "leaving_bottom":

            start_y = self.loss_origin_center[1]

            hidden_y = (
                self.height
                + self.trade_card_size[1] // 2
            )

            current_y = int(
                start_y
                + (hidden_y - start_y)
                * progress
            )

            self.loss_card_center = (
                self.loss_origin_center[0],
                current_y
            )

            if progress >= 1.0:

                self.loss_movement_phase = "entering_center"

                self.loss_card_center = (
                    self.width // 2,
                    (
                        self.height
                        + self.acquisition_card_size[1] // 2
                    )
                )

                self.loss_movement_start_time = current_time

        elif self.loss_movement_phase == "entering_center":

            start_y = (
                self.height
                + self.acquisition_card_size[1] // 2
            )

            target_y = self.height // 2

            current_y = int(
                start_y
                + (target_y - start_y)
                * progress
            )

            self.loss_card_center = (
                self.width // 2,
                current_y
            )

            if progress >= 1.0:

                self.loss_movement_phase = (
                    "waiting_at_center"
                )

                self.loss_card_center = (
                    self.width // 2,
                    self.height // 2
                )

        elif self.loss_movement_phase == "leaving_top":

            start_y = self.height // 2

            hidden_y = -(
                self.acquisition_card_size[1] // 2
                + 400
            )

            current_y = int(
                start_y
                + (hidden_y - start_y)
                * progress
            )

            self.loss_card_center = (
                self.width // 2,
                current_y
            )

            if progress >= 1.0:

                # la carta corrente ha lasciato
                # definitivamente la riga del giocatore
                self.removed_player_card_indices.add(
                    self.chosen_lost_card
                )

                self.loss_movement_phase = None
                self.loss_card_center = None

                # passo alla carta successiva
                # nella coda delle perdite
                self.loss_queue_position += 1

                # se rimangono altre carte,
                # ne avvio immediatamente la presentazione
                if (
                    self.loss_queue_position
                    < len(self.chosen_lost_cards)
                ):
                    self.start_next_loss_movement()
                    return

                # l'intera sequenza è terminata
                self.chosen_lost_card = None

                self.finish_trade()

    def continue_loss_animation(self):

        if self.loss_movement_phase != "waiting_at_center":
            return

        self.loss_movement_phase = "leaving_top"

        self.loss_movement_start_time = (
            pygame.time.get_ticks()
        )

    def update(self):

        # con una sconfitta, l'avversario sceglie
        # automaticamente con One, Difference e All
        if (
            self.match_result == "loss"
            and self.trade_rule in (
                "One",
                "Difference",
                "All"
            )
        ):

            if self.loss_movement_phase is not None:
                self.update_loss_movement()
            else:
                self.update_loss_selection()

            return

        # Direct non utilizza flip o selezioni;
        # aggiorno direttamente le sue animazioni
        if self.trade_rule == "Direct":

            # se è in corso la presentazione
            # di una carta persa, la aggiorno
            if self.loss_movement_phase is not None:
                self.update_loss_movement()
                return

            # prima dell'avvio rispetto
            # la breve attesa iniziale
            if not self.direct_trade_started:

                elapsed_time = (
                    pygame.time.get_ticks()
                    - self.direct_trade_start_time
                )

                if elapsed_time >= self.direct_trade_delay:
                    self.start_direct_trade()

                return

        # quando il giocatore vince tutte le carte,
        # avvio automaticamente il primo flip
        if (
            self.automatic_win_selection
            and not self.chosen_trade_cards
            and self.trade_flip_phase is None
            and self.acquisition_phase is None
        ):

            elapsed_time = (
                pygame.time.get_ticks()
                - self.automatic_win_selection_start_time
            )

            if (
                elapsed_time
                >= self.automatic_win_selection_delay
            ):
                self.start_next_automatic_win_flip()

            return

        # l'animazione della carta vinta
        # ha la precedenza sul normale flip
        if self.acquisition_phase is not None:
            self.update_acquisition_animation()
            return

        if self.trade_flip_phase is None:
            return

        current_time = pygame.time.get_ticks()

        elapsed_time = (
            current_time
            - self.trade_flip_start_time
        )

        if elapsed_time < self.trade_flip_phase_duration:
            return

        # flip dal fronte rosso al retro
        if self.trade_flip_phase == "red_shrinking":
            self.trade_flip_phase = "back_expanding"

        elif self.trade_flip_phase == "back_expanding":
            self.trade_flip_phase = "back_shrinking"

        # dal retro passo al fronte blu
        elif self.trade_flip_phase == "back_shrinking":
            self.trade_flip_phase = "blue_expanding"

        elif self.trade_flip_phase == "blue_expanding":

            # il flip è terminato;
            # la carta rimane blu
            self.trade_flip_phase = None

            # con All oppure Difference da cinque carte
            # continuo automaticamente senza conferma
            if self.automatic_win_selection:

                self.automatic_win_selection_position += 1

                # avvio il flip della carta successiva
                if (
                    self.automatic_win_selection_position
                    < len(self.opponent_cards)
                ):
                    self.chosen_trade_card = None
                    self.start_next_automatic_win_flip()
                    return

                # dopo il quinto flip avvio direttamente
                # la presentazione delle cinque carte
                self.confirm_trade_card()
                return

            # nella selezione manuale apro la conferma
            # quando raggiungo il numero richiesto
            if (
                len(self.chosen_trade_cards)
                >= self.trade_card_count
            ):
                self.state.open_panel(
                    TradeCardConfirmationPanel(
                        self.width,
                        self.height,
                        self.state,
                        self
                    )
                )

            # altrimenti permetto al giocatore
            # di scegliere la carta successiva
            else:
                self.chosen_trade_card = None

            return

        # flip inverso dal blu al retro
        elif self.trade_flip_phase == "blue_shrinking":
            self.trade_flip_phase = (
                "reverse_back_expanding"
            )

        elif (
            self.trade_flip_phase
            == "reverse_back_expanding"
        ):
            self.trade_flip_phase = (
                "reverse_back_shrinking"
            )

        # dal retro torno al fronte rosso
        elif (
            self.trade_flip_phase
            == "reverse_back_shrinking"
        ):
            self.trade_flip_phase = "red_expanding"

        elif self.trade_flip_phase == "red_expanding":

            # rimuovo dalla selezione la carta
            # che ha appena completato il flip inverso
            if (
                self.chosen_trade_card
                in self.chosen_trade_cards
            ):
                self.chosen_trade_cards.remove(
                    self.chosen_trade_card
                )

            self.trade_flip_phase = None
            self.chosen_trade_card = None
            return

        # ogni nuova fase parte
        # dal momento corrente
        self.trade_flip_start_time = current_time

    # disegna nella parte inferiore dello schermo
    # il pannello con nome e quantità della carta indicata
    def draw_card_name_panel(
        self,
        screen,
        card
    ):

        panel_rect = pygame.Rect(
            0,
            0,
            self.card_name_panel_width,
            self.card_name_panel_height
        )

        panel_rect.center = (
            self.width // 2,
            self.height - 40
        )

        # disegno sfondo e bordo
        pygame.draw.rect(
            screen,
            self.card_name_panel_color,
            panel_rect
        )

        pygame.draw.rect(
            screen,
            self.card_name_panel_border_color,
            panel_rect,
            2
        )

        # recupero la quantità attualmente posseduta
        card_quantity = (
            self.state.card_collection.get_quantity(
                card
            )
        )

        # le carte di rarità 1 mostrano
        # soltanto il simbolo dell'infinito
        if card.rarity == 1:
            quantity_text = "∞"

        # le altre carte mostrano la quantità posseduta
        else:
            quantity_text = f"x{card_quantity}"

        # una carta con quantità x0 appare in blu
        if (
            card.rarity > 1
            and card_quantity == 0
        ):
            text_color = (
                70,
                160,
                255
            )

        # le carte già possedute appaiono in bianco
        else:
            text_color = (
                255,
                255,
                255
            )

        # preparo nome e quantità
        card_information_text = (
            f"{card.name}   {quantity_text}"
        )

        card_name_surface = (
            self.card_name_panel_font.render(
                card_information_text,
                True,
                text_color
            )
        )

        card_name_rect = card_name_surface.get_rect(
            center=panel_rect.center
        )

        screen.blit(
            card_name_surface,
            card_name_rect
        )

    # disegna le due mani
    def draw(self, screen):

        # riempio la finestra con lo sfondo temporaneo
        screen.fill(
            self.background_color
        )

        # preparo il titolo della Trade Rule corrente
        if self.trade_rule == "One":
            title_text = (
                "Trade Rule: One - Select 1 Card"
            )

        elif self.trade_rule == "Difference":

            title_text = (
                "Trade Rule: Difference - "
                f"Select {self.trade_card_count} Cards"
            )

        elif self.trade_rule == "All":
            title_text = (
                "Trade Rule: All - All Cards"
            )

        else:
            title_text = (
                f"Trade Rule: {self.trade_rule}"
            )

        title_surface = self.title_font.render(
            title_text,
            True,
            (255, 255, 255)
        )

        title_rect = title_surface.get_rect(
            center=(
                self.width // 2,
                45
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )

        # calcolo la larghezza completa di una riga
        row_width = (
            len(self.opponent_card_surfaces)
            * self.trade_card_size[0]
            + (
                len(self.opponent_card_surfaces) - 1
            ) * self.card_spacing
        )

        # centro orizzontalmente le due righe
        row_start_x = (
            self.width - row_width
        ) // 2

        # posizione verticale delle due righe
        opponent_row_y = 110
        player_row_y = 420

        # ricreo i rettangoli delle carte
        self.opponent_card_rects = []
        self.player_card_rects = []

        # disegno la riga rossa dell'avversario
        for i, red_card_surface in enumerate(
            self.opponent_card_surfaces
        ):

            # rettangolo fisso della carta;
            # non cambia durante lo shrink
            card_rect = pygame.Rect(
                (
                    row_start_x
                    + i
                    * (
                        self.trade_card_size[0]
                        + self.card_spacing
                    )
                ),
                opponent_row_y,
                self.trade_card_size[0],
                self.trade_card_size[1]
            )

            self.opponent_card_rects.append(
                card_rect
            )

            # dopo il completamento dello scambio
            # lascio vuota la posizione della carta vinta
            if i in self.removed_opponent_card_indices:
                continue

            # durante l'animazione di acquisizione
            # la carta viene disegnata separatamente
            if (
                i == self.chosen_trade_card
                and self.acquisition_phase is not None
            ):
                continue

            # normalmente mostro il fronte rosso
            surface_to_draw = red_card_surface
            animated_width = self.trade_card_size[0]

            # con Direct mostro immediatamente
            # il colore ottenuto alla fine della partita
            if (
                self.trade_rule == "Direct"
                and self.opponent_card_final_owners[i]
                == "player"
            ):
                surface_to_draw = (
                    self.selected_opponent_card_surfaces[i]
                )

            # tutte le carte già selezionate
            # devono rimanere con il fronte blu
            if i in self.chosen_trade_cards:
                surface_to_draw = (
                    self.selected_opponent_card_surfaces[i]
                )

            # soltanto la carta corrente
            # deve mostrare le fasi del flip
            if (
                i == self.chosen_trade_card
                and self.trade_flip_phase is not None
            ):

                blue_card_surface = (
                    self.selected_opponent_card_surfaces[i]
                )

                flip_progress = (
                    pygame.time.get_ticks()
                    - self.trade_flip_start_time
                ) / self.trade_flip_phase_duration

                flip_progress = max(
                    0.0,
                    min(1.0, flip_progress)
                )

                if self.trade_flip_phase == "red_shrinking":
                    surface_to_draw = red_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * (1.0 - flip_progress)
                    )

                elif self.trade_flip_phase in (
                    "back_expanding",
                    "reverse_back_expanding"
                ):
                    surface_to_draw = (
                        self.trade_card_back_surface
                    )

                    animated_width = int(
                        self.trade_card_size[0]
                        * flip_progress
                    )

                elif self.trade_flip_phase in (
                    "back_shrinking",
                    "reverse_back_shrinking"
                ):
                    surface_to_draw = (
                        self.trade_card_back_surface
                    )

                    animated_width = int(
                        self.trade_card_size[0]
                        * (1.0 - flip_progress)
                    )

                elif self.trade_flip_phase == "blue_expanding":
                    surface_to_draw = blue_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * flip_progress
                    )

                elif self.trade_flip_phase == "blue_shrinking":
                    surface_to_draw = blue_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * (1.0 - flip_progress)
                    )

                elif self.trade_flip_phase == "red_expanding":
                    surface_to_draw = red_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * flip_progress
                    )

            # evito una superficie larga zero pixel
            animated_width = max(
                1,
                animated_width
            )

            surface_to_draw = pygame.transform.smoothscale(
                surface_to_draw,
                (
                    animated_width,
                    self.trade_card_size[1]
                )
            )

            # mantengo la carta centrata
            # durante tutto il flip
            animated_card_rect = surface_to_draw.get_rect(
                center=card_rect.center
            )

            screen.blit(
                surface_to_draw,
                animated_card_rect
            )

        # disegno la riga blu del giocatore
        for i, blue_card_surface in enumerate(
            self.player_card_surfaces
        ):

            card_rect = pygame.Rect(
                (
                    row_start_x
                    + i
                    * (
                        self.trade_card_size[0]
                        + self.card_spacing
                    )
                ),
                player_row_y,
                self.trade_card_size[0],
                self.trade_card_size[1]
            )

            self.player_card_rects.append(
                card_rect
            )

            if i in self.removed_player_card_indices:
                continue

            if (
                i == self.chosen_lost_card
                and self.loss_movement_phase is not None
            ):
                continue

            # normalmente la carta appartiene
            # ancora al giocatore ed è blu
            surface_to_draw = blue_card_surface
            animated_width = self.trade_card_size[0]

            # con Direct mostro immediatamente
            # il colore ottenuto alla fine della partita
            if (
                self.trade_rule == "Direct"
                and self.player_card_final_owners[i]
                == "opponent"
            ):
                surface_to_draw = (
                    self.lost_player_card_surfaces[i]
                )

            # le carte che hanno completato il flip
            # devono rimanere permanentemente rosse
            if i in self.flipped_lost_card_indices:
                surface_to_draw = (
                    self.lost_player_card_surfaces[i]
                )

            # soltanto la carta corrente
            # mostra le singole fasi del flip
            if (
                i == self.chosen_lost_card
                and self.loss_flip_phase is not None
            ):

                red_card_surface = (
                    self.lost_player_card_surfaces[i]
                )

                flip_progress = (
                    pygame.time.get_ticks()
                    - self.loss_flip_start_time
                ) / self.trade_flip_phase_duration

                flip_progress = max(
                    0.0,
                    min(1.0, flip_progress)
                )

                if self.loss_flip_phase == "blue_shrinking":
                    surface_to_draw = blue_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * (1.0 - flip_progress)
                    )

                elif (
                    self.loss_flip_phase
                    == "loss_back_expanding"
                ):
                    surface_to_draw = (
                        self.trade_card_back_surface
                    )

                    animated_width = int(
                        self.trade_card_size[0]
                        * flip_progress
                    )

                elif (
                    self.loss_flip_phase
                    == "loss_back_shrinking"
                ):
                    surface_to_draw = (
                        self.trade_card_back_surface
                    )

                    animated_width = int(
                        self.trade_card_size[0]
                        * (1.0 - flip_progress)
                    )

                elif self.loss_flip_phase == "red_expanding":
                    surface_to_draw = red_card_surface

                    animated_width = int(
                        self.trade_card_size[0]
                        * flip_progress
                    )

            animated_width = max(
                1,
                animated_width
            )

            surface_to_draw = pygame.transform.smoothscale(
                surface_to_draw,
                (
                    animated_width,
                    self.trade_card_size[1]
                )
            )

            animated_card_rect = surface_to_draw.get_rect(
                center=card_rect.center
            )

            screen.blit(
                surface_to_draw,
                animated_card_rect
            )

        if (
            self.loss_movement_phase is not None
            and self.chosen_lost_card is not None
            and self.loss_card_center is not None
        ):

            loss_surface = (
                self.lost_player_card_surfaces[
                    self.chosen_lost_card
                ]
            )

            if self.loss_movement_phase == "leaving_bottom":
                current_loss_size = self.trade_card_size
            else:
                current_loss_size = self.acquisition_card_size

            loss_surface = pygame.transform.smoothscale(
                loss_surface,
                current_loss_size
            )

            loss_rect = loss_surface.get_rect(
                center=self.loss_card_center
            )

            screen.blit(
                loss_surface,
                loss_rect
            )

        # disegno separatamente la carta
        # durante l'animazione di acquisizione
        if (
            self.acquisition_phase is not None
            and self.chosen_trade_card is not None
            and self.acquisition_card_center is not None
        ):

            acquisition_surface = (
                self.selected_opponent_card_surfaces[
                    self.chosen_trade_card
                ]
            )

            # nella prima salita mantiene
            # le dimensioni della riga
            if self.acquisition_phase == "leaving_top":
                current_card_size = self.trade_card_size

            # dopo essere uscita viene mostrata ingrandita
            else:
                current_card_size = self.acquisition_card_size

            acquisition_surface = (
                pygame.transform.smoothscale(
                    acquisition_surface,
                    current_card_size
                )
            )

            acquisition_rect = acquisition_surface.get_rect(
                center=self.acquisition_card_center
            )

            screen.blit(
                acquisition_surface,
                acquisition_rect
            )

        # durante la selezione manuale,
        # la manina indica la carta avversaria
        if (
            self.match_result == "win"
            and self.trade_rule in (
                "One",
                "Difference"
            )
            and self.trade_card_count < 5
            and self.opponent_card_rects
            and self.chosen_trade_card is None
            and len(self.chosen_trade_cards)
            < self.trade_card_count
        ):

            focused_card_rect = (
                self.opponent_card_rects[
                    self.focused_trade_card
                ]
            )

            # la punta della manina indica
            # il centro esatto della carta
            self.hand_cursor.draw_at_point(
                screen,
                focused_card_rect.center
            )

        # durante la normale selezione mostro
        # il nome della carta indicata
        if (
            self.match_result == "win"
            and self.trade_rule in (
                "One",
                "Difference"
            )
            and self.trade_card_count < 5
            and self.opponent_cards
            and self.chosen_trade_card is None
            and len(self.chosen_trade_cards)
            < self.trade_card_count
        ):

            focused_card = self.opponent_cards[
                self.focused_trade_card
            ]

            self.draw_card_name_panel(
                screen,
                focused_card
            )

        # quando la carta vinta è ferma al centro,
        # mostro nuovamente il suo nome
        if (
            self.acquisition_phase
            == "waiting_at_center"
            and self.chosen_trade_card is not None
        ):

            acquired_card = self.opponent_cards[
                self.chosen_trade_card
            ]

            self.draw_card_name_panel(
                screen,
                acquired_card
            )

        if (
            self.loss_movement_phase
            == "waiting_at_center"
            and self.chosen_lost_card is not None
        ):

            lost_card = self.player_cards[
                self.chosen_lost_card
            ]

            self.draw_card_name_panel(
                screen,
                lost_card
            )