import pygame #serve per creare la finestra di gioco

#inizializzo py game
pygame.init()
# disabilito la ripetizione dei tasti in modo che non scorre velocissimo il menu
pygame.key.set_repeat(0)  

# dimensioni della finestra
width = 1280
height = 720

# creo la finestra di gioco
screen = pygame.display.set_mode((width, height))

#carico lo sfondo del menu
background_image = pygame.image.load("assets/images/background_start_menu.png").convert()  # carico l'immagine di sfondo
background_image = pygame.transform.scale(background_image, (width, height))  # ridimensiono l'immagine di sfondo alle dimensioni della finestra

#creo un font da usare per le voci del menu
font = pygame.font.SysFont("Arial", 45) # font Arial, dimensione 50

# elenco delle voci del menu
menu_items = [
    "Story Mode", 
    "Free Match", 
    "Local Multiplayer",  
    "Deck", 
    "Statistics", 
    "Guide",
    "Settings",  
    "Credits",
    "Exit"]   

# variabili per gestire la selezione e animazione delle voci del menu
selected_item = 0  # indice della voce selezionata

# animazione dello scorrimento del menu
scrolling = False  # flag per indicare se il menu sta animando lo scorrimento
scroll_direction = 0  # direzione dello scorrimento (-1 per su, 1 per giù)
scroll_offset = 0.0  # offset di scorrimento per l'animazione
scroll_speed = 0.4  # velocità di scorrimento in pixel per frame

# quante voci nel menu appaiono sullo schermo contemporaneamente, 5 in questo caso
positions = [
    -2,   # voce sopra
    -1,   # voce sopra
     0,   # voce selezionata
     1,   # voce sotto
     2    # voce sotto
]


running = True
while running: #loop per tenere aperta la finestra di gioco
    # 1 EVENTI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #gestisco la pressione dei tasti per navigare nel menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_item = (selected_item - 1) % len(menu_items)  # seleziono la voce precedente
                scrolling = True  # inizio l'animazione dello scorrimento
                scroll_direction = -1  # imposto la direzione dello scorrimento
                scroll_offset = 0.0  # resetto l'offset di scorrimento
            elif event.key == pygame.K_DOWN:
                selected_item = (selected_item + 1) % len(menu_items)  # seleziono la voce successiva
                scrolling = True  # inizio l'animazione dello scorrimento
                scroll_direction = 1  # imposto la direzione dello scorrimento 
                scroll_offset = 0.0  # resetto l'offset di scorrimento

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # se la rotellina del mouse è stata scrollata verso l'alto
                selected_item = (selected_item - 1) % len(menu_items)  # seleziono la voce precedente
                scrolling = True  # inizio l'animazione dello scorrimento
                scroll_direction = -1  # imposto la direzione dello scorrimento
                scroll_offset = 0.0  # resetto l'offset di scorrimento
            elif event.y < 0:  # se la rotellina del mouse è stata scrollata verso il basso
                selected_item = (selected_item + 1) % len(menu_items)  # seleziono la voce successiva
                scrolling = True  # inizio l'animazione dello scorrimento
                scroll_direction = 1  # imposto la direzione dello scorrimento 
                scroll_offset = 0.0  # resetto l'offset di scorrimento

        CENTER_Y = height // 2  # coordinata y del centro dello schermo
        SPACING = 41  # distanza tra le voci del menu

    # 2 LOGICA
    if scrolling:  # se il menu sta animando lo scorrimento
        scroll_offset += scroll_speed  # aggiorno l'offset di scorrimento
        if scroll_offset >= SPACING:  # se l'offset ha raggiunto la distanza tra le voci del menu
            scrolling = False  # fermo l'animazione dello scorrimento
            scroll_offset = 0.0  # resetto l'offset di scorrimento

    # aggiorno la finestra di gioco
    screen.blit(background_image, (0, 0))  # disegno lo sfondo

    for offset in positions:  # ciclo per disegnare le voci del menu
            index = (selected_item + offset) % len(menu_items)  # calcolo l'indice della voce da disegnare
            text_surface = font.render(menu_items[index], True, (255, 255, 255))  # creo la superficie del testo

            if offset == 0:  # se la voce è selezionata
                text_surface.set_alpha(255) #opacita normale
            elif offset == -1 or offset == 1:  # se la voce è sopra o sotto quella selezionata
                text_surface.set_alpha(120) #opacita media
                text_surface = pygame.transform.scale(text_surface, (int(text_surface.get_width() * 0.7), int(text_surface.get_height() * 0.8)))  # ridimensiono il testo
            else:  # se la voce non è selezionata
                text_surface.set_alpha(60) #opacita ridotta
                text_surface = pygame.transform.scale(text_surface, (int(text_surface.get_width() * 0.5), int(text_surface.get_height() * 0.6)))  # ridimensiono il testo
                
    
            x = (width - text_surface.get_width()) // 2  # calcolo la coordinata x per centrare il testo
            y = CENTER_Y + (CENTER_Y // 5 * 3) + offset * SPACING - scroll_offset * scroll_direction - text_surface.get_height() // 2 # calcolo la coordinata y per posizionare il testo

            screen.blit(text_surface, (x, y))  # disegno il testo sullo schermo

    pygame.display.flip() # disegna tutto quello che sta nel buffer

# Chiude pygame
pygame.quit()