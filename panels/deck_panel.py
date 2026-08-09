import pygame
from panels.panel import Panel
#funzione che carica le carte dal file JSON
from game.card_loader import load_cards
# funzione che costruisce graficamente una carta
from renderers.card_renderer import render_card
# set di carte abilitati nella versione corrente (e sfondo carta relativo)
from config import ACTIVE_CARD_SETS, CARD_BACK_PATH, DEBUG_REVEAL_ALL_CARDS
# cursore animato riutilizzabile
from ui.animated_hand_cursor import AnimatedHandCursor


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

        # creo la manina animata del Deck
        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # carico l'immagine del retro della carta
        self.card_back = pygame.image.load(
            CARD_BACK_PATH
        ).convert_alpha()

        # ridimensiono il retro come l'anteprima delle carte
        self.card_back = pygame.transform.smoothscale(
            self.card_back,
            (280, 354)
        )

        # indice dello slot attualmente selezionato
        self.selected_card = 0

        # dato che ci sono piu pagine di carte
        self.current_page = 0

        # VARIABILI PER ANIMAZIONE CAMBIO PAGINA

        # indica se è in corso l'animazione del cambio pagina
        self.page_animating = False

        # fase dell'animazione: uscita oppure entrata
        self.page_animation_phase = None

        # direzione dell'animazione: -1 sinistra, 1 destra
        self.page_animation_direction = 0

        # spostamento orizzontale applicato ai contenuti
        self.page_animation_offset = 0.0

        # pagina che verrà mostrata al termine dell'animazione
        self.target_page = 0

        # velocità dello scorrimento orizzontale
        self.page_animation_speed = 6

        # numero carte per pagina
        self.cards_per_page = 11

        # carico soltanto le carte appartenenti ai set abilitati
        self.cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # superficie che conterrà l'anteprima della carta selezionata
        self.card_preview = None

        # identifica la carta e lo stato mostrati nell'anteprima
        self.previewed_card_key = None

        # lista che contiene i rettangoli degli slot delle carte
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
            self.previewed_card_key = None
            return

        # recupero la carta selezionata
        selected_card = self.cards[card_index]

        # durante lo sviluppo posso mostrare tutte le anteprime
        is_discovered = (
            DEBUG_REVEAL_ALL_CARDS
            or self.state.card_collection.is_discovered(
                selected_card
            )
        )

        quantity = self.state.card_collection.get_quantity(
            selected_card
        )

        # determino lo stato grafico dell'anteprima
        if not is_discovered:
            preview_state = "hidden"

        elif quantity == 0 and not DEBUG_REVEAL_ALL_CARDS:
            preview_state = "discovered_empty"

        else:
            preview_state = "owned"

        # creo una chiave composta da carta selezionata e stato grafico
        preview_key = (
            card_index,
            preview_state
        )

        # evito di ricostruire la stessa anteprima a ogni frame
        if preview_key == self.previewed_card_key:
            return

        # una carta mai scoperta mostra soltanto il retro
        if preview_state == "hidden":
            self.card_preview = self.card_back

        # una carta scoperta mostra il proprio fronte
        else:
            self.card_preview = render_card(
                selected_card,
                "blue"
            )

            # se la quantità è zero, trasformo la carta in bianco e nero
            if preview_state == "discovered_empty":
                self.card_preview = pygame.transform.grayscale(
                    self.card_preview
                )

            # ridimensiono l'anteprima mantenendo le proporzioni
            self.card_preview = pygame.transform.smoothscale(
                self.card_preview,
                (280, 354)
            )

        # salvo la carta e lo stato mostrati
        self.previewed_card_key = preview_key

    # avvia il cambio pagina nella direzione richiesta
    def change_page(self, direction):

        # ignoro nuovi cambi mentre l'animazione è in corso
        if self.page_animating:
            return

        # evito il cambio se esiste una sola pagina
        if self.total_pages <= 1:
            return

        # calcolo la pagina che dovrà entrare
        self.target_page = (
            self.current_page + direction
        ) % self.total_pages

        # salvo la direzione richiesta
        self.page_animation_direction = direction

        # l'animazione comincia facendo uscire la pagina attuale
        self.page_animation_phase = "out"
        self.page_animation_offset = 0.0
        self.page_animating = True

    # aggiorna lo scorrimento orizzontale delle righe
    def update_page_animation(self):

        # non faccio nulla se non è in corso un'animazione
        if not self.page_animating:
            return

        # larghezza da percorrere per uscire dall'area della lista
        animation_distance = 400

        # sposto le righe nella direzione dell'animazione
        self.page_animation_offset -= (
            self.page_animation_direction
            * self.page_animation_speed
        )

        # la pagina attuale ha terminato l'uscita
        if (
            self.page_animation_phase == "out"
            and abs(self.page_animation_offset) >= animation_distance
        ):

            # applico la nuova pagina
            self.current_page = self.target_page

            # seleziono la prima carta della nuova pagina
            self.selected_card = 0

            # faccio partire la nuova pagina dal lato opposto
            self.page_animation_offset = (
                self.page_animation_direction
                * animation_distance
            )

            # comincia la fase di entrata
            self.page_animation_phase = "in"

        # la nuova pagina ha raggiunto la posizione centrale
        elif self.page_animation_phase == "in":

            reached_center = (
                self.page_animation_direction == 1
                and self.page_animation_offset <= 0
            ) or (
                self.page_animation_direction == -1
                and self.page_animation_offset >= 0
            )

            if reached_center:

                # termino l'animazione
                self.page_animation_offset = 0.0
                self.page_animating = False
                self.page_animation_phase = None
                self.page_animation_direction = 0

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
            elif (
                event.key == pygame.K_UP
                and cards_on_page > 0
                and not self.page_animating
            ):
                self.selected_card = (
                    self.selected_card - 1
                ) % cards_on_page

            elif (
                event.key == pygame.K_DOWN
                and cards_on_page > 0
                and not self.page_animating
            ):
                self.selected_card = (
                    self.selected_card + 1
                ) % cards_on_page


            # pagina precedente
            elif event.key == pygame.K_LEFT:
                self.change_page(-1)

            # pagina successiva
            elif event.key == pygame.K_RIGHT:
                self.change_page(1)

        # cambio pagina con la rotella del mouse
        if event.type == pygame.MOUSEWHEEL:

            # rotella verso l'alto: pagina precedente
            if event.y > 0:
                self.change_page(-1)

            # rotella verso il basso: pagina successiva
            elif event.y < 0:
                self.change_page(1)

        # ignoro l'hover mentre le righe stanno scorrendo
        if (
            event.type == pygame.MOUSEMOTION
            and not self.page_animating
        ):
            
            # controllo tutti i rettangoli degli slot
            for i, slot_rect in enumerate(self.slot_rects):

                # seleziono lo slot soltanto se contiene una carta
                if (
                    i < cards_on_page
                    and slot_rect.collidepoint(event.pos)
                ):
                    self.selected_card = i

        if event.type == pygame.MOUSEBUTTONDOWN:

            # tasto destro del mouse
            if event.button == 3:
                self.state.close_panel()

    # logica del pannello                
    def update(self):

        # aggiorno l'animazione del cambio pagina
        self.update_page_animation()

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

        # creo i 11 spazi per le carte della pagina
        slot_height = 39
        slot_spacing = 4

        # svuoto la lista prima di ricreare i rettangoli degli slot
        self.slot_rects = []

        # calcolo l'indice della prima carta della pagina corrente
        start_index = self.current_page * self.cards_per_page

        # estraggo solamente le carte appartenenti alla pagina corrente
        page_cards = self.cards[
            start_index:start_index + self.cards_per_page
        ]

        # converto l'offset dell'animazione in pixel interi
        row_offset = int(self.page_animation_offset)

        # salvo l'area di disegno attuale
        previous_clip = screen.get_clip()

        # impedisco alle righe animate di uscire dall'area della lista
        screen.set_clip(list_rect)

        # creo uno slot per ogni carta prevista nella pagina
        for i in range(self.cards_per_page):
            slot_rect = pygame.Rect(
                list_rect.x + 10,
                list_rect.y + 10 + i * (slot_height + slot_spacing),
                list_rect.width - 20,
                slot_height
            )

            self.slot_rects.append(slot_rect)

            # creo una copia dello slot spostata dall'animazione
            draw_slot_rect = slot_rect.move(
                row_offset,
                0
            )

            # disegno lo slot nella posizione animata
            pygame.draw.rect(
                screen,
                (50, 50, 50),
                draw_slot_rect
            )


            # se nello slot è presente una carta, mostro nome e quantità
            if i < len(page_cards):

                # recupero la carta presente nello slot
                card = page_cards[i]

                # durante lo sviluppo posso mostrare anche le carte non scoperte
                is_discovered = (
                    DEBUG_REVEAL_ALL_CARDS
                    or self.state.card_collection.is_discovered(card)
                )

                # recupero la quantità posseduta
                quantity = self.state.card_collection.get_quantity(card)

                # le carte di rarità 1 mostrano il simbolo dell'infinito
                if quantity is None:
                    quantity_text = "∞"
                else:
                    quantity_text = f"x{quantity}"

                # mostro il nome vero soltanto se la carta è stata scoperta
                if is_discovered:
                    display_name = card.name
                else:
                    # sostituisco ogni lettera del nome con un punto interrogativo
                    # mantenendo eventuali spazi, trattini e altri simboli
                    display_name = "".join(
                        "?" if character.isalpha() else character
                        for character in card.name
                    )

                # in modalità debug mostro tutte le carte normalmente
                if quantity == 0 and not DEBUG_REVEAL_ALL_CARDS:
                    text_color = (140, 140, 140)
                else:
                    text_color = (255, 255, 255)

                # preparo il nome visibile della carta
                card_name = self.info_font.render(
                    display_name,
                    True,
                    text_color
                )

                # posiziono il nome all'interno dello slot
                card_name_rect = card_name.get_rect(
                    midleft=(
                        draw_slot_rect.x + 15,
                        draw_slot_rect.centery
                    )
                )

                # disegno il nome della carta
                screen.blit(card_name, card_name_rect)

                # preparo la quantità usando lo stesso colore del nome
                quantity_surface = self.info_font.render(
                    quantity_text,
                    True,
                    text_color
                )

                # posiziono la quantità sul lato destro dello slot
                quantity_rect = quantity_surface.get_rect(
                    midright=(
                        draw_slot_rect.right - 15,
                        draw_slot_rect.centery
                    )
                )

                # disegno la quantità posseduta
                screen.blit(quantity_surface, quantity_rect)


        # ripristino l'area di disegno precedente
        screen.set_clip(previous_clip)

        # durante l'animazione la manina rimane nascosta
        if (
            not self.page_animating
            and self.selected_card < len(self.slot_rects)
        ):

            # recupero lo slot selezionato nella sua posizione fissa
            selected_slot_rect = self.slot_rects[
                self.selected_card
            ]

            # disegno la manina animata accanto allo slot selezionato
            self.hand_cursor.draw(
                screen,
                selected_slot_rect,
                gap=5
            )

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