import pygame
import random
import math

from screens.screen import Screen
from game.board import Board

from config import (
    ACTIVE_CARD_SETS,
    CARD_BACK_PATH,
    DEBUG_DRAW_MATCH_GRID
)
from panels.play_again_panel import PlayAgainPanel
# funzione che costruisce graficamente le carte
from renderers.card_renderer import render_card
from ui.animated_hand_cursor import AnimatedHandCursor
from game.card_loader import load_cards
# schermata mostrata dopo il risultato
# per applicare la Trade Rule
from screens.trade_screen import TradeScreen
from panels.leave_match_confirmation_panel import LeaveMatchConfirmationPanel

# schermata che gestisce una partita di Triple Triad
class MatchScreen(Screen):

    def __init__(
        self,
        width,
        height,
        state,
        player_cards,
        match_rules,
        opponent_cards=None,
        preserve_hands=False
    ):

        # dimensioni della finestra
        self.width = width
        self.height = height

        # stato globale del gioco
        self.state = state

        # carico tutte le carte appartenenti
        # ai set attivi della versione corrente
        available_opponent_cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # durante Sudden Death utilizzo esattamente
        # la mano ricevuta dal round precedente
        if preserve_hands:
            self.player_cards = list(
                player_cards
            )

        # con Hand Random genero cinque carte differenti
        # tra tutte quelle attualmente possedute
        elif match_rules["hand"] == "Random":

            owned_player_cards = []

            # filtro tutte le carte dei set attivi
            # controllando la quantità posseduta
            for card in available_opponent_cards:

                quantity = (
                    self.state.card_collection.get_quantity(
                        card
                    )
                )

                # None indica una quantità infinita;
                # accetto inoltre quantità comprese tra 1 e 99
                if (
                    quantity is None
                    or 1 <= quantity <= 99
                ):
                    owned_player_cards.append(
                        card
                    )

            # una partita richiede almeno cinque
            # carte differenti disponibili
            if len(owned_player_cards) < 5:
                raise ValueError(
                    "Not enough owned cards "
                    "to generate a random player hand"
                )

            # estraggo cinque carte differenti
            self.player_cards = random.sample(
                owned_player_cards,
                5
            )

        # con Hand Choice utilizzo invece
        # le carte selezionate manualmente
        else:
            self.player_cards = list(
                player_cards
            )

        # durante Sudden Death conservo esattamente
        # la mano avversaria ricevuta dal round precedente
        if opponent_cards is not None:
            self.opponent_cards = list(
                opponent_cards
            )

        # durante una nuova partita genero normalmente
        # cinque carte avversarie casuali di rarità 1
        else:

            rarity_one_cards = [
                card
                for card in available_opponent_cards
                if card.rarity == 1
            ]

            # verifico che esistano almeno
            # cinque carte utilizzabili
            if len(rarity_one_cards) < 5:
                raise ValueError(
                    "Not enough rarity 1 cards "
                    "to generate the opponent hand"
                )

            self.opponent_cards = random.sample(
                rarity_one_cards,
                5
            )

        # dimensioni delle carte mostrate durante la partita
        self.match_card_size = (
            150,
            190
        )

        # superfici grafiche delle carte del giocatore
        self.player_card_surfaces = []

        # costruisco una sola volta le cinque carte blu
        for card in self.player_cards:

            card_surface = render_card(
                card,
                "blue"
            )

            card_surface = pygame.transform.smoothscale(
                card_surface,
                self.match_card_size
            )

            self.player_card_surfaces.append(
                card_surface
            )

        # superfici grafiche delle carte dell'avversario
        self.opponent_card_surfaces = []

        # conservo questa informazione perché servirà
        # anche al pannello con il nome della carta
        self.opponent_cards_face_up = (
            match_rules["cards"] == "Face Up"
        )

        # se le carte sono coperte, carico il retro una sola volta
        if not self.opponent_cards_face_up:

            opponent_card_back = pygame.image.load(
                CARD_BACK_PATH
            ).convert_alpha()

            opponent_card_back = pygame.transform.smoothscale(
                opponent_card_back,
                self.match_card_size
            )

        # costruisco le cinque carte avversarie
        for card in self.opponent_cards:

            # con Face Up mostro il fronte rosso
            if self.opponent_cards_face_up:
                card_surface = render_card(
                    card,
                    "red"
                )

                card_surface = pygame.transform.smoothscale(
                    card_surface,
                    self.match_card_size
                )

            # con Face Down mostro soltanto il retro
            else:
                card_surface = opponent_card_back.copy()

            self.opponent_card_surfaces.append(
                card_surface
            )

        # rettangoli delle carte dell'avversario
        self.opponent_card_rects = []

        # indici degli slot avversari
        # le cui carte sono già state giocate
        self.played_opponent_card_indices = set()

        # indice della carta scelta durante il turno avversario
        self.selected_opponent_card = None

        # casella scelta dall'avversario
        self.opponent_target_row = None
        self.opponent_target_column = None

        # fase corrente dell'animazione avversaria;
        # None significa che non è in corso il suo turno
        self.opponent_turn_phase = None

        # momento nel quale è iniziata la fase corrente
        self.opponent_phase_start_time = 0

        # durata di ogni fase dell'avversario
        self.opponent_phase_duration = 1000

        # rettangoli delle carte del giocatore;
        # serviranno successivamente per mouse e selezione
        self.player_card_rects = []

        # rettangoli fissi usati solamente per il mouse;
        # non si spostano insieme alla carta selezionata
        self.player_card_hover_rects = []

        # indici degli slot le cui carte
        # sono già state giocate sul tabellone
        self.played_player_card_indices = set()

        # indice della carta attualmente indicata
        # nella mano del giocatore
        self.selected_player_card = 0

        # dimensioni del pannello che mostra
        # il nome della carta indicata
        self.card_name_panel_width = 390
        self.card_name_panel_height = 64

        # colori coerenti con gli altri pannelli
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

        # font usato per il nome della carta
        self.card_name_panel_font = pygame.font.SysFont(
            "Arial",
            28
        )

        # manina animata usata durante la partita
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # dimensioni complete della freccia
        # che seleziona chi inizia la partita
        self.turn_arrow_size = (
            90,
            70
        )

        # colori della sfumatura verticale:
        # rosso chiaro sopra e rosso medio sotto
        self.turn_arrow_top_color = (
            255,
            155,
            155
        )

        self.turn_arrow_bottom_color = (
            195,
            75,
            75
        )

        self.turn_arrow_surfaces = {
            "left": self.create_turn_arrow_surface(
                "left"
            ),
            "right": self.create_turn_arrow_surface(
                "right"
            ),
            "down": self.create_turn_arrow_surface(
                "down"
            )
        }

        # dimensioni dell'indicatore permanente
        # mostrato sopra la mano del giocatore attivo
        self.active_turn_indicator_size = (
            54,
            42
        )

        # proprietario del turno indicato dal triangolo;
        # viene assegnato al termine dell'animazione iniziale
        self.active_turn_owner = None

        # velocità della pulsazione orizzontale continua
        self.active_turn_indicator_speed = 5.0

        # fase del trasferimento dell'indicatore:
        # None, leaving, waiting oppure entering
        self.turn_indicator_transition_phase = None

        # giocatore che riceverà il turno
        # al termine del trasferimento
        self.pending_turn_owner = None

        # momento iniziale della fase corrente
        self.turn_indicator_transition_start_time = 0

        # durata della salita fuori dallo schermo
        self.turn_indicator_leave_duration = 300

        # durata della pausa fuori dallo schermo
        self.turn_indicator_wait_duration = 200

        # durata della discesa sul lato opposto
        self.turn_indicator_enter_duration = 300

        # posizione verticale normale dell'indicatore
        self.turn_indicator_rest_y = 32

        # posizione verticale completamente fuori dallo schermo
        self.turn_indicator_hidden_y = (
            -self.active_turn_indicator_size[1]
        )

        # scelgo casualmente chi inizierà la partita;
        # la scelta rimane nascosta durante l'animazione
        self.starting_turn_owner = random.choice(
            [
                "player",
                "opponent"
            ]
        )

        # inizialmente la freccia è rivolta a sinistra
        self.turn_arrow_direction = "left"

        # il flip comincia restringendo la freccia
        self.turn_arrow_phase = "shrinking"

        # momento iniziale della fase corrente
        self.turn_arrow_phase_start_time = (
            pygame.time.get_ticks()
        )

        # numero di rotazioni complete già eseguite
        self.turn_arrow_completed_flips = 0

        # numero minimo di rotazioni prima
        # di potersi fermare sul risultato
        self.turn_arrow_minimum_flips = 14

        # durata iniziale di metà rotazione;
        # aumenterà gradualmente per simulare il rallentamento
        self.turn_arrow_phase_duration = 45

        # momento nel quale la freccia
        # si sarà fermata sul risultato
        self.turn_arrow_finished_time = None

        # durata della pausa finale prima
        # di iniziare il turno scelto
        self.turn_arrow_result_pause = 500

        # prima della partita mostro l'animazione
        # che sceglie casualmente chi comincia
        self.input_mode = "starting_turn_animation"

        # casella inizialmente indicata nel tabellone
        self.selected_board_row = 0
        self.selected_board_column = 0

        # coordinate e dimensioni del tabellone
        self.board_x = 400
        self.board_y = 57
        self.board_cell_width = 160
        self.board_cell_height = 202

        # rettangoli fissi delle nove caselle
        self.board_cell_rects = []

        for row in range(3):

            board_row_rects = []

            for column in range(3):

                cell_rect = pygame.Rect(
                    (
                        self.board_x
                        + column * self.board_cell_width
                    ),
                    (
                        self.board_y
                        + row * self.board_cell_height
                    ),
                    self.board_cell_width,
                    self.board_cell_height
                )

                board_row_rects.append(
                    cell_rect
                )

            self.board_cell_rects.append(
                board_row_rects
            )

        # punteggio iniziale dei due giocatori
        self.player_score = 5
        self.opponent_score = 5

        # risultato finale della partita;
        # rimane None finché la partita non termina
        self.match_result = None

        # momento di inizio dell'animazione
        # di comparsa del risultato finale
        self.result_fade_start_time = None

        # durata del fade-in espressa in millisecondi
        self.result_fade_duration = 800

        # dimensioni dei numeri del punteggio;
        # circa un terzo dell'altezza delle carte
        self.score_number_size = (
            64,
            64
        )

        # numeri azzurri usati per il punteggio del giocatore
        self.player_score_number_surfaces = {}

        # numeri rossi usati per il punteggio dell'avversario
        self.opponent_score_number_surfaces = {}

        # carico e preparo ogni numero una sola volta
        for value in range(1, 10):

            number_surface = pygame.image.load(
                (
                    "assets/images/cards/numbers/"
                    f"{value}.png"
                )
            ).convert_alpha()

            number_surface = pygame.transform.smoothscale(
                number_surface,
                self.score_number_size
            )

            # il punteggio del giocatore sfuma
            # dal bianco all'azzurro chiaro
            player_number_surface = self.apply_score_gradient(
                number_surface,
                (255, 255, 255),
                (105, 185, 255)
            )

            # il punteggio dell'avversario sfuma
            # dal bianco al rosso chiaro
            opponent_number_surface = self.apply_score_gradient(
                number_surface,
                (255, 255, 255),
                (255, 125, 125)
            )

            self.player_score_number_surfaces[
                value
            ] = player_number_surface

            self.opponent_score_number_surfaces[
                value
            ] = opponent_number_surface

        # conservo le regole configurate
        # prima dell'inizio della partita
        self.match_rules = match_rules

        # creo il tabellone logico 3x3
        self.board = Board()

        self.board_card_surfaces = {}

        # posizioni delle carte che stanno eseguendo
        # contemporaneamente l'animazione di cattura
        self.flipping_card_positions = []

        # proprietario che riceverà le carte catturate
        # al centro dell'animazione di flip
        self.flip_new_owner = None

                # fase corrente del flip verticale:
        # front_shrinking: il vecchio fronte si restringe
        # back_expanding: il retro si allarga
        # back_shrinking: il retro si restringe
        # front_expanding: il nuovo fronte si allarga
        self.flip_phase = None

        # momento nel quale è iniziata la fase corrente
        self.flip_phase_start_time = 0

        # durata in millisecondi di ogni quarto del flip;
        # l'animazione completa durerà circa 480 millisecondi
        self.flip_phase_duration = 120

        # carico i PNG mostrati quando
        # si attivano le regole speciali
        self.rule_effect_surfaces = {
            "same": pygame.image.load(
                "assets/images/cards/rules/same.png"
            ).convert_alpha(),

            "plus": pygame.image.load(
                "assets/images/cards/rules/plus.png"
            ).convert_alpha(),

            "combo": pygame.image.load(
                "assets/images/cards/rules/combo.png"
            ).convert_alpha()
        }

        # coda delle regole che devono ancora essere risolte;
        # ogni elemento conterrà nome, catture e proprietario
        self.rule_resolution_queue = []

        # carte catturate direttamente da Same o Plus;
        # dopo il loro flip daranno origine alla Combo
        self.pending_combo_source_positions = []

        # regola il cui PNG è attualmente visibile;
        # None significa che non è mostrato alcun feedback
        self.active_rule_effect = None

        # momento nel quale è apparso
        # il PNG della regola attiva
        self.active_rule_effect_start_time = 0

        # ogni PNG rimane visibile per un secondo
        self.rule_effect_duration = 1000

        # carico il retro della carta usato
        # durante il centro dell'animazione
        self.board_card_back_surface = pygame.image.load(
            CARD_BACK_PATH
        ).convert_alpha()

        # ridimensiono il retro come le carte sul tabellone
        self.board_card_back_surface = pygame.transform.smoothscale(
            self.board_card_back_surface,
            self.match_card_size
        )

        # carico lo sfondo contenente
        # il tabellone disegnato graficamente
        self.background_image = pygame.image.load(
            "assets/images/background_match_screen.png"
        ).convert()

        # assicuro che lo sfondo occupi
        # esattamente l'intera finestra
        self.background_image = pygame.transform.scale(
            self.background_image,
            (
                self.width,
                self.height
            )
        )

        # percorsi delle immagini mostrate
        # in base al risultato finale della partita
        result_image_paths = {
            "win": "assets/images/win.png",
            "loss": "assets/images/loss.png",
            "draw": "assets/images/draw.png"
        }

        # superfici delle tre possibili schermate finali
        self.result_surfaces = {}

        # carico una sola volta le immagini dei risultati
        for result_name, image_path in result_image_paths.items():

            result_surface = pygame.image.load(
                image_path
            ).convert_alpha()

            # mantengo la risoluzione originale di 400 x 350 pixel
            self.result_surfaces[
                result_name
            ] = result_surface

    # costruisce una freccia triangolare
    # con una sfumatura verticale rossa
    def create_turn_arrow_surface(self, direction):

        arrow_width = self.turn_arrow_size[0]
        arrow_height = self.turn_arrow_size[1]

        # superficie che conterrà la sfumatura
        gradient_surface = pygame.Surface(
            self.turn_arrow_size,
            pygame.SRCALPHA
        )

        # disegno la sfumatura una riga alla volta
        for y in range(arrow_height):

            gradient_progress = (
                y / (arrow_height - 1)
            )

            red = int(
                self.turn_arrow_top_color[0]
                + (
                    self.turn_arrow_bottom_color[0]
                    - self.turn_arrow_top_color[0]
                ) * gradient_progress
            )

            green = int(
                self.turn_arrow_top_color[1]
                + (
                    self.turn_arrow_bottom_color[1]
                    - self.turn_arrow_top_color[1]
                ) * gradient_progress
            )

            blue = int(
                self.turn_arrow_top_color[2]
                + (
                    self.turn_arrow_bottom_color[2]
                    - self.turn_arrow_top_color[2]
                ) * gradient_progress
            )

            pygame.draw.line(
                gradient_surface,
                (red, green, blue, 255),
                (0, y),
                (arrow_width, y)
            )

        # preparo una maschera trasparente
        # con la forma triangolare della freccia
        arrow_mask = pygame.Surface(
            self.turn_arrow_size,
            pygame.SRCALPHA
        )

        # punti della freccia rivolta a sinistra
        if direction == "left":
            arrow_points = [
                (arrow_width - 8, 8),
                (8, arrow_height // 2),
                (arrow_width - 8, arrow_height - 8)
            ]

        # punti della freccia rivolta a destra
        elif direction == "right":
            arrow_points = [
                (8, 8),
                (arrow_width - 8, arrow_height // 2),
                (8, arrow_height - 8)
            ]

        # punti del triangolo rivolto verso il basso
        else:
            arrow_points = [
                (8, 8),
                (arrow_width - 8, 8),
                (arrow_width // 2, arrow_height - 8)
            ]

        pygame.draw.polygon(
            arrow_mask,
            (255, 255, 255, 255),
            arrow_points
        )

        # applico la forma triangolare
        # alla superficie contenente la sfumatura
        gradient_surface.blit(
            arrow_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        return gradient_surface
    
    # applica una sfumatura verticale alle parti bianche
    # di una superficie, mantenendo nero e trasparenza
    def apply_score_gradient(
        self,
        number_surface,
        top_color,
        bottom_color
    ):

        # creo la superficie della sfumatura
        gradient_surface = pygame.Surface(
            self.score_number_size,
            pygame.SRCALPHA
        )

        # creo la sfumatura verticale una riga alla volta
        for y in range(self.score_number_size[1]):

            gradient_progress = (
                y / (self.score_number_size[1] - 1)
            )

            red = int(
                top_color[0]
                + (bottom_color[0] - top_color[0])
                * gradient_progress
            )

            green = int(
                top_color[1]
                + (bottom_color[1] - top_color[1])
                * gradient_progress
            )

            blue = int(
                top_color[2]
                + (bottom_color[2] - top_color[2])
                * gradient_progress
            )

            pygame.draw.line(
                gradient_surface,
                (red, green, blue, 255),
                (0, y),
                (self.score_number_size[0], y)
            )

        # creo una copia del numero originale
        colored_surface = number_surface.copy()

        # applico la sfumatura alle parti bianche
        colored_surface.blit(
            gradient_surface,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        return colored_surface

    # restituisce le posizioni catturate
    # dall'eventuale attivazione della regola Plus
    def get_plus_capture_positions(
        self,
        row,
        column
    ):

        # Plus deve essere attiva nelle regole Extra
        if not self.match_rules["extra"]["Plus"]:
            return []

        # recupero la carta appena posizionata
        placed_cell = self.board.get_cell(
            row,
            column
        )

        if placed_cell is None:
            return []

        placed_card = placed_cell["card"]
        placed_owner = placed_cell["owner"]

        # per ogni possibile somma conserverò
        # le carte adiacenti che la producono
        sum_groups = {}

        # per ogni direzione salvo:
        # spostamento, lato della carta posizionata
        # e lato opposto della carta adiacente
        directions = [
            (-1, 0, "top", "bottom"),
            (0, 1, "right", "left"),
            (1, 0, "bottom", "top"),
            (0, -1, "left", "right")
        ]

        # calcolo la somma prodotta
        # da ogni coppia di lati adiacenti
        for (
            row_offset,
            column_offset,
            placed_side,
            neighbour_side
        ) in directions:

            neighbour_row = row + row_offset
            neighbour_column = column + column_offset

            neighbour_cell = self.board.get_cell(
                neighbour_row,
                neighbour_column
            )

            # ignoro i bordi e le caselle vuote
            if neighbour_cell is None:
                continue

            neighbour_card = neighbour_cell["card"]

            placed_value = getattr(
                placed_card,
                placed_side
            )

            neighbour_value = getattr(
                neighbour_card,
                neighbour_side
            )

            side_sum = (
                placed_value + neighbour_value
            )

            # creo il gruppo della somma
            # se non era ancora presente
            if side_sum not in sum_groups:
                sum_groups[side_sum] = []

            sum_groups[side_sum].append(
                (
                    neighbour_row,
                    neighbour_column,
                    neighbour_cell["owner"]
                )
            )

        # conterrà le carte avversarie coinvolte
        # in gruppi con almeno due somme uguali
        plus_capture_positions = []

        for matching_neighbours in sum_groups.values():

            # una singola somma non attiva Plus
            if len(matching_neighbours) < 2:
                continue

            # le carte alleate contribuiscono alla regola,
            # ma soltanto quelle avversarie vengono catturate
            for (
                neighbour_row,
                neighbour_column,
                neighbour_owner
            ) in matching_neighbours:

                if neighbour_owner == placed_owner:
                    continue

                capture_position = (
                    neighbour_row,
                    neighbour_column
                )

                # evito eventuali posizioni duplicate
                if (
                    capture_position
                    not in plus_capture_positions
                ):
                    plus_capture_positions.append(
                        capture_position
                    )

        return plus_capture_positions

    # restituisce le posizioni catturate
    # dall'eventuale attivazione della regola Same
    def get_same_capture_positions(
        self,
        row,
        column
    ):

        # Same deve essere attiva nelle regole Extra
        if not self.match_rules["extra"]["Same"]:
            return []

        # recupero la carta appena piazzata
        placed_cell = self.board.get_cell(
            row,
            column
        )

        if placed_cell is None:
            return []

        placed_card = placed_cell["card"]
        placed_owner = placed_cell["owner"]

        # conterrà tutte le carte adiacenti
        # i cui valori coincidono
        matching_neighbours = []

        directions = [
            (-1, 0, "top", "bottom"),
            (0, 1, "right", "left"),
            (1, 0, "bottom", "top"),
            (0, -1, "left", "right")
        ]

        # confronto tutti i lati adiacenti
        for (
            row_offset,
            column_offset,
            placed_side,
            neighbour_side
        ) in directions:

            neighbour_row = row + row_offset
            neighbour_column = column + column_offset

            # recupero prima il valore del lato
            # della carta appena posizionata
            placed_value = getattr(
                placed_card,
                placed_side
            )

            # controllo se la direzione conduce
            # fuori dai confini del tabellone
            neighbour_is_wall = not (
                0 <= neighbour_row < 3
                and 0 <= neighbour_column < 3
            )

            if neighbour_is_wall:

                # con Wall attiva, ogni bordo esterno
                # viene considerato come un valore 10
                if (
                    self.match_rules["special"]["Wall"]
                    and placed_value == 10
                ):
                    matching_neighbours.append(
                        (
                            None,
                            None,
                            "wall"
                        )
                    )

                # oltre il bordo non può esserci una carta
                continue

            # la posizione è interna al tabellone;
            # recupero l'eventuale carta adiacente
            neighbour_cell = self.board.get_cell(
                neighbour_row,
                neighbour_column
            )

            # ignoro le caselle interne ancora vuote
            if neighbour_cell is None:
                continue

            neighbour_card = neighbour_cell["card"]

            neighbour_value = getattr(
                neighbour_card,
                neighbour_side
            )

            # salvo ogni lato con valori identici
            if placed_value == neighbour_value:
                matching_neighbours.append(
                    (
                        neighbour_row,
                        neighbour_column,
                        neighbour_cell["owner"]
                    )
                )

        # Same richiede almeno due coincidenze
        if len(matching_neighbours) < 2:
            return []

        # almeno una delle carte coincidenti
        # deve appartenere all'avversario
        # almeno una corrispondenza deve essere
        # una vera carta appartenente all'avversario;
        # il muro da solo non può essere catturato
        opponent_is_involved = any(
            neighbour_owner not in (
                placed_owner,
                "wall"
            )
            for (
                neighbour_row,
                neighbour_column,
                neighbour_owner
            ) in matching_neighbours
        )

        if not opponent_is_involved:
            return []

        # restituisco soltanto le carte avversarie;
        # quelle alleate contribuiscono alla regola
        # ma non devono cambiare proprietario
        return [
            (
                neighbour_row,
                neighbour_column
            )
            for (
                neighbour_row,
                neighbour_column,
                neighbour_owner
            ) in matching_neighbours
            if neighbour_owner not in (
                placed_owner,
                "wall"
            )
        ]
    
    # individua le catture normali, Same e Plus
    # e prepara la loro risoluzione nell'ordine corretto
    def resolve_basic_captures(
        self,
        row,
        column
    ):

        placed_cell = self.board.get_cell(
            row,
            column
        )

        if placed_cell is None:
            return False

        placed_card = placed_cell["card"]
        placed_owner = placed_cell["owner"]

        # controllo le due regole speciali;
        # l'ordine di risoluzione sarà Same e poi Plus
        same_capture_positions = (
            self.get_same_capture_positions(
                row,
                column
            )
        )

        plus_capture_positions = (
            self.get_plus_capture_positions(
                row,
                column
            )
        )

        # conterrà separatamente le catture
        # prodotte dal normale valore maggiore
        basic_capture_positions = []

        directions = [
            (-1, 0, "top", "bottom"),
            (0, 1, "right", "left"),
            (1, 0, "bottom", "top"),
            (0, -1, "left", "right")
        ]

        for (
            row_offset,
            column_offset,
            placed_side,
            neighbour_side
        ) in directions:

            neighbour_row = row + row_offset
            neighbour_column = column + column_offset

            neighbour_cell = self.board.get_cell(
                neighbour_row,
                neighbour_column
            )

            # ignoro bordi, caselle vuote
            # e carte già appartenenti allo stesso giocatore
            if (
                neighbour_cell is None
                or neighbour_cell["owner"] == placed_owner
            ):
                continue

            neighbour_card = neighbour_cell["card"]

            placed_value = getattr(
                placed_card,
                placed_side
            )

            neighbour_value = getattr(
                neighbour_card,
                neighbour_side
            )

            if placed_value > neighbour_value:

                capture_position = (
                    neighbour_row,
                    neighbour_column
                )

                if (
                    capture_position
                    not in basic_capture_positions
                ):
                    basic_capture_positions.append(
                        capture_position
                    )

        # pulisco la coda di un'eventuale
        # risoluzione precedente
        self.rule_resolution_queue = []

        # Same ha sempre la precedenza su Plus
        if same_capture_positions:

            same_batch = list(
                same_capture_positions
            )

            # le catture normali della stessa mossa
            # flippano insieme alle catture di Same
            for position in basic_capture_positions:
                if position not in same_batch:
                    same_batch.append(
                        position
                    )

            self.queue_rule_resolution(
                "same",
                same_batch,
                placed_owner,
                same_capture_positions
            )

            # se si è attivata anche Plus,
            # verrà mostrata e risolta dopo Same
            if plus_capture_positions:

                # non devo flippare nuovamente carte
                # già catturate dal primo gruppo
                remaining_plus_positions = [
                    position
                    for position in plus_capture_positions
                    if position not in same_batch
                ]

                # mostro Plus soltanto se cattura almeno una carta
                # che non è già stata catturata tramite Same
                if remaining_plus_positions:
                    self.queue_rule_resolution(
                        "plus",
                        remaining_plus_positions,
                        placed_owner,
                        remaining_plus_positions
                    )

        # se Same non è attiva, Plus diventa
        # la prima regola della sequenza
        elif plus_capture_positions:

            plus_batch = list(
                plus_capture_positions
            )

            # le normali catture della carta posizionata
            # avvengono insieme alle catture di Plus
            for position in basic_capture_positions:
                if position not in plus_batch:
                    plus_batch.append(
                        position
                    )

            self.queue_rule_resolution(
                "plus",
                plus_batch,
                placed_owner,
                plus_capture_positions
            )

        # senza regole speciali eseguo
        # immediatamente le catture normali
        else:

            if not basic_capture_positions:
                return False

            self.flipping_card_positions = list(
                basic_capture_positions
            )

            self.flip_new_owner = placed_owner
            self.flip_phase = "front_shrinking"
            self.flip_phase_start_time = (
                pygame.time.get_ticks()
            )

            return True

        # mostro il PNG della prima regola in coda
        self.start_next_rule_effect()

        return True

    # calcola una singola ondata di Combo partendo
    # dalle carte catturate nell'ondata precedente
    def get_combo_capture_positions(
        self,
        source_positions,
        new_owner
    ):

        # Combo deve essere attiva nelle regole Extra
        if not self.match_rules["extra"]["Combo"]:
            return []

        # conterrà le nuove carte catturate
        # durante questa singola ondata
        combo_capture_positions = []

        # per ogni direzione salvo:
        # spostamento, lato della carta sorgente
        # e lato opposto della carta adiacente
        directions = [
            (-1, 0, "top", "bottom"),
            (0, 1, "right", "left"),
            (1, 0, "bottom", "top"),
            (0, -1, "left", "right")
        ]

        # ogni carta catturata nell'ondata precedente
        # si comporta come se fosse stata appena posizionata
        for source_row, source_column in source_positions:

            source_cell = self.board.get_cell(
                source_row,
                source_column
            )

            # ignoro eventuali posizioni non valide
            if source_cell is None:
                continue

            source_card = source_cell["card"]

            # confronto la carta sorgente
            # con tutte le carte adiacenti
            for (
                row_offset,
                column_offset,
                source_side,
                neighbour_side
            ) in directions:

                neighbour_row = (
                    source_row + row_offset
                )

                neighbour_column = (
                    source_column + column_offset
                )

                neighbour_cell = self.board.get_cell(
                    neighbour_row,
                    neighbour_column
                )

                # ignoro bordi, caselle vuote
                # e carte già appartenenti al nuovo proprietario
                if (
                    neighbour_cell is None
                    or neighbour_cell["owner"] == new_owner
                ):
                    continue

                neighbour_card = neighbour_cell["card"]

                source_value = getattr(
                    source_card,
                    source_side
                )

                neighbour_value = getattr(
                    neighbour_card,
                    neighbour_side
                )

                # durante Combo si applica soltanto
                # il normale confronto valore maggiore
                if source_value > neighbour_value:

                    capture_position = (
                        neighbour_row,
                        neighbour_column
                    )

                    # una carta adiacente potrebbe essere raggiunta
                    # da più sorgenti nella stessa ondata
                    if (
                        capture_position
                        not in combo_capture_positions
                    ):
                        combo_capture_positions.append(
                            capture_position
                        )

        return combo_capture_positions

    # aggiunge alla coda una regola attivata
    # insieme alle carte che dovrà catturare
    def queue_rule_resolution(
        self,
        rule_name,
        captured_positions,
        new_owner,
        combo_source_positions
    ):

        self.rule_resolution_queue.append(
            {
                "name": rule_name,

                # tutte le carte che devono flippare
                # durante la risoluzione della regola
                "captured_positions": list(
                    captured_positions
                ),

                "new_owner": new_owner,

                # soltanto le carte catturate direttamente
                # da Same o Plus possono avviare Combo
                "combo_source_positions": list(
                    combo_source_positions
                )
            }
        )

    # mostra il PNG della prossima regola
    # presente nella coda di risoluzione
    def start_next_rule_effect(self):

        # non esistono altre regole da mostrare
        if not self.rule_resolution_queue:
            return False

        # estraggo la prima regola della coda
        self.active_rule_effect = (
            self.rule_resolution_queue.pop(0)
        )

        # salvo il momento di comparsa del PNG
        self.active_rule_effect_start_time = (
            pygame.time.get_ticks()
        )

        return True


    # conclude l'intera sequenza di catture
    # e permette al turno di proseguire
    def finish_capture_resolution(self):

        # se questa era l'ultima mossa,
        # ora posso determinare il risultato
        if self.input_mode == "match_over":
            self.determine_match_result()
            return

        # dopo tutte le catture avvio
        # il trasferimento del turno già preparato
        if (
            self.input_mode
            == "waiting_for_turn_transition"
            and self.pending_turn_owner is not None
        ):
            self.start_turn_indicator_transition(
                self.pending_turn_owner
            )


    # aggiorna il PNG della regola attualmente visibile
    # e avvia il relativo gruppo di flip
    def update_active_rule_effect(self):

        if self.active_rule_effect is None:
            return

        current_time = pygame.time.get_ticks()

        elapsed_time = (
            current_time
            - self.active_rule_effect_start_time
        )

        # mantengo il PNG visibile per un secondo
        if elapsed_time < self.rule_effect_duration:
            return

        # conservo la regola prima di nasconderne il PNG
        completed_rule_effect = (
            self.active_rule_effect
        )

        self.active_rule_effect = None

        captured_positions = (
            completed_rule_effect[
                "captured_positions"
            ]
        )

        # aggiungo le nuove sorgenti a quelle eventualmente
        # prodotte da una regola precedente nella stessa mossa
        for combo_source_position in completed_rule_effect[
            "combo_source_positions"
        ]:

            if (
                combo_source_position
                not in self.pending_combo_source_positions
            ):
                self.pending_combo_source_positions.append(
                    combo_source_position
                )  

        # se la regola possiede carte da catturare,
        # avvio il relativo flip simultaneo
        if captured_positions:

            self.flipping_card_positions = list(
                captured_positions
            )

            self.flip_new_owner = (
                completed_rule_effect[
                    "new_owner"
                ]
            )

            self.flip_phase = "front_shrinking"
            self.flip_phase_start_time = current_time
            return

        # una regola può essere stata attivata anche se
        # le sue carte sono già state catturate da una
        # regola precedente; in quel caso passo oltre
        if not self.start_next_rule_effect():
            self.finish_capture_resolution()
        
    # aggiorna le quattro fasi del flip
    # delle carte catturate
    def update_capture_animation(self):

        # non faccio nulla se non è in corso un flip
        if self.flip_phase is None:
            return

        current_time = pygame.time.get_ticks()

        elapsed_time = (
            current_time
            - self.flip_phase_start_time
        )

        # aspetto che la fase corrente sia terminata
        if elapsed_time < self.flip_phase_duration:
            return

        # il vecchio fronte ha terminato
        # di restringersi: mostro il retro
        if self.flip_phase == "front_shrinking":
            self.flip_phase = "back_expanding"

        # il retro ha raggiunto la larghezza completa
        elif self.flip_phase == "back_expanding":
            self.flip_phase = "back_shrinking"

        # il retro è nuovamente diventato sottile;
        # ora cambio il proprietario delle carte
        elif self.flip_phase == "back_shrinking":

            # cambio proprietario e punteggio
            # per tutte le carte catturate insieme
            for row, column in self.flipping_card_positions:

                self.board.change_owner(
                    row,
                    column,
                    self.flip_new_owner
                )

                if self.flip_new_owner == "player":
                    self.player_score += 1
                    self.opponent_score -= 1

                else:
                    self.player_score -= 1
                    self.opponent_score += 1

            # ora può apparire il fronte con il nuovo colore
            self.flip_phase = "front_expanding"

        # il nuovo fronte ha recuperato
        # la propria larghezza completa
        elif self.flip_phase == "front_expanding":

            # conservo il proprietario prima
            # di pulire i dati del flip terminato
            completed_flip_owner = (
                self.flip_new_owner
            )


            # Same e Plus devono essere risolte entrambe
            # prima di iniziare l'eventuale catena Combo
            if self.rule_resolution_queue:

                # termino e pulisco il flip appena concluso
                self.flip_phase = None
                self.flipping_card_positions = []
                self.flip_new_owner = None

                # mostro la prossima regola speciale
                self.start_next_rule_effect()
                return
            
            # calcolo la nuova ondata di Combo usando
            # soltanto le sorgenti di Same, Plus
            # oppure della precedente ondata di Combo
            combo_capture_positions = (
                self.get_combo_capture_positions(
                    self.pending_combo_source_positions,
                    completed_flip_owner
                )
            )

            # le sorgenti sono state elaborate;
            # l'eventuale nuova ondata diventerà
            # la sorgente della Combo successiva
            self.pending_combo_source_positions = []

            # termino e pulisco l'animazione
            self.flip_phase = None
            self.flipping_card_positions = []
            self.flip_new_owner = None

            # ogni ondata di Combo ha la precedenza
            # sulle altre regole ancora presenti in coda
            if combo_capture_positions:

                self.rule_resolution_queue.insert(
                    0,
                    {
                        "name": "combo",

                        # carte che flipperanno
                        # contemporaneamente in questa ondata
                        "captured_positions": list(
                            combo_capture_positions
                        ),

                        "new_owner": completed_flip_owner,

                        # queste carte potranno generare
                        # la successiva ondata di Combo
                        "combo_source_positions": list(
                            combo_capture_positions
                        )
                    }
                )

            # mostro il PNG della Combo oppure
            # quello della prossima regola in attesa
            if self.start_next_rule_effect():
                return

            # non esistono altri gruppi di catture;
            # posso terminare la risoluzione della mossa
            self.finish_capture_resolution()

            return

        # ogni nuova fase parte dal momento attuale
        self.flip_phase_start_time = current_time

    # ricostruisce le due mani per un nuovo round
    # di Sudden Death usando i proprietari finali
    def get_sudden_death_hands(self):

        # carte che appartengono al giocatore
        # e all'avversario alla fine del round
        new_player_cards = []
        new_opponent_cards = []

        # recupero le nove carte posizionate
        # sul tabellone
        for row in range(3):
            for column in range(3):

                board_cell = self.board.get_cell(
                    row,
                    column
                )

                if board_cell is None:
                    continue

                card = board_cell["card"]
                owner = board_cell["owner"]

                # le carte blu passano al giocatore
                if owner == "player":
                    new_player_cards.append(
                        card
                    )

                # le carte rosse passano all'avversario
                else:
                    new_opponent_cards.append(
                        card
                    )

        # aggiungo le eventuali carte del giocatore
        # che non sono state posizionate sul tabellone
        for i, card in enumerate(self.player_cards):

            if i not in self.played_player_card_indices:
                new_player_cards.append(
                    card
                )

        # aggiungo le eventuali carte dell'avversario
        # che non sono state posizionate sul tabellone
        for i, card in enumerate(self.opponent_cards):

            if i not in self.played_opponent_card_indices:
                new_opponent_cards.append(
                    card
                )

        # un pareggio deve produrre esattamente
        # cinque carte per ciascun giocatore
        if (
            len(new_player_cards) != 5
            or len(new_opponent_cards) != 5
        ):
            raise ValueError(
                "Invalid Sudden Death hands: "
                f"player={len(new_player_cards)}, "
                f"opponent={len(new_opponent_cards)}"
            )

        return (
            new_player_cards,
            new_opponent_cards
        )

    # determina il risultato confrontando
    # i punteggi finali dei due giocatori
    def determine_match_result(self):

        if self.player_score > self.opponent_score:
            self.match_result = "win"

        elif self.player_score < self.opponent_score:
            self.match_result = "loss"

        else:
            self.match_result = "draw"

        # avvio il fade-in dell'immagine del risultato
        self.result_fade_start_time = pygame.time.get_ticks()

    # controlla se tutte le nove caselle sono occupate
    # e interrompe i normali turni della partita
    def check_match_finished(self):

        # se esiste ancora una casella vuota,
        # la partita deve continuare
        if not self.board.is_full():
            return False

        # blocco i controlli e i turni normali
        self.input_mode = "match_over"

        # attendo anche l'eventuale feedback di Same
        # prima di calcolare il risultato definitivo
        if (
            self.flip_phase is None
            and self.active_rule_effect is None
            and not self.rule_resolution_queue
        ):
            self.determine_match_result()

        # interrompo l'eventuale turno dell'avversario
        self.opponent_turn_phase = None

        # pulisco le selezioni temporanee dell'avversario
        self.selected_opponent_card = None
        self.opponent_target_row = None
        self.opponent_target_column = None

        # segnalo che il tabellone è completo
        return True

    # sposta la selezione saltando
    # le carte già giocate
    def move_player_card_selection(self, direction):

        # provo al massimo tutti e cinque gli slot
        for step in range(len(self.player_cards)):

            next_index = (
                self.selected_player_card + direction
            ) % len(self.player_cards)

            self.selected_player_card = next_index

            # interrompo quando trovo una carta disponibile
            if (
                self.selected_player_card
                not in self.played_player_card_indices
            ):
                return

    # piazza sul tabellone la carta scelta dal giocatore
    def place_selected_player_card(self):

        # il piazzamento è possibile soltanto
        # durante la selezione di una casella
        if (
            self.input_mode != "board"
            or not self.player_cards
        ):
            return

        # recupero la carta scelta
        selected_card = self.player_cards[
            self.selected_player_card
        ]

        # provo a inserire la carta nella casella selezionata
        card_placed = self.board.place_card(
            selected_card,
            "player",
            self.selected_board_row,
            self.selected_board_column
        )

        # una casella già occupata non può essere utilizzata
        if not card_placed:
            return

        # confronto la carta appena piazzata
        # con tutte le carte avversarie adiacenti
        capture_started = self.resolve_basic_captures(
            self.selected_board_row,
            self.selected_board_column
        )

        # segno lo slot come utilizzato senza rimuoverlo;
        # le altre carte mantengono così la loro posizione
        self.played_player_card_indices.add(
            self.selected_player_card
        )

        # se il tabellone è pieno, termino la partita
        # senza avviare un altro turno avversario
        if self.check_match_finished():
            return

        # se è iniziata una cattura, attendo prima
        # che tutte le carte abbiano terminato il flip
        if capture_started:
            self.input_mode = "waiting_for_turn_transition"
            self.pending_turn_owner = "opponent"

        # senza catture posso iniziare immediatamente
        # il trasferimento dell'indicatore
        else:
            self.start_turn_indicator_transition(
                "opponent"
            )

    # avvia il trasferimento dell'indicatore
    # verso il giocatore che riceverà il turno
    def start_turn_indicator_transition(
        self,
        new_turn_owner
    ):

        # salvo il prossimo proprietario del turno
        self.pending_turn_owner = new_turn_owner

        # inizio facendo salire l'indicatore attuale
        self.turn_indicator_transition_phase = "leaving"

        # salvo il momento di inizio della salita
        self.turn_indicator_transition_start_time = (
            pygame.time.get_ticks()
        )

        # blocco temporaneamente gli input e i turni
        self.input_mode = "turn_transition"

    # aggiorna la salita, la pausa e la discesa
    # dell'indicatore del turno
    def update_turn_indicator_transition(self):

        current_time = pygame.time.get_ticks()

        elapsed_time = (
            current_time
            - self.turn_indicator_transition_start_time
        )

        # attendo che l'indicatore completi la salita
        if self.turn_indicator_transition_phase == "leaving":

            if elapsed_time < self.turn_indicator_leave_duration:
                return

            # raggiunta la parte superiore,
            # inizio la breve pausa fuori dallo schermo
            self.turn_indicator_transition_phase = "waiting"
            self.turn_indicator_transition_start_time = current_time
            return

        # mantengo l'indicatore fuori dallo schermo
        if self.turn_indicator_transition_phase == "waiting":

            if elapsed_time < self.turn_indicator_wait_duration:
                return

            # terminata la pausa, comincio a farlo
            # scendere sul lato del nuovo giocatore
            self.turn_indicator_transition_phase = "entering"
            self.turn_indicator_transition_start_time = current_time
            return

        # attendo il completamento della discesa
        if self.turn_indicator_transition_phase == "entering":

            if elapsed_time < self.turn_indicator_enter_duration:
                return

            # assegno definitivamente il turno
            # al nuovo proprietario
            self.active_turn_owner = self.pending_turn_owner

            # termino e pulisco il trasferimento
            self.pending_turn_owner = None
            self.turn_indicator_transition_phase = None

            # se il turno passa all'avversario,
            # avvio la sua prima fase di attesa
            if self.active_turn_owner == "opponent":
                self.input_mode = "opponent_turn"
                self.opponent_turn_phase = "waiting_to_select"
                self.opponent_phase_start_time = current_time

            # il passaggio al giocatore verrà utilizzato
            # anche al termine del turno avversario
            else:
                self.input_mode = "hand"
                
    # aggiorna l'animazione iniziale
    # che determina chi comincia la partita
    def update_starting_turn_animation(self):

        current_time = pygame.time.get_ticks()

        # quando la freccia si è fermata,
        # attendo brevemente prima di iniziare
        if self.turn_arrow_phase == "stopped":

            if (
                current_time
                - self.turn_arrow_finished_time
                < self.turn_arrow_result_pause
            ):
                return

            # terminata l'estrazione, mostro l'indicatore
            # permanente sopra la mano di chi inizia
            self.active_turn_owner = self.starting_turn_owner

            # se è stato scelto il giocatore,
            # attivo i controlli della sua mano
            if self.starting_turn_owner == "player":
                self.input_mode = "hand"

            # se è stato scelto l'avversario,
            # avvio normalmente il suo turno
            else:
                self.input_mode = "opponent_turn"
                self.opponent_turn_phase = "waiting_to_select"
                self.opponent_phase_start_time = current_time

            # l'animazione iniziale è terminata
            self.turn_arrow_phase = None
            return

        elapsed_time = (
            current_time
            - self.turn_arrow_phase_start_time
        )

        # aspetto il completamento
        # della fase corrente
        if elapsed_time < self.turn_arrow_phase_duration:
            return

        # la freccia è diventata sottile;
        # cambio il lato verso il quale è rivolta
        if self.turn_arrow_phase == "shrinking":

            if self.turn_arrow_direction == "left":
                self.turn_arrow_direction = "right"
            else:
                self.turn_arrow_direction = "left"

            # ora la nuova freccia si riallarga
            self.turn_arrow_phase = "expanding"
            self.turn_arrow_phase_start_time = current_time
            return

        # la freccia ha recuperato
        # la propria larghezza completa
        if self.turn_arrow_phase == "expanding":

            self.turn_arrow_completed_flips += 1

            # direzione associata al risultato casuale
            if self.starting_turn_owner == "player":
                target_direction = "left"
            else:
                target_direction = "right"

            # dopo il numero minimo di rotazioni,
            # mi fermo appena raggiungo il risultato scelto
            if (
                self.turn_arrow_completed_flips
                >= self.turn_arrow_minimum_flips
                and self.turn_arrow_direction
                == target_direction
            ):
                self.turn_arrow_phase = "stopped"
                self.turn_arrow_finished_time = current_time
                return

            # mantengo veloci le prime rotazioni
            # e rallento soltanto nella parte finale
            completed_slow_flips = max(
                0,
                self.turn_arrow_completed_flips - 9
            )

            self.turn_arrow_phase_duration = min(
                180,
                45 + completed_slow_flips * 15
            )

            # avvio una nuova rotazione
            self.turn_arrow_phase = "shrinking"
            self.turn_arrow_phase_start_time = current_time

    # gestisce gli eventi della partita
    def handle_events(self, event):

        # durante il feedback di Same oppure una cattura
        # blocco temporaneamente tutti gli input
        if (
            self.active_rule_effect is not None
            or self.flip_phase is not None
        ):
            return

        # quando la partita è terminata,
        # accetto soltanto la conferma del risultato
        if (
            self.input_mode == "match_over"
            and self.match_result is not None
        ):

            # controllo se il fade-in è terminato
            result_fade_finished = (
                pygame.time.get_ticks()
                - self.result_fade_start_time
                >= self.result_fade_duration
            )

            # dopo il fade, Invio oppure click sinistro
            # aprono il pannello per la rivincita
            result_confirmed = (
                (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                )
                or
                (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                )
            )

            if (
                result_fade_finished
                and result_confirmed
            ):

                # con un pareggio non avviene alcuno scambio
                if self.match_result == "draw":

                    # con Sudden Death attiva redistribuisco
                    # le stesse dieci carte secondo il colore finale
                    if self.match_rules["special"]["Sudden Death"]:

                        (
                            sudden_death_player_cards,
                            sudden_death_opponent_cards
                        ) = self.get_sudden_death_hands()

                        # creo immediatamente un nuovo round,
                        # conservando entrambe le mani redistribuite
                        sudden_death_match = MatchScreen(
                            self.width,
                            self.height,
                            self.state,
                            sudden_death_player_cards,
                            self.match_rules,
                            opponent_cards=(
                                sudden_death_opponent_cards
                            ),
                            preserve_hands=True
                        )

                        self.state.change_screen(
                            sudden_death_match
                        )

                        # assicuro che non rimangano
                        # pannelli aperti dal round precedente
                        self.state.close_panel()

                    # senza Sudden Death mantengo
                    # il normale comportamento Play Again
                    else:
                        self.state.open_panel(
                            PlayAgainPanel(
                                self.width,
                                self.height,
                                self.state,
                                self.player_cards,
                                self.match_rules
                            )
                        )

                # con vittoria o sconfitta passo
                # invece alla schermata dello scambio
                else:

                    trade_screen = TradeScreen(
                        self.width,
                        self.height,
                        self.state,
                        self.player_cards,
                        self.opponent_cards,
                        self.match_rules,
                        self.match_result,
                        self.player_score,
                        self.opponent_score
                    )

                    self.state.change_screen(
                        trade_screen
                    )

                    # assicuro che non rimangano
                    # pannelli aperti sulla nuova schermata
                    self.state.close_panel()

            # durante il risultato blocco
            # tutti gli altri controlli della partita
            return

        # controllo la tastiera
        if event.type == pygame.KEYDOWN:

            # ESC torna alla scelta della carta
            # se la manina si trova sul tabellone
            if (
                event.key == pygame.K_ESCAPE
                and self.input_mode == "board"
            ):
                self.input_mode = "hand"

            # nella modalità hand scelgo una carta
            elif self.input_mode == "hand":

                # ESC chiede conferma prima
                # di abbandonare la partita
                if event.key == pygame.K_ESCAPE:
                    self.state.open_panel(
                        LeaveMatchConfirmationPanel(
                            self.width,
                            self.height,
                            self.state,
                            self.match_rules
                        )
                    )

                # seleziono la carta precedente
                elif (
                    event.key == pygame.K_UP
                    and self.player_cards
                ):
                    self.move_player_card_selection(-1)

                # seleziono la carta successiva
                elif (
                    event.key == pygame.K_DOWN
                    and self.player_cards
                ):
                    self.move_player_card_selection(1)

                # confermo la carta e passo al tabellone
                elif (
                    event.key == pygame.K_RETURN
                    and self.player_cards
                ):
                    self.input_mode = "board"

                    # parto dalla casella in alto a sinistra
                    self.selected_board_row = 0
                    self.selected_board_column = 0

            # nella modalità board scelgo una casella
            elif self.input_mode == "board":

                # sposto la manina nella riga precedente
                if event.key == pygame.K_UP:
                    self.selected_board_row = (
                        self.selected_board_row - 1
                    ) % 3

                # sposto la manina nella riga successiva
                elif event.key == pygame.K_DOWN:
                    self.selected_board_row = (
                        self.selected_board_row + 1
                    ) % 3

                # sposto la manina nella colonna precedente
                elif event.key == pygame.K_LEFT:
                    self.selected_board_column = (
                        self.selected_board_column - 1
                    ) % 3

                # sposto la manina nella colonna successiva
                elif event.key == pygame.K_RIGHT:
                    self.selected_board_column = (
                        self.selected_board_column + 1
                    ) % 3

                # confermo la casella e piazzo la carta
                elif event.key == pygame.K_RETURN:
                    self.place_selected_player_card()

        # il mouseover sulle carte funziona
        # soltanto nella modalità hand
        if (
            event.type == pygame.MOUSEMOTION
            and self.input_mode == "hand"
        ):

            # controllo le aree fisse in ordine inverso
            for i in range(
                len(self.player_card_hover_rects) - 1,
                -1,
                -1
            ):

                # ignoro gli slot delle carte già giocate
                if i in self.played_player_card_indices:
                    continue

                card_rect = self.player_card_hover_rects[i]

                if card_rect.collidepoint(event.pos):
                    self.selected_player_card = i
                    break

        # nella modalità board il mouseover
        # sposta la manina tra le nove caselle
        if (
            event.type == pygame.MOUSEMOTION
            and self.input_mode == "board"
        ):

            # controllo tutte le righe del tabellone
            for row in range(3):

                # controllo tutte le colonne della riga
                for column in range(3):

                    cell_rect = self.board_cell_rects[
                        row
                    ][
                        column
                    ]

                    # seleziono la casella sotto il mouse
                    if cell_rect.collidepoint(event.pos):
                        self.selected_board_row = row
                        self.selected_board_column = column
                        break
        
        # controllo i click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            # il clic sinistro seleziona una carta
            # quando mi trovo nella modalità hand
            if (
                event.button == 1
                and self.input_mode == "hand"
            ):

                # controllo le carte in ordine inverso,
                # perché quelle più in basso sono disegnate sopra
                for i in range(
                    len(self.player_card_rects) - 1,
                    -1,
                    -1
                ):

                    # ignoro gli slot delle carte già giocate
                    if i in self.played_player_card_indices:
                        continue

                    card_rect = self.player_card_rects[i]

                    # seleziono la carta cliccata
                    if card_rect.collidepoint(event.pos):
                        self.selected_player_card = i
                        self.input_mode = "board"

                        # parto dalla casella in alto a sinistra
                        self.selected_board_row = 0
                        self.selected_board_column = 0
                        break

            # nella modalità board il clic sinistro
            # piazza la carta nella casella cliccata
            elif (
                event.button == 1
                and self.input_mode == "board"
            ):

                # controllo tutte le caselle del tabellone
                for row in range(3):
                    for column in range(3):

                        cell_rect = self.board_cell_rects[
                            row
                        ][
                            column
                        ]

                        # recupero la casella cliccata
                        if cell_rect.collidepoint(event.pos):
                            self.selected_board_row = row
                            self.selected_board_column = column

                            # provo a piazzare la carta
                            self.place_selected_player_card()
                            break

                    # interrompo anche il ciclo esterno
                    # se il turno del giocatore è terminato
                    if self.input_mode == "opponent_turn":
                        break
            
            # se la manina si trova sul tabellone,
            # il clic destro torna alla scelta delle carte
            elif (
                event.button == 3
                and self.input_mode == "board"
            ):
                self.input_mode = "hand"

            # se la manina si trova sulla mano,
            # il click destro chiede conferma
            # prima di abbandonare la partita
            elif (
                event.button == 3
                and self.input_mode == "hand"
            ):
                self.state.open_panel(
                    LeaveMatchConfirmationPanel(
                        self.width,
                        self.height,
                        self.state,
                        self.match_rules
                    )
                )

    # aggiorna la logica della partita
    def update(self):

        # prima dell'inizio della partita,
        # aggiorno soltanto la freccia 50:50
        if self.input_mode == "starting_turn_animation":
            self.update_starting_turn_animation()
            return

        # il PNG della regola deve terminare
        # prima di avviare il relativo flip
        if self.active_rule_effect is not None:
            self.update_active_rule_effect()
            return
        
        # l'animazione di cattura ha la precedenza
        # su qualsiasi avanzamento del turno
        if self.flip_phase is not None:
            self.update_capture_animation()
            return

        # durante il trasferimento aggiorno soltanto
        # il movimento dell'indicatore del turno
        if self.input_mode == "turn_transition":
            self.update_turn_indicator_transition()
            return

        # se attendo la conclusione di un flip,
        # non devo ancora iniziare il nuovo turno
        if self.input_mode == "waiting_for_turn_transition":
            return

        # interrompo se non è il turno dell'avversario
        if self.input_mode != "opponent_turn":
            return

        # recupero il tempo attuale
        current_time = pygame.time.get_ticks()

        # calcolo il tempo trascorso nella fase corrente
        elapsed_time = (
            current_time
            - self.opponent_phase_start_time
        )

        # nella prima fase attendo prima di scegliere
        if (
            self.opponent_turn_phase == "waiting_to_select"
            and elapsed_time >= self.opponent_phase_duration
        ):

            # recupero gli indici delle carte
            # che l'avversario non ha ancora giocato
            available_card_indices = [
                i
                for i in range(len(self.opponent_cards))
                if i not in self.played_opponent_card_indices
            ]

            # recupero tutte le caselle ancora vuote
            empty_board_positions = []

            for row in range(3):
                for column in range(3):

                    if self.board.is_empty(
                        row,
                        column
                    ):
                        empty_board_positions.append(
                            (
                                row,
                                column
                            )
                        )

            # interrompo se non esistono mosse disponibili
            if (
                not available_card_indices
                or not empty_board_positions
            ):
                return

            # scelgo casualmente una carta disponibile
            self.selected_opponent_card = random.choice(
                available_card_indices
            )

            # scelgo casualmente una casella vuota
            (
                self.opponent_target_row,
                self.opponent_target_column
            ) = random.choice(
                empty_board_positions
            )

            # passo alla fase che mostra la carta scelta
            self.opponent_turn_phase = "showing_selection"

            # riavvio il timer della nuova fase
            self.opponent_phase_start_time = current_time

        # dopo aver mostrato la carta scelta,
        # l'avversario la piazza sul tabellone
        elif (
            self.opponent_turn_phase == "showing_selection"
            and elapsed_time >= self.opponent_phase_duration
        ):

            # recupero la carta scelta
            opponent_card = self.opponent_cards[
                self.selected_opponent_card
            ]

            # inserisco la carta nella casella scelta
            card_placed = self.board.place_card(
                opponent_card,
                "opponent",
                self.opponent_target_row,
                self.opponent_target_column
            )

            # continuo soltanto se il piazzamento è riuscito
            if card_placed:

                # confronto la carta avversaria appena piazzata
                # con tutte le carte del giocatore adiacenti
                capture_started = self.resolve_basic_captures(
                    self.opponent_target_row,
                    self.opponent_target_column
                )

                # segno lo slot avversario come utilizzato
                self.played_opponent_card_indices.add(
                    self.selected_opponent_card
                )

                # controllo anche il caso futuro nel quale
                # sia l'avversario a riempire l'ultima casella
                if self.check_match_finished():
                    return

                # termino l'animazione dell'avversario
                self.opponent_turn_phase = None

                # pulisco carta e posizione temporanee
                self.selected_opponent_card = None
                self.opponent_target_row = None
                self.opponent_target_column = None

                # sposto la selezione sulla prima carta
                # del giocatore ancora disponibile
                self.move_player_card_selection(1)

                # se l'avversario ha catturato delle carte,
                # attendo il completamento del loro flip
                if capture_started:
                    self.input_mode = "waiting_for_turn_transition"
                    self.pending_turn_owner = "player"

                # senza catture posso iniziare immediatamente
                # il trasferimento verso il giocatore
                else:
                    self.start_turn_indicator_transition(
                        "player"
                    )

    # disegna nella parte bassa dello schermo
    # il pannello con il nome della carta indicata
    def draw_card_name_panel(
        self,
        screen,
        card_name
    ):

        # centro il pannello orizzontalmente
        # lasciando un piccolo margine inferiore
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

        # disegno lo sfondo del pannello
        pygame.draw.rect(
            screen,
            self.card_name_panel_color,
            panel_rect
        )

        # disegno il bordo bianco
        pygame.draw.rect(
            screen,
            self.card_name_panel_border_color,
            panel_rect,
            2
        )

        # preparo il nome della carta
        card_name_surface = (
            self.card_name_panel_font.render(
                card_name,
                True,
                (255, 255, 255)
            )
        )

        # centro il testo nel pannello
        card_name_rect = card_name_surface.get_rect(
            center=panel_rect.center
        )

        # disegno il nome
        screen.blit(
            card_name_surface,
            card_name_rect
        )

    # disegna la schermata della partita
    def draw(self, screen):

        # disegno lo sfondo che contiene
        # il tabellone centrale 3x3
        screen.blit(
            self.background_image,
            (0, 0)
        )

        # disegno una griglia di controllo sopra lo sfondo
        # soltanto quando il relativo debug è attivo
        if DEBUG_DRAW_MATCH_GRID:

            # coordinate esatte del tabellone centrale
            board_x = 400
            board_y = 57

            # dimensioni di ogni casella
            cell_width = 160
            cell_height = 202

            # creo e disegno le nove caselle
            for row in range(3):
                for column in range(3):

                    cell_rect = pygame.Rect(
                        board_x + column * cell_width,
                        board_y + row * cell_height,
                        cell_width,
                        cell_height
                    )

                    # bordo rosso usato per verificare
                    # la corrispondenza con lo sfondo
                    pygame.draw.rect(
                        screen,
                        (255, 0, 0),
                        cell_rect,
                        3
                    )

        # disegno le carte presenti nelle nove caselle
        for row in range(3):
            for column in range(3):

                cell = self.board.get_cell(
                    row,
                    column
                )

                # ignoro le caselle ancora vuote
                if cell is None:
                    continue

                placed_card = cell["card"]
                owner = cell["owner"]

                # creo una chiave composta da carta e proprietario;
                # il proprietario determina il colore dello sfondo
                surface_key = (
                    placed_card.card_id,
                    owner
                )

                # costruisco la superficie soltanto la prima volta
                if surface_key not in self.board_card_surfaces:

                    if owner == "player":
                        background_color = "blue"
                    else:
                        background_color = "red"

                    board_card_surface = render_card(
                        placed_card,
                        background_color
                    )

                    board_card_surface = pygame.transform.smoothscale(
                        board_card_surface,
                        self.match_card_size
                    )

                    self.board_card_surfaces[
                        surface_key
                    ] = board_card_surface

                # recupero la superficie dalla cache
                board_card_surface = self.board_card_surfaces[
                    surface_key
                ]

                # normalmente disegno il fronte della carta
                surface_to_draw = board_card_surface

                # normalmente la carta mantiene la larghezza completa
                animated_width = self.match_card_size[0]

                # controllo se questa carta appartiene
                # al gruppo che sta flippando
                card_is_flipping = (
                    (row, column)
                    in self.flipping_card_positions
                )

                if (
                    card_is_flipping
                    and self.flip_phase is not None
                ):

                    # calcolo l'avanzamento della fase corrente
                    flip_progress = (
                        pygame.time.get_ticks()
                        - self.flip_phase_start_time
                    ) / self.flip_phase_duration

                    # impedisco al valore di uscire
                    # dall'intervallo compreso tra 0 e 1
                    flip_progress = max(
                        0.0,
                        min(1.0, flip_progress)
                    )

                    # il vecchio fronte si restringe
                    if self.flip_phase == "front_shrinking":
                        animated_width = int(
                            self.match_card_size[0]
                            * (1.0 - flip_progress)
                        )

                    # il retro compare e si allarga
                    elif self.flip_phase == "back_expanding":
                        surface_to_draw = (
                            self.board_card_back_surface
                        )

                        animated_width = int(
                            self.match_card_size[0]
                            * flip_progress
                        )

                    # il retro si restringe nuovamente
                    elif self.flip_phase == "back_shrinking":
                        surface_to_draw = (
                            self.board_card_back_surface
                        )

                        animated_width = int(
                            self.match_card_size[0]
                            * (1.0 - flip_progress)
                        )

                    # il nuovo fronte colorato si allarga
                    elif self.flip_phase == "front_expanding":
                        animated_width = int(
                            self.match_card_size[0]
                            * flip_progress
                        )

                    # mantengo almeno un pixel di larghezza
                    # per evitare una superficie non valida
                    animated_width = max(
                        1,
                        animated_width
                    )

                    # ridimensiono soltanto la larghezza;
                    # l'altezza rimane sempre invariata
                    surface_to_draw = pygame.transform.smoothscale(
                        surface_to_draw,
                        (
                            animated_width,
                            self.match_card_size[1]
                        )
                    )

                # mantengo la carta centrata nella casella
                # anche durante il restringimento orizzontale
                board_card_rect = surface_to_draw.get_rect(
                    center=self.board_cell_rects[
                        row
                    ][
                        column
                    ].center
                )

                # disegno il fronte normale oppure
                # la fase corrente dell'animazione
                screen.blit(
                    surface_to_draw,
                    board_card_rect
                )

        # posizione iniziale della mano del giocatore
        player_hand_x = 100
        player_hand_y = 35

        # distanza verticale ridotta per lasciare
        # spazio libero sotto la mano del giocatore
        player_card_offset = 115

        # ricreo i rettangoli delle carte
        self.player_card_rects = []

        # rettangoli fissi usati solamente per il mouse;
        # non si spostano insieme alla carta selezionata
        self.player_card_hover_rects = []

        # disegno le cinque carte sovrapposte verticalmente
        for i, card_surface in enumerate(
            self.player_card_surfaces
        ):

            # creo un rettangolo fisso nella posizione originale;
            # questo rettangolo non segue lo spostamento laterale
            hover_rect = pygame.Rect(
                player_hand_x,
                player_hand_y + i * player_card_offset,
                self.match_card_size[0],
                self.match_card_size[1]
            )

            self.player_card_hover_rects.append(
                hover_rect
            )

            # posizione orizzontale normale della carta
            card_x = player_hand_x

            # la carta indicata dalla manina
            # si sposta leggermente verso il tabellone
            if i == self.selected_player_card:
                card_x += 35

            card_rect = card_surface.get_rect(
                topleft=(
                    card_x,
                    player_hand_y
                    + i * player_card_offset
                )
            )

            # salvo il rettangolo per i futuri controlli
            self.player_card_rects.append(
                card_rect
            )

            # disegno soltanto le carte
            # che non sono ancora state giocate
            if i not in self.played_player_card_indices:
                screen.blit(
                    card_surface,
                    card_rect
                )

        # nella modalità hand la manina
        # indica la carta selezionata
        if (
            self.input_mode == "hand"
            and self.player_card_rects
        ):

            selected_player_card_rect = (
                self.player_card_rects[
                    self.selected_player_card
                ]
            )

            self.hand_cursor.draw(
                screen,
                selected_player_card_rect,
                gap=35
            )

        # nella modalità board la punta della manina
        # indica il centro della casella selezionata
        elif self.input_mode == "board":

            selected_cell_rect = self.board_cell_rects[
                self.selected_board_row
            ][
                self.selected_board_column
            ]

            self.hand_cursor.draw_at_point(
                screen,
                selected_cell_rect.center
            )

        # posizione iniziale della mano dell'avversario,
        # simmetrica rispetto a quella del giocatore
        opponent_hand_x = (
            self.width
            - player_hand_x
            - self.match_card_size[0]
        )

        opponent_hand_y = player_hand_y

        # ricreo i rettangoli delle carte avversarie
        self.opponent_card_rects = []

        # disegno le cinque carte sovrapposte verticalmente
        for i, card_surface in enumerate(
            self.opponent_card_surfaces
        ):

            # posizione orizzontale normale della carta avversaria
            card_x = opponent_hand_x

            # durante la scelta, la carta indicata
            # avanza di 35 pixel verso il tabellone
            if (
                self.opponent_turn_phase == "showing_selection"
                and i == self.selected_opponent_card
            ):
                card_x -= 35

            card_rect = card_surface.get_rect(
                topleft=(
                    card_x,
                    opponent_hand_y
                    + i * player_card_offset
                )
            )

            # salvo il rettangolo per i futuri controlli
            self.opponent_card_rects.append(
                card_rect
            )

            # disegno soltanto le carte avversarie
            # che non sono ancora state giocate
            if i not in self.played_opponent_card_indices:
                screen.blit(
                    card_surface,
                    card_rect
                )

        # nome da mostrare nel pannello descrittivo;
        # None significa che il pannello resta nascosto
        displayed_card_name = None

        # quando il giocatore sta scegliendo dalla propria mano,
        # mostro la carta spostata lateralmente
        if (
            self.input_mode == "hand"
            and self.player_cards
            and self.selected_player_card
            not in self.played_player_card_indices
        ):

            selected_player_card = self.player_cards[
                self.selected_player_card
            ]

            displayed_card_name = (
                selected_player_card.name
            )

        # durante i primi 500 ms visibili del turno avversario,
        # mostro il nome della carta spostata lateralmente
        elif (
            self.input_mode == "opponent_turn"
            and self.opponent_turn_phase
            == "showing_selection"
            and self.selected_opponent_card is not None
            and self.opponent_cards_face_up
        ):

            selected_opponent_card = self.opponent_cards[
                self.selected_opponent_card
            ]

            displayed_card_name = (
                selected_opponent_card.name
            )

        # quando la manina si trova sul tabellone,
        # mostro il nome soltanto se la casella è occupata
        elif self.input_mode == "board":

            indicated_board_cell = self.board.get_cell(
                self.selected_board_row,
                self.selected_board_column
            )

            if indicated_board_cell is not None:
                displayed_card_name = (
                    indicated_board_cell["card"].name
                )

        # disegno il pannello soltanto quando
        # esiste realmente un nome da mostrare
        if displayed_card_name is not None:
            self.draw_card_name_panel(
                screen,
                displayed_card_name
            )

        # recupero il numero azzurro del giocatore
        player_score_surface = (
            self.player_score_number_surfaces[
                self.player_score
            ]
        )

        # recupero il numero rosso dell'avversario
        opponent_score_surface = (
            self.opponent_score_number_surfaces[
                self.opponent_score
            ]
        )

        # centro il punteggio sotto la colonna del giocatore;
        # il numero può sovrapporsi leggermente all'ultima carta
        player_score_rect = player_score_surface.get_rect(
            center=(
                175,
                675
            )
        )

        # centro il punteggio sotto la futura
        # colonna delle carte dell'avversario
        opponent_score_rect = opponent_score_surface.get_rect(
            center=(
                1105,
                675
            )
        )

        # disegno i due punteggi
        screen.blit(
            player_score_surface,
            player_score_rect
        )

        screen.blit(
            opponent_score_surface,
            opponent_score_rect
        )

        # mostro il risultato soltanto quando
        # la partita è realmente terminata
        if (
            self.match_result is not None
            and self.result_fade_start_time is not None
        ):

            # calcolo quanto tempo è trascorso
            # dall'inizio del fade-in
            fade_elapsed_time = (
                pygame.time.get_ticks()
                - self.result_fade_start_time
            )

            # calcolo l'avanzamento da 0.0 a 1.0
            fade_progress = (
                fade_elapsed_time
                / self.result_fade_duration
            )

            fade_progress = max(
                0.0,
                min(1.0, fade_progress)
            )

            # converto l'avanzamento nell'alpha di Pygame:
            # 0 è invisibile, 255 è completamente visibile
            result_alpha = int(
                255 * fade_progress
            )

            # uso una copia per non modificare
            # permanentemente l'immagine originale
            result_surface = self.result_surfaces[
                self.match_result
            ].copy()

            result_surface.set_alpha(
                result_alpha
            )

            # centro l'immagine sopra il tabellone
            result_rect = result_surface.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2
                )
            )

            # disegno il risultato con l'opacità corrente
            screen.blit(
                result_surface,
                result_rect
            )

        # mostro il PNG della regola
        # attualmente in fase di risoluzione
        if self.active_rule_effect is not None:

            active_rule_name = (
                self.active_rule_effect["name"]
            )

            active_rule_surface = (
                self.rule_effect_surfaces[
                    active_rule_name
                ]
            )

            active_rule_rect = active_rule_surface.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2
                )
            )

            screen.blit(
                active_rule_surface,
                active_rule_rect
            )
            
        # durante la selezione del primo turno,
        # disegno la freccia al centro dello schermo
        if (
            self.input_mode == "starting_turn_animation"
            and self.turn_arrow_phase is not None
        ):

            # normalmente la freccia mantiene
            # la propria larghezza completa
            animated_arrow_width = (
                self.turn_arrow_size[0]
            )

            # shrinking ed expanding usano
            # l'avanzamento della fase corrente
            if self.turn_arrow_phase in (
                "shrinking",
                "expanding"
            ):

                arrow_progress = (
                    pygame.time.get_ticks()
                    - self.turn_arrow_phase_start_time
                ) / self.turn_arrow_phase_duration

                arrow_progress = max(
                    0.0,
                    min(1.0, arrow_progress)
                )

                # la freccia si restringe
                # mantenendo invariata l'altezza
                if self.turn_arrow_phase == "shrinking":
                    animated_arrow_width = int(
                        self.turn_arrow_size[0]
                        * (1.0 - arrow_progress)
                    )

                # dopo aver cambiato direzione,
                # la nuova freccia si riallarga
                else:
                    animated_arrow_width = int(
                        self.turn_arrow_size[0]
                        * arrow_progress
                    )

            # evito superfici larghe zero pixel
            animated_arrow_width = max(
                1,
                animated_arrow_width
            )

            # recupero la freccia orientata
            # nella direzione corrente
            turn_arrow_surface = self.turn_arrow_surfaces[
                self.turn_arrow_direction
            ]

            # ridimensiono soltanto la larghezza
            turn_arrow_surface = pygame.transform.smoothscale(
                turn_arrow_surface,
                (
                    animated_arrow_width,
                    self.turn_arrow_size[1]
                )
            )

            # mantengo la freccia centrata
            # durante tutta la rotazione
            turn_arrow_rect = turn_arrow_surface.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2
                )
            )

            screen.blit(
                turn_arrow_surface,
                turn_arrow_rect
            )

        # dopo la scelta iniziale mostro un triangolo
        # sopra la mano del giocatore che possiede il turno
        if self.active_turn_owner is not None:

            # recupero il tempo per creare
            # una pulsazione continua e regolare
            elapsed_time = (
                pygame.time.get_ticks() / 1000.0
            )

            # la larghezza oscilla dal 100% al 50%;
            # l'altezza rimane sempre invariata
            width_factor = (
                0.75
                + 0.25 * math.cos(
                    elapsed_time
                    * self.active_turn_indicator_speed
                )
            )

            animated_indicator_width = max(
                1,
                int(
                    self.active_turn_indicator_size[0]
                    * width_factor
                )
            )

            # recupero il triangolo rivolto verso il basso
            active_turn_surface = self.turn_arrow_surfaces[
                "down"
            ]

            # applico soltanto lo shrink orizzontale
            active_turn_surface = pygame.transform.smoothscale(
                active_turn_surface,
                (
                    animated_indicator_width,
                    self.active_turn_indicator_size[1]
                )
            )

            # normalmente l'indicatore rimane sopra
            # la mano del proprietario attuale
            indicator_owner = self.active_turn_owner
            indicator_y = self.turn_indicator_rest_y

            # durante la salita mantengo il vecchio lato
            if self.turn_indicator_transition_phase == "leaving":

                transition_progress = (
                    pygame.time.get_ticks()
                    - self.turn_indicator_transition_start_time
                ) / self.turn_indicator_leave_duration

                transition_progress = max(
                    0.0,
                    min(1.0, transition_progress)
                )

                indicator_y = int(
                    self.turn_indicator_rest_y
                    + (
                        self.turn_indicator_hidden_y
                        - self.turn_indicator_rest_y
                    ) * transition_progress
                )

            # durante la pausa rimane fuori dallo schermo
            elif self.turn_indicator_transition_phase == "waiting":
                indicator_y = self.turn_indicator_hidden_y

            # durante la discesa utilizzo già il nuovo lato
            elif self.turn_indicator_transition_phase == "entering":

                indicator_owner = self.pending_turn_owner

                transition_progress = (
                    pygame.time.get_ticks()
                    - self.turn_indicator_transition_start_time
                ) / self.turn_indicator_enter_duration

                transition_progress = max(
                    0.0,
                    min(1.0, transition_progress)
                )

                indicator_y = int(
                    self.turn_indicator_hidden_y
                    + (
                        self.turn_indicator_rest_y
                        - self.turn_indicator_hidden_y
                    ) * transition_progress
                )

            # scelgo il centro della colonna corretta
            if indicator_owner == "player":
                indicator_x = 175
            else:
                indicator_x = 1105

            # posiziono l'indicatore mantenendo attiva
            # anche la pulsazione orizzontale
            active_turn_rect = active_turn_surface.get_rect(
                center=(
                    indicator_x,
                    indicator_y
                )
            )

            screen.blit(
                active_turn_surface,
                active_turn_rect
            )