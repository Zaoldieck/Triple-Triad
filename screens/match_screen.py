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

        # rettangoli delle carte del giocatore;
        # serviranno successivamente per mouse e selezione
        self.player_card_rects = []

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

    # gestisce gli eventi della partita
    def handle_events(self, event):
        pass

    # aggiorna la logica della partita
    def update(self):
        pass

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

        # posizione iniziale della mano del giocatore
        player_hand_x = 100
        player_hand_y = 10

        # distanza verticale ridotta per lasciare
        # spazio libero sotto la mano del giocatore
        player_card_offset = 115

        # ricreo i rettangoli delle carte
        self.player_card_rects = []

        # disegno le cinque carte sovrapposte verticalmente
        for i, card_surface in enumerate(
            self.player_card_surfaces
        ):

            card_rect = card_surface.get_rect(
                topleft=(
                    player_hand_x,
                    player_hand_y
                    + i * player_card_offset
                )
            )

            # salvo il rettangolo per i futuri controlli
            self.player_card_rects.append(
                card_rect
            )

            # le carte successive vengono disegnate sopra
            # la parte inferiore delle precedenti
            screen.blit(
                card_surface,
                card_rect
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

            card_rect = card_surface.get_rect(
                topleft=(
                    opponent_hand_x,
                    opponent_hand_y
                    + i * player_card_offset
                )
            )

            # salvo il rettangolo per i futuri controlli
            self.opponent_card_rects.append(
                card_rect
            )

            # le carte successive coprono parzialmente
            # quelle disegnate precedentemente
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