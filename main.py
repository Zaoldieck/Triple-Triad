import pygame #serve per creare la finestra di gioco
from screens.main_menu import MainMenu # serve per importare la classe MainMenu dal file main_menu.py

#inizializzo py game
pygame.init()
# disabilito la ripetizione dei tasti in modo che non scorre velocissimo il menu
pygame.key.set_repeat(0)  

# dimensioni della finestra
width = 1280
height = 720

# creo la finestra di gioco
screen = pygame.display.set_mode((width, height))

#creo il menu principale
main_menu = MainMenu(width, height)  # creo un'istanza della classe MainMenu spostato a parte

running = True
while running: #loop per tenere aperta la finestra di gioco
    # 1 EVENTI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # inoltro gli eventi al menu principale
        main_menu.handle_events(event)

    # 2 LOGICA
    main_menu.update()

    # 3 DISEGNO
    main_menu.draw(screen)

    pygame.display.flip() # disegna tutto quello che sta nel buffer

# Chiude pygame
pygame.quit()