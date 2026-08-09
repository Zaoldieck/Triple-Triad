import pygame
from panels.panel import Panel
#funzione che carica le carte dal file JSON
from game.card_loader import load_cards
# funzione che costruisce graficamente una carta
from renderers.card_renderer import render_card
# set di carte abilitati nella versione corrente
from config import ACTIVE_CARD_SETS

class DeckPanel(Panel):

    def __init__(self, width, height, state):

        self.width = width
        self.height = height
        self.state = state

        # dimensioni del pannello
        self.panel_width = 900
        self.panel_height = 550

        # dimensioni iniziali per l'animazione
        self.current_width = 0
        self.current_height = 0

        # velocita apertura pannello (animazione)
        self.open_speed = 3

        # indica se il pannello e' ancora in apertura
        self.opening = True

        # colore pannello
        self.color = (100, 100, 100)

        # font 
        self.font = pygame.font.SysFont("Arial", 40)

        # font piu piccolo per info del deck
        self.info_font = pygame.font.SysFont("Arial", 24)

        # carico l'immagine del cursore
        self.hand_cursor = pygame.image.load(
            "assets/images/hand_cursor.png"
        ).convert_alpha()

        # ridimensiono il cursore manina
        self.hand_cursor = pygame.transform.smoothscale(self.hand_cursor, (64,64))

        # indice dello slot attualmente selezionato
        self.selected_card = 0

        # dato che ci sono piu pagine di carte
        self.current_page = 0

        # numero carte per pagina
        self.cards_per_page = 10

        # carico soltanto le carte appartenenti ai set abilitati
        self.cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # superficie che conterrà l'anteprima della carta
        self.card_preview = None

        # superficie che conterrà l'anteprima della carta selezionata
        self.card_preview = None

        # indice della carta attualmente mostrata nell'anteprima
        self.previewed_card_index = None

        # lista che contiene i rettangoli dei 10 slot delle carte
        self.slot_rects = []


    # aggiorna l'anteprima quando cambia la carta selezionata  
    def update_card_preview(self):

        # calcolo l'indice della carta nell'intero catalogo
        card_index = (
            self.current_page * self.cards_per_page
            + self.selected_card
        )

        # se lo slot selezionato è vuoto, rimuovo l'anteprima
        if card_index >= len(self.cards):
            self.card_preview = None
            self.previewed_card_index = None
            return

        # evito di ricostruire la stessa carta a ogni frame
        if card_index == self.previewed_card_index:
            return

        # recupero la carta selezionata
        selected_card = self.cards[card_index]

        # costruisco la carta usando lo sfondo blu
        self.card_preview = render_card(
            selected_card,
            "blue"
        )

        # ridimensiono l'anteprima mantenendo le proporzioni
        self.card_preview = pygame.transform.smoothscale(
            self.card_preview,
            (280, 354)
        )

        # salvo l'indice della carta mostrata
        self.previewed_card_index = card_index



    def handle_events(self, event):

        # calcolo quante carte sono presenti nella pagina corrente
        start_index = self.current_page * self.cards_per_page

        cards_on_page = max(
            0,
            min(
                self.cards_per_page,
                len(self.cards) - start_index
            )
        )



        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

            # sposto la selezione soltanto tra gli slot contenenti carte (quindi non sugli slot vuoti)
            elif event.key == pygame.K_UP and cards_on_page > 0:
                self.selected_card = (
                    self.selected_card - 1
                ) % cards_on_page

            elif event.key == pygame.K_DOWN and cards_on_page > 0:
                self.selected_card = (
                    self.selected_card + 1
                ) % cards_on_page


            # pagina sinistra e destra del pannello deck
            elif event.key == pygame.K_LEFT:
                self.current_page = (self.current_page - 1) % self.total_pages

            elif event.key == pygame.K_RIGHT:
                self.current_page = (self.current_page + 1) % self.total_pages

        # evento rotella del mouse
        if event.type == pygame.MOUSEWHEEL:

            # rotella verso l'alto 
            if event.y > 0:
                self.current_page = (
                    self.current_page - 1
                ) % self.total_pages

            # rotella verso il basso 
            if event.y < 0:
                self.current_page = (
                    self.current_page + 1
                ) % self.total_pages

        # se il mouse si muove
        if event.type == pygame.MOUSEMOTION:

            # controllo tutti i rettangoli degli slot
            for i, slot_rect in enumerate(self.slot_rects):

                # seleziono lo slot soltanto se contiene una carta
                if (
                    i < cards_on_page
                    and slot_rect.collidepoint(event.pos)
                ):
                    self.selected_card = i

    # logica del pannello                
    def update(self):

        # aggiorno l'anteprima della carta selezionata
        self.update_card_preview()

        if self.opening:

            self.current_width += self.open_speed
            self.current_height += self.open_speed

            # quando raggiunge la dimensione finale ferma l'animazione!
            if self.current_width >= self.panel_width:
                self.current_width = self.panel_width

            if self.current_height >= self.panel_height:
                self.current_height = self.panel_height

            if self.current_width == self.panel_width and self.current_height == self.panel_height:
                self.opening = False            

    # disegna il pannello
    def draw(self, screen):

        #posizione del pannello sullo schermo
        x = (self.width - self.current_width) // 2
        y = (self.height - self.current_height) // 2

        #creo il rettangolo del pannello
        panel_rect = pygame.Rect(x, y, self.current_width, self.current_height)

        #disegno il pannello
        pygame.draw.rect(screen, self.color, panel_rect)

        # area che conterra' la lista delle carte
        list_rect = pygame.Rect(
            x + 30,
            y + 30,
            400,
            self.current_height - 60
        )
        # area per la lista delle carte, disegna
        pygame.draw.rect(screen, (70, 70, 70), list_rect)

        # creo i 10 spazi per le carte della pagina
        slot_height = 42
        slot_spacing = 5

        # svuoto la lista prima di ricreare i rettangoli degli slot
        self.slot_rects = []

        # calcolo l'indice della prima carta della pagina corrente
        start_index = self.current_page * self.cards_per_page

        # estraggo solamente le carte appartenenti alla pagina corrente
        page_cards = self.cards[
            start_index:start_index + self.cards_per_page
        ]

        for i in range(10):
            slot_rect = pygame.Rect(
                list_rect.x + 10,
                list_rect.y + 10 + i * (slot_height + slot_spacing),
                list_rect.width - 20,
                slot_height
            )

            self.slot_rects.append(slot_rect)

            pygame.draw.rect(screen, (50,50,50), slot_rect)


            # se nello slot è presente una carta, ne mostro il nome
            if i < len(page_cards):

                card_name = self.info_font.render(
                    page_cards[i].name,
                    True,
                    (255, 255, 255)
                )

                # posiziono il nome all'interno dello slot
                card_name_rect = card_name.get_rect(
                    midleft=(slot_rect.x + 15, slot_rect.centery)
                )

                # disegno il nome della carta
                screen.blit(card_name, card_name_rect)



            # disegno la manina accanto allo slot selezionato
            if i == self.selected_card:
                hand_rect = self.hand_cursor.get_rect()
                hand_rect.centery = slot_rect.centery
                hand_rect.right = slot_rect.left - 5

                screen.blit(self.hand_cursor, hand_rect)

        #preparo il testo con il numero della pagina corrente
        page_text = self.info_font.render(
            f"Page {self.current_page + 1} / {self.total_pages}",
            True,
            (255, 255, 255)
        )

        #posiziono il numero della pagina nella parte destra del pannello
        page_text_rect = page_text.get_rect(
            center=(x + 665, y + 30)
        )

        #disegno il numero sulla pagina
        screen.blit(page_text,page_text_rect)

        # disegno l'anteprima della carta nella parte destra del pannello
        if self.card_preview is not None:

            # centro l'anteprima nella parte destra
            preview_rect = self.card_preview.get_rect(
                center=(x + 665, y + 300)
            )

            # disegno la carta completa
            screen.blit(self.card_preview, preview_rect)               

    @property
    def total_pages(self):

        #calcolo il numero di pagine in base alle carte caricate
        pages = (
            len(self.cards) + self.cards_per_page - 1
        ) // self.cards_per_page

        # mostra comunque almeno una apgina anche se non ci sono carte
        return max(1, pages)