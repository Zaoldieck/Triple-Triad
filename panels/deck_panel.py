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

        # dimensioni iniziali dell'animazione
        self.current_width = 0
        self.current_height = 0

        # apertura indipendente dagli FPS
        self.opening = True
        self.open_duration = 180
        self.open_start_time = pygame.time.get_ticks()

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

        # direzione verticale tenuta premuta:
        # -1 verso l'alto, 1 verso il basso, 0 nessuna
        self.held_vertical_direction = 0

        # momento della pressione iniziale del tasto
        self.held_vertical_start_time = 0

        # momento dell'ultimo movimento automatico
        self.last_vertical_repeat_time = 0

        # attesa prima di iniziare lo scorrimento continuo
        self.vertical_repeat_delay = 500

        # intervallo tra i movimenti automatici successivi
        self.vertical_repeat_interval = 90

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

        # durata di ciascuna fase del cambio pagina,
        # indipendente dal numero di FPS
        self.page_animation_duration = 180

        # momento iniziale della fase corrente
        self.page_animation_start_time = 0

        # numero carte per pagina
        self.cards_per_page = 11

        # carico soltanto le carte appartenenti ai set abilitati
        self.cards = load_cards(
            "data/cards.json",
            ACTIVE_CARD_SETS
        )

        # indice della prima carta visibile
        # nella lista della rarità corrente
        self.first_visible_card = 0

        # superficie che conterrà l'anteprima della carta selezionata
        self.card_preview = None

        # identifica la carta e lo stato mostrati nell'anteprima
        self.previewed_card_key = None

        # lista che contiene i rettangoli degli slot delle carte
        self.slot_rects = []

    # restituisce soltanto le carte appartenenti
    # alla rarità attualmente mostrata
    def get_current_rarity_cards(self):

        # current_page parte da 0,
        # mentre le rarità vanno da 1 a 10
        current_rarity = self.current_page + 1

        return [
            card
            for card in self.cards
            if card.rarity == current_rarity
        ]
    
    # aggiorna l'anteprima quando cambia la carta selezionata
    def update_card_preview(self):

        # recupero tutte le carte
        # appartenenti alla rarità corrente
        rarity_cards = self.get_current_rarity_cards()

        # se la rarità è vuota oppure la selezione
        # non corrisponde a una carta, rimuovo l'anteprima
        if (
            not rarity_cards
            or self.selected_card >= len(rarity_cards)
        ):
            self.card_preview = None
            self.previewed_card_key = None
            return

        # recupero la carta selezionata
        # all'interno della rarità corrente
        selected_card = rarity_cards[
            self.selected_card
        ]

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
            selected_card.card_id,
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

        # calcolo la rarità richiesta
        requested_page = (
            self.current_page + direction
        )

        # impedisco di andare prima della rarità 1
        # oppure oltre la rarità 10
        if not 0 <= requested_page < self.total_pages:
            return

        # salvo la nuova pagina valida
        self.target_page = requested_page

        # salvo la direzione richiesta
        self.page_animation_direction = direction

        # l'animazione comincia facendo uscire
        # la pagina attualmente visibile
        self.page_animation_phase = "out"
        self.page_animation_offset = 0.0
        self.page_animating = True

        self.page_animation_start_time = (
            pygame.time.get_ticks()
        )

    # aggiorna lo scorrimento orizzontale
    # delle righe durante il cambio rarità
    def update_page_animation(self):

        if not self.page_animating:
            return

        animation_distance = 400
        current_time = pygame.time.get_ticks()

        elapsed_time = (
            current_time
            - self.page_animation_start_time
        )

        animation_progress = min(
            1.0,
            elapsed_time
            / self.page_animation_duration
        )

        # movimento rapido all'inizio
        # e più morbido alla fine
        eased_progress = (
            1.0
            - (1.0 - animation_progress) ** 3
        )

        # faccio uscire la pagina attuale
        if self.page_animation_phase == "out":

            self.page_animation_offset = (
                -self.page_animation_direction
                * animation_distance
                * eased_progress
            )

            if animation_progress >= 1.0:

                # applico la nuova rarità
                self.current_page = self.target_page
                self.selected_card = 0
                self.first_visible_card = 0

                # la nuova pagina entra
                # dal lato opposto
                self.page_animation_phase = "in"

                self.page_animation_offset = (
                    self.page_animation_direction
                    * animation_distance
                )

                self.page_animation_start_time = (
                    current_time
                )

        # faccio entrare la nuova pagina
        elif self.page_animation_phase == "in":

            self.page_animation_offset = (
                self.page_animation_direction
                * animation_distance
                * (1.0 - eased_progress)
            )

            if animation_progress >= 1.0:

                self.page_animation_offset = 0.0
                self.page_animating = False
                self.page_animation_phase = None
                self.page_animation_direction = 0

    # sposta la selezione nella rarità corrente
    # e scorre automaticamente le righe visibili
    def move_card_selection(self, direction):

        # recupero le carte della rarità corrente
        rarity_cards = self.get_current_rarity_cards()

        # non posso muovere la selezione
        # se questa rarità non contiene carte
        if not rarity_cards:
            return

        # calcolo la nuova posizione impedendo
        # alla selezione di superare gli estremi
        self.selected_card = max(
            0,
            min(
                len(rarity_cards) - 1,
                self.selected_card + direction
            )
        )

        # se la carta selezionata si trova sopra
        # la prima riga visibile, scorro verso l'alto
        if self.selected_card < self.first_visible_card:
            self.first_visible_card = self.selected_card

        # se la carta selezionata si trova sotto
        # l'ultima riga visibile, scorro verso il basso
        elif (
            self.selected_card
            >= self.first_visible_card + self.cards_per_page
        ):
            self.first_visible_card = (
                self.selected_card
                - self.cards_per_page
                + 1
            )

    # aggiorna lo scorrimento verticale
    # quando Su oppure Giù rimangono premuti
    def update_held_vertical_navigation(self):

        # nessun tasto verticale è tenuto premuto
        if self.held_vertical_direction == 0:
            return

        # non scorro durante il cambio rarità
        if self.page_animating:
            return

        current_time = pygame.time.get_ticks()

        # aspetto mezzo secondo dalla pressione iniziale
        if (
            current_time - self.held_vertical_start_time
            < self.vertical_repeat_delay
        ):
            return

        # dopo l'attesa, avanzo rispettando
        # l'intervallo della ripetizione
        if (
            current_time - self.last_vertical_repeat_time
            >= self.vertical_repeat_interval
        ):
            self.move_card_selection(
                self.held_vertical_direction
            )

            self.last_vertical_repeat_time = current_time

    def handle_events(self, event):

        # recupero le carte appartenenti
        # alla rarità corrente
        rarity_cards = self.get_current_rarity_cards()

        # calcolo quante carte sono attualmente visibili
        cards_on_page = max(
            0,
            min(
                self.cards_per_page,
                len(rarity_cards) - self.first_visible_card
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
                # eseguo immediatamente il primo movimento
                self.move_card_selection(-1)

                # preparo la ripetizione se il tasto
                # rimane premuto per almeno mezzo secondo
                current_time = pygame.time.get_ticks()
                self.held_vertical_direction = -1
                self.held_vertical_start_time = current_time
                self.last_vertical_repeat_time = current_time

            elif (
                event.key == pygame.K_DOWN
                and cards_on_page > 0
                and not self.page_animating
            ):
                # eseguo immediatamente il primo movimento
                self.move_card_selection(1)

                # preparo la ripetizione se il tasto
                # rimane premuto per almeno mezzo secondo
                current_time = pygame.time.get_ticks()
                self.held_vertical_direction = 1
                self.held_vertical_start_time = current_time
                self.last_vertical_repeat_time = current_time


            # pagina precedente
            elif event.key == pygame.K_LEFT:
                self.change_page(-1)

            # pagina successiva
            elif event.key == pygame.K_RIGHT:
                self.change_page(1)

        # interrompo lo scorrimento continuo
        # quando il tasto viene rilasciato
        if event.type == pygame.KEYUP:

            released_held_key = (
                (
                    event.key == pygame.K_UP
                    and self.held_vertical_direction == -1
                )
                or
                (
                    event.key == pygame.K_DOWN
                    and self.held_vertical_direction == 1
                )
            )

            if released_held_key:
                self.held_vertical_direction = 0

        # la rotella scorre le carte
        # della rarità corrente una riga alla volta
        if (
            event.type == pygame.MOUSEWHEEL
            and not self.page_animating
        ):

            # rotella verso l'alto:
            # seleziono la carta precedente
            if event.y > 0:
                self.move_card_selection(-1)

            # rotella verso il basso:
            # seleziono la carta successiva
            elif event.y < 0:
                self.move_card_selection(1)

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
                    # converto la riga visibile
                    # nell'indice reale dentro la rarità
                    self.selected_card = (
                        self.first_visible_card + i
                    )

        if event.type == pygame.MOUSEBUTTONDOWN:

            # tasto destro del mouse
            if event.button == 3:
                self.state.close_panel()

    # logica del pannello                
    def update(self):

        # aggiorno l'animazione del cambio pagina
        self.update_page_animation()

        # aggiorno l'eventuale scorrimento continuo
        # causato da Su oppure Giù tenuti premuti
        self.update_held_vertical_navigation()

        # aggiorno l'anteprima della carta selezionata
        self.update_card_preview()

        if self.opening:

            elapsed_time = (
                pygame.time.get_ticks()
                - self.open_start_time
            )

            open_progress = min(
                1.0,
                elapsed_time / self.open_duration
            )

            # movimento ease-out:
            # rapido all'inizio e morbido alla fine
            eased_progress = (
                1.0
                - (1.0 - open_progress) ** 3
            )

            self.current_width = int(
                self.panel_width
                * eased_progress
            )

            self.current_height = int(
                self.panel_height
                * eased_progress
            )

            if open_progress >= 1.0:
                self.current_width = self.panel_width
                self.current_height = self.panel_height
                self.opening = False       

    # disegna il pannello
    def draw(self, screen):

        #posizione del pannello sullo schermo
        x = (self.width - self.current_width) // 2
        y = (self.height - self.current_height) // 2

        #creo il rettangolo del pannello
        panel_rect = pygame.Rect(x, y, self.current_width, self.current_height)

        # disegno il pannello durante l'apertura
        pygame.draw.rect(
            screen,
            self.color,
            panel_rect
        )

        # righe, testi e anteprima vengono mostrati
        # soltanto a pannello completamente aperto
        if self.opening:
            return

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

        # recupero tutte le carte
        # appartenenti alla rarità corrente
        rarity_cards = self.get_current_rarity_cards()

        # estraggo al massimo 11 carte partendo
        # dalla prima posizione attualmente visibile
        page_cards = rarity_cards[
            self.first_visible_card:
            self.first_visible_card + self.cards_per_page
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

        # controllo se esistono carte nascoste
        # sopra l'intervallo attualmente visibile
        can_scroll_up = (
            self.first_visible_card > 0
        )

        # controllo se esistono carte nascoste
        # sotto l'intervallo attualmente visibile
        can_scroll_down = (
            self.first_visible_card
            + len(page_cards)
            < len(rarity_cards)
        )

        # mostro una freccia sopra la lista
        # quando è possibile scorrere verso l'alto
        if can_scroll_up:

            up_arrow_surface = self.info_font.render(
                "▲",
                True,
                (255, 255, 255)
            )

            up_arrow_rect = up_arrow_surface.get_rect(
                center=(
                    list_rect.centerx,
                    list_rect.top - 14
                )
            )

            screen.blit(
                up_arrow_surface,
                up_arrow_rect
            )

        # mostro una freccia sotto la lista
        # quando è possibile scorrere verso il basso
        if can_scroll_down:

            down_arrow_surface = self.info_font.render(
                "▼",
                True,
                (255, 255, 255)
            )

            down_arrow_rect = down_arrow_surface.get_rect(
                center=(
                    list_rect.centerx,
                    list_rect.bottom + 14
                )
            )

            screen.blit(
                down_arrow_surface,
                down_arrow_rect
            )

        # converto l'indice reale della carta
        # nella relativa riga visibile
        selected_visible_row = (
            self.selected_card
            - self.first_visible_card
        )

        # durante l'animazione la manina rimane nascosta
        if (
            not self.page_animating
            and 0 <= selected_visible_row < len(page_cards)
        ):

            # recupero lo slot corrispondente
            # alla riga attualmente visibile
            selected_slot_rect = self.slot_rects[
                selected_visible_row
            ]

            # disegno la manina animata
            # accanto alla carta selezionata
            self.hand_cursor.draw(
                screen,
                selected_slot_rect,
                gap=5
            )

        # calcolo il numero totale di carte
        # appartenenti alla rarità corrente
        total_rarity_cards = len(rarity_cards)

        # se la rarità non contiene carte,
        # l'intervallo visibile è 0–0
        if total_rarity_cards == 0:
            first_visible_number = 0
            last_visible_number = 0

        else:
            # gli indici interni partono da zero,
            # mentre il contatore mostrato parte da uno
            first_visible_number = (
                self.first_visible_card + 1
            )

            last_visible_number = (
                self.first_visible_card
                + len(page_cards)
            )

        # preparo rarità, intervallo visibile
        # e numero totale di carte
        page_text = self.info_font.render(
            (
                f"Rarity {self.current_page + 1}   "
                f"Cards {first_visible_number}–"
                f"{last_visible_number} / "
                f"{total_rarity_cards}"
            ),
            True,
            (255, 255, 255)
        )

        #posiziono il numero della pagina nella parte destra del pannello
        page_text_rect = page_text.get_rect(
            center=(x + 665, y + 30)
        )

        # disegno le informazioni della rarità corrente
        screen.blit(
            page_text,
            page_text_rect
        )

        # mostro una freccia triangolare a sinistra
        # soltanto se esiste una rarità precedente
        if self.current_page > 0:

            left_arrow_center_x = (
                page_text_rect.left - 18
            )

            left_arrow_center_y = (
                page_text_rect.centery
            )

            pygame.draw.polygon(
                screen,
                (255, 255, 255),
                [
                    (
                        left_arrow_center_x + 7,
                        left_arrow_center_y - 9
                    ),
                    (
                        left_arrow_center_x - 7,
                        left_arrow_center_y
                    ),
                    (
                        left_arrow_center_x + 7,
                        left_arrow_center_y + 9
                    )
                ]
            )

        # mostro una freccia triangolare a destra
        # soltanto se esiste una rarità successiva
        if self.current_page < self.total_pages - 1:

            right_arrow_center_x = (
                page_text_rect.right + 18
            )

            right_arrow_center_y = (
                page_text_rect.centery
            )

            pygame.draw.polygon(
                screen,
                (255, 255, 255),
                [
                    (
                        right_arrow_center_x - 7,
                        right_arrow_center_y - 9
                    ),
                    (
                        right_arrow_center_x + 7,
                        right_arrow_center_y
                    ),
                    (
                        right_arrow_center_x - 7,
                        right_arrow_center_y + 9
                    )
                ]
            )

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

        # esistono sempre dieci pagine fisse:
        # una per ogni livello di rarità
        return 10