import pygame

# dimensioni originali usate per costruire le carte
CARD_WIDTH = 416
CARD_HEIGHT = 526
CARD_SIZE = (CARD_WIDTH, CARD_HEIGHT)

NUMBER_SIZE = (40, 40)
ELEMENT_SIZE = (52, 52)


# restituisce il percorso del bordo corretto in base alla rarità
def get_border_path(rarity):

    # le rarità da 1 a 5 condividono il primo bordo
    if 1 <= rarity <= 5:
        border_number = 1

    # le rarità 6 e 7 condividono il secondo bordo
    elif 6 <= rarity <= 7:
        border_number = 2

    # le rarità 8 e 9 condividono il terzo bordo
    elif 8 <= rarity <= 9:
        border_number = 3

    # la rarità 10 utilizza il quarto bordo
    elif rarity == 10:
        border_number = 4

    # segnalo un errore se la rarità non è compresa tra 1 e 10
    else:
        raise ValueError(
            f"Invalid card rarity: {rarity}"
        )

    # costruisco e restituisco il percorso del bordo
    return (
        "assets/images/cards/borders/"
        f"rarity_{border_number}.png"
    )

# restituisce il percorso dello sfondo scelto per la carta
def get_background_path(background_color):

    # controllo che il colore richiesto sia disponibile
    if background_color not in ["blue", "red"]:
        raise ValueError(
            f"Invalid card background: {background_color}"
        )

    # costruisco e restituisco il percorso dello sfondo
    return (
        "assets/images/cards/backgrounds/"
        f"{background_color}.png"
    )

# restituisce il percorso dell'immagine associata a un valore
def get_number_path(value):

    # controllo che il valore sia compreso tra 1 e 10
    if not 1 <= value <= 10:
        raise ValueError(
            f"Invalid card value: {value}"
        )

    # costruisco e restituisco il percorso dell'immagine numerica
    return (
        "assets/images/cards/numbers/"
        f"{value}.png"
    )

# restituisce il percorso dell'icona associata all'elemento
def get_element_path(element):

    # una carta con elemento None non deve mostrare alcuna icona
    if element is None:
        return None

    # elenco degli elementi disponibili
    valid_elements = [
        "earth",
        "fire",
        "holy",
        "ice",
        "poison",
        "thunder",
        "water",
        "wind"
    ]

    # controllo che l'elemento richiesto sia disponibile
    if element not in valid_elements:
        raise ValueError(
            f"Invalid card element: {element}"
        )

    # costruisco e restituisco il percorso dell'icona
    return (
        "assets/images/cards/elements/"
        f"{element}.png"
    )


# costruisce graficamente una carta sovrapponendo i vari livelli
def render_card(card, background_color):

    # recupero il percorso dello sfondo richiesto
    background_path = get_background_path(background_color)

    # carico lo sfondo mantenendo l'eventuale trasparenza
    card_surface = pygame.image.load(
        background_path
    ).convert_alpha()

    # assicuro che lo sfondo abbia le dimensioni corrette
    card_surface = pygame.transform.smoothscale(
        card_surface,
        CARD_SIZE
    )

    # carico l'illustrazione specifica della carta
    card_image = pygame.image.load(
        card.image_path
    ).convert_alpha()

    # assicuro che l'illustrazione abbia le dimensioni della carta
    card_image = pygame.transform.smoothscale(
        card_image,
        CARD_SIZE
    )

    # sovrappongo l'illustrazione trasparente allo sfondo
    card_surface.blit(card_image, (0, 0))

    # recupero il bordo associato alla rarità della carta
    border_path = get_border_path(card.rarity)

    # carico il bordo mantenendo la trasparenza
    border_image = pygame.image.load(
        border_path
    ).convert_alpha()

    # assicuro che il bordo abbia le dimensioni della carta
    border_image = pygame.transform.smoothscale(
        border_image,
        CARD_SIZE
    )

    # sovrappongo il bordo allo sfondo e all'illustrazione
    card_surface.blit(border_image, (0, 0))

    # associo ogni valore alla sua posizione sulla carta
    number_data = [
        (card.top, (48, 20)),
        (card.right, (78, 50)),
        (card.bottom, (48, 80)),
        (card.left, (18, 50))
    ]

    # carico e disegno i quattro valori della carta
    for value, position in number_data:

        # recupero il percorso dell'immagine del valore
        number_path = get_number_path(value)

        # carico l'immagine numerica mantenendo la trasparenza
        number_image = pygame.image.load(
            number_path
        ).convert_alpha()

        # ridimensiono l'immagine numerica
        number_image = pygame.transform.smoothscale(
            number_image,
            NUMBER_SIZE
        )

        # disegno il valore nella posizione assegnata
        card_surface.blit(number_image, position)

    # recupero il percorso dell'eventuale icona elementale
    element_path = get_element_path(card.element)

    # disegno l'icona soltanto se la carta possiede un elemento
    if element_path is not None:

        # carico l'icona mantenendo la trasparenza
        element_image = pygame.image.load(
            element_path
        ).convert_alpha()

        # ridimensiono l'icona elementale
        element_image = pygame.transform.smoothscale(
            element_image,
            ELEMENT_SIZE
        )

        # calcolo la posizione nell'angolo in alto a destra
        element_position = (
            CARD_WIDTH - ELEMENT_SIZE[0] - 18,
            18
        )

        # sovrappongo l'icona elementale alla carta
        card_surface.blit(
            element_image,
            element_position
        )


    # restituisco la carta composta fin ora
    return card_surface