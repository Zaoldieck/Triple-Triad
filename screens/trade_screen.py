import pygame
import random

from screens.screen import Screen
from renderers.card_renderer import render_card
from ui.animated_hand_cursor import AnimatedHandCursor
from config import CARD_BACK_PATH
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
        opponent_score
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
        # l'avversario prende una carta
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

        # indice della carta scelta temporaneamente;
        # None significa che non è stata ancora scelta
        self.chosen_trade_card = None

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

        # durata di ogni movimento
        self.acquisition_move_duration = 600

        # dimensioni della carta ingrandita
        self.acquisition_card_size = (
            280,
            354
        )

        # posizione corrente del centro della carta
        self.acquisition_card_center = None

        # posizione originale nella prima riga
        self.acquisition_origin_center = None

        # carta del giocatore scelta dall'avversario
        self.chosen_lost_card = None

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

    # seleziona la carta indicata dalla manina
    # e apre il pannello di conferma
    def select_trade_card(self):

        # impedisco selezioni duplicate
        if self.chosen_trade_card is not None:
            return

        self.chosen_trade_card = (
            self.focused_trade_card
        )

        # inizio il flip restringendo
        # il fronte rosso della carta
        self.trade_flip_phase = "red_shrinking"

        self.trade_flip_start_time = (
            pygame.time.get_ticks()
        )

    # conferma definitivamente la carta scelta
    def confirm_trade_card(self):

        if self.chosen_trade_card is None:
            return

        selected_card = self.opponent_cards[
            self.chosen_trade_card
        ]

        # aggiungo una copia alla collezione;
        # le carte infinite e il limite x99
        # sono già gestiti da CardCollection
        self.state.card_collection.add_card(
            selected_card,
            1
        )

        # recupero la posizione originale
        # della carta nella riga avversaria
        self.acquisition_origin_center = (
            self.opponent_card_rects[
                self.chosen_trade_card
            ].center
        )

        self.acquisition_card_center = (
            self.acquisition_origin_center
        )

        # inizio facendo salire la carta
        # fino a farla uscire dallo schermo
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

    # gestisce la navigazione della Trade Rule One
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
        # soltanto quando il giocatore ha vinto con One
        player_selects_card = (
            self.match_result == "win"
            and self.trade_rule == "One"
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

                # la carta ha lasciato definitivamente
                # la riga dell'avversario
                self.removed_opponent_card_indices.add(
                    self.chosen_trade_card
                )

                self.acquisition_phase = None
                self.acquisition_card_center = None

                # soltanto adesso mostro Play Again
                self.state.open_panel(
                    PlayAgainPanel(
                        self.width,
                        self.height,
                        self.state,
                        self.player_cards,
                        self.match_rules
                    )
                )

    # aggiorna la scelta automatica dell'avversario
    # e il flip blu verso rosso
    def update_loss_selection(self):

        current_time = pygame.time.get_ticks()

        # dopo un secondo scelgo una carta
        # usando la rarità come peso
        if self.chosen_lost_card is None:

            elapsed_time = (
                current_time
                - self.loss_selection_start_time
            )

            if elapsed_time < self.loss_selection_delay:
                return

            card_indices = list(
                range(len(self.player_cards))
            )

            rarity_weights = [
                card.rarity
                for card in self.player_cards
            ]

            self.chosen_lost_card = random.choices(
                card_indices,
                weights=rarity_weights,
                k=1
            )[0]

            # avvio il flip dal fronte blu
            self.loss_flip_phase = "blue_shrinking"

            self.loss_flip_start_time = current_time
            return

        # terminato il flip, per ora
        # lascio la carta rossa nella seconda riga
        if self.loss_flip_phase is None:
            return

        elapsed_time = (
            current_time
            - self.loss_flip_start_time
        )

        if elapsed_time < self.trade_flip_phase_duration:
            return

        if self.loss_flip_phase == "blue_shrinking":
            self.loss_flip_phase = "loss_back_expanding"

        elif self.loss_flip_phase == "loss_back_expanding":
            self.loss_flip_phase = "loss_back_shrinking"

        elif self.loss_flip_phase == "loss_back_shrinking":
            self.loss_flip_phase = "red_expanding"

        elif self.loss_flip_phase == "red_expanding":

            self.loss_flip_phase = None

            # recupero la posizione originale
            # nella seconda riga
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

            # la carta persa comincia
            # uscendo dal bordo inferiore
            self.loss_movement_phase = "leaving_bottom"

            self.loss_movement_start_time = current_time
            return

        self.loss_flip_start_time = current_time

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

                self.removed_player_card_indices.add(
                    self.chosen_lost_card
                )

                self.loss_movement_phase = None
                self.loss_card_center = None

                self.state.open_panel(
                    PlayAgainPanel(
                        self.width,
                        self.height,
                        self.state,
                        self.player_cards,
                        self.match_rules
                    )
                )

    def continue_loss_animation(self):

        if self.loss_movement_phase != "waiting_at_center":
            return

        self.loss_movement_phase = "leaving_top"

        self.loss_movement_start_time = (
            pygame.time.get_ticks()
        )

    def update(self):

        # con una sconfitta e Trade Rule One,
        # l'avversario sceglie automaticamente
        if (
            self.match_result == "loss"
            and self.trade_rule == "One"
        ):

            if self.loss_movement_phase is not None:
                self.update_loss_movement()
            else:
                self.update_loss_selection()

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

            # soltanto ora apro la conferma
            self.state.open_panel(
                TradeCardConfirmationPanel(
                    self.width,
                    self.height,
                    self.state,
                    self
                )
            )

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

            # annullo completamente la selezione
            self.trade_flip_phase = None
            self.chosen_trade_card = None
            return

        # ogni nuova fase parte
        # dal momento corrente
        self.trade_flip_start_time = current_time

    # disegna nella parte inferiore dello schermo
    # il pannello con il nome della carta indicata
    def draw_card_name_panel(
        self,
        screen,
        card_name
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

        # preparo e centro il nome
        card_name_surface = (
            self.card_name_panel_font.render(
                card_name,
                True,
                (255, 255, 255)
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

            cards_to_select = abs(
                self.player_score
                - self.opponent_score
            )

            title_text = (
                "Trade Rule: Difference - "
                f"Select {cards_to_select} Cards"
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

            # gestisco soltanto la carta scelta
            if i == self.chosen_trade_card:

                blue_card_surface = (
                    self.selected_opponent_card_surfaces[i]
                )

                # se non è in corso un flip,
                # la selezione confermata rimane blu
                if self.trade_flip_phase is None:
                    surface_to_draw = blue_card_surface

                else:
                    flip_progress = (
                        pygame.time.get_ticks()
                        - self.trade_flip_start_time
                    ) / self.trade_flip_phase_duration

                    flip_progress = max(
                        0.0,
                        min(1.0, flip_progress)
                    )

                    # il fronte rosso si restringe
                    if self.trade_flip_phase == "red_shrinking":
                        surface_to_draw = red_card_surface
                        animated_width = int(
                            self.trade_card_size[0]
                            * (1.0 - flip_progress)
                        )

                    # il retro si allarga
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

                    # il retro si restringe
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

                    # il fronte blu si allarga
                    elif self.trade_flip_phase == "blue_expanding":
                        surface_to_draw = blue_card_surface

                        animated_width = int(
                            self.trade_card_size[0]
                            * flip_progress
                        )

                    # il fronte blu si restringe
                    elif self.trade_flip_phase == "blue_shrinking":
                        surface_to_draw = blue_card_surface

                        animated_width = int(
                            self.trade_card_size[0]
                            * (1.0 - flip_progress)
                        )

                    # il fronte rosso si riallarga
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

            surface_to_draw = blue_card_surface
            animated_width = self.trade_card_size[0]

            # gestisco il flip della carta
            # scelta automaticamente
            if i == self.chosen_lost_card:

                red_card_surface = (
                    self.lost_player_card_surfaces[i]
                )

                # dopo il flip la carta rimane rossa
                if self.loss_flip_phase is None:
                    surface_to_draw = red_card_surface

                else:
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

                    elif self.loss_flip_phase == "loss_back_expanding":
                        surface_to_draw = (
                            self.trade_card_back_surface
                        )

                        animated_width = int(
                            self.trade_card_size[0]
                            * flip_progress
                        )

                    elif self.loss_flip_phase == "loss_back_shrinking":
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

        # con Trade Rule One e una vittoria,
        # la manina indica la carta avversaria scelta
        if (
            self.match_result == "win"
            and self.trade_rule == "One"
            and self.opponent_card_rects
            and self.chosen_trade_card is None
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
            and self.trade_rule == "One"
            and self.opponent_cards
            and self.chosen_trade_card is None
        ):

            focused_card = self.opponent_cards[
                self.focused_trade_card
            ]

            self.draw_card_name_panel(
                screen,
                focused_card.name
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
                acquired_card.name
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
                lost_card.name
            )