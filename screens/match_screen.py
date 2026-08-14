import pygame
import random

from screens.screen import Screen
from game.board import Board

from config import (
    ACTIVE_CARD_SETS,
    CARD_BACK_PATH,
    DEBUG_DRAW_MATCH_GRID
)

# funzione che costruisce graficamente le carte
from renderers.card_renderer import render_card
from ui.animated_hand_cursor import AnimatedHandCursor
from game.card_loader import load_cards

# schermata che gestisce una partita di Triple Triad
class MatchScreen(Screen):

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

        # conservo una copia delle cinque carte
        # selezionate dal giocatore
        self.player_cards = list(
            player_cards
        )

        # carico tutte le carte appartenenti
        # ai set attivi della versione corrente
        available_opponent_cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # per ora l'avversario può utilizzare
        # soltanto carte di rarità 1
        rarity_one_cards = [
            card
            for card in available_opponent_cards
            if card.rarity == 1
        ]

        # verifico che esistano almeno cinque carte utilizzabili
        if len(rarity_one_cards) < 5:
            raise ValueError(
                "Not enough rarity 1 cards "
                "to generate the opponent hand"
            )

        # scelgo cinque carte differenti in modo casuale
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

        # controllo se le carte avversarie devono essere visibili
        opponent_cards_face_up = (
            match_rules["cards"] == "Face Up"
        )

        # se le carte sono coperte, carico il retro una sola volta
        if not opponent_cards_face_up:

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
            if opponent_cards_face_up:
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
        self.opponent_phase_duration = 500

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

        # manina animata usata durante la partita
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # modalità attuale dei controlli:
        # hand seleziona una carta, board seleziona una casella
        self.input_mode = "hand"

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

        # segno lo slot come utilizzato senza rimuoverlo;
        # le altre carte mantengono così la loro posizione
        self.played_player_card_indices.add(
            self.selected_player_card
        )

        # passo al turno dell'avversario
        self.input_mode = "opponent_turn"

        # inizialmente attendo mezzo secondo
        # prima di mostrare la carta scelta
        self.opponent_turn_phase = "waiting_to_select"

        # salvo il momento di inizio della fase
        self.opponent_phase_start_time = (
            pygame.time.get_ticks()
        )

    # gestisce gli eventi della partita
    def handle_events(self, event):

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

                # seleziono la carta precedente
                if (
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

    # aggiorna la logica della partita
    def update(self):

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

                # segno lo slot avversario come utilizzato
                self.played_opponent_card_indices.add(
                    self.selected_opponent_card
                )

                # termino l'animazione dell'avversario
                self.opponent_turn_phase = None

                # pulisco carta e posizione temporanee
                self.selected_opponent_card = None
                self.opponent_target_row = None
                self.opponent_target_column = None

                # torno alla selezione della mano del giocatore
                self.input_mode = "hand"

                # la carta giocata dal giocatore non è più selezionabile;
                # sposto la selezione sulla prima carta disponibile successiva
                self.move_player_card_selection(1)   

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

                # centro la carta nella relativa casella
                board_card_rect = board_card_surface.get_rect(
                    center=self.board_cell_rects[
                        row
                    ][
                        column
                    ].center
                )

                screen.blit(
                    board_card_surface,
                    board_card_rect
                )

        # posizione iniziale della mano del giocatore
        player_hand_x = 100
        player_hand_y = 10

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