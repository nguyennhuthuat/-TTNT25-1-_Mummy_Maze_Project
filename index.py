import pygame
import os 

def main():
    pygame.init()

    screen_width = 1000
    screen_height = 600
    screen = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
    pygame.display.set_caption("MUMMY MAZE")

    # Load and scale background image
    background_image = pygame.image.load(os.path.join('Assets', 'Images', 'background.jpg')).convert()
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))


    running = True   # Main loop flag

    while running:
        
        for event in pygame.event.get():   # Event handling
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background_image, (0,0))   # Draw background

        # Update the display
        pygame.display.flip()
        pygame.display.update()

    pygame.quit() # Quit Pygame


if __name__ == "__main__":
    main()





