import pygame
import sys

def open_lobby(screen, background_to_draw, logo_icon):
    try:
        main_font = pygame.font.SysFont("comic sans ms", 24) 
        footer_font = pygame.font.SysFont("comic sans ms", 14) # Thêm dòng này (size 14 thay vì 24)
        title_font = pygame.font.SysFont("comic sans ms", 50)
        font_btn = pygame.font.SysFont('Arial', 50, bold = 30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # TẢI ẢNH WINDOW
    try:
        board_img = pygame.image.load('./MummyMaze/main_menu_assets/window.png').convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.scale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x - 250, center_y - 150, 500, 300)

    #TẢI TÊN GAME
    scale_size = 1.2
    logo_img = pygame.image.load('./MummyMaze/main_menu_assets/menulogo.png').convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (logo_img.get_width() * scale_size, logo_img.get_height() * scale_size))
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 230))

    # Định vị nút bấm
    btn_w, btn_h = 300, 100
    gap = 60            

    rect_classic_mode = pygame.Rect(0, 0, btn_w, btn_h)
    rect_classic_mode.center = (center_x - (btn_w // 2 + gap), center_y + 190)

    rect_adventure = pygame.Rect(0, 0, btn_w, btn_h)
    rect_adventure.center = (center_x - (btn_w // 2 + gap), center_y + 190 + 90)
    
    rect_tutorials = pygame.Rect(0, 0, btn_w, btn_h)
    rect_tutorials.center = (center_x + (btn_w // 2 + gap), center_y + 190)

    rect_quit_game = pygame.Rect(0, 0, btn_w, btn_h)
    rect_quit_game.center = (center_x + (btn_w // 2 + gap), center_y + 190 + 90)

    # Tạo lớp phủ mờ (Alpha)
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150) # Độ mờ (0-255)
    overlay.fill(COLOR_BG_OVERLAY)
    
    running = True
    user_action = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_classic_mode.collidepoint(mouse_pos):
                    user_action = "enter classic mode"; running = False
                elif rect_tutorials.collidepoint(mouse_pos):
                    user_action = "open tutorials"; running = False
                elif rect_adventure.collidepoint(mouse_pos):
                    user_action = "open adventure"; running = False
                elif rect_quit_game.collidepoint(mouse_pos):
                    user_action = "quit game"; running = False
        
        # 1. Vẽ ảnh nền Game trước
        if background_to_draw:
            screen.blit(background_to_draw, (0, 0))
        else:
            screen.fill((100, 150, 100))

        screen.blit(overlay, (0, 0))

        screen.blit(logo_img, logo_rect)

        # 2. Vẽ lose_window
        if board_img:
            screen.blit(board_img, board_rect)
        else:
            pygame.draw.rect(screen, (210, 180, 140), board_rect)
        
        # Vẽ tên game
        screen.blit(logo_img, logo_rect)

        # 3. Vẽ chữ lên các nút
        for rect, text in [(rect_classic_mode, "CLASSIC MODE"), 
                           (rect_tutorials, "TUTORIALS"),
                           (rect_adventure, "ADVENTURE"),
                           (rect_quit_game, "QUIT GAME")]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)
        
        screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))


        pygame.display.flip()
        
    return user_action

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mummy Maze - 25TNT1 - Dudes Chase Money")  

    # Tải Background chính
    try:
        bg = pygame.image.load('./MummyMaze/main_menu_assets/background_window.png').convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None
    
    try:
        logo_image = pygame.image.load("./MummyMaze/main_menu_assets/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")

    action = open_lobby(screen, bg, logo_icon)
    
    print(f"Action: {action}")

    pygame.time.delay(500)
    pygame.quit()
    sys.exit()