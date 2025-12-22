import pygame
import sys

def open_lose_window(screen, background_to_draw):
    font_btn = pygame.font.SysFont('Arial', 22, bold=True)
    
    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # TẢI ẢNH BẢNG (Board)
    try:
        board_img = pygame.image.load('./MummyMaze/main_menu_assets/window.png').convert_alpha()
        scale_factor = 1.22
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.scale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x-250, center_y-150, 500, 300)

    #TẢI TÊN GAME
    logo_img = pygame.image.load('./MummyMaze/main_menu_assets/menulogo.png').convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (700, 700))
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 200))

    #TẢI DÒNG "GAME OVER"
    game_over_img = pygame.image.load('./MummyMaze/main_menu_assets/game_over.png').convert_alpha()
    game_over_img = pygame.transform.scale(game_over_img, (300, 300))
    game_over_rect = game_over_img.get_rect(center=(center_x - 50, center_y + 100))

    # Định vị nút bấm
    btn_w, btn_h = 300, 100
    gap = 20                

    rect_retry = pygame.Rect(0, 0, btn_w, btn_h)
    rect_retry.center = (center_x - (btn_w // 2 + gap), center_y + 170)
    
    rect_abandon = pygame.Rect(0, 0, btn_w, btn_h)
    rect_abandon.center = (center_x + (btn_w // 2 + gap), center_y + 170)

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
                if rect_retry.collidepoint(mouse_pos):
                    user_action = "retry"; running = False
                elif rect_abandon.collidepoint(mouse_pos):
                    user_action = "abandon"; running = False
        
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

        # Vẽ "GAME OVER"
        screen.blit(game_over_img, game_over_rect)

        # 3. Vẽ chữ lên các nút
        for rect, text in [(rect_retry, "TRY AGAIN"), (rect_abandon, "QUIT")]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        
    return user_action

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Tải Background chính
    try:
        bg = pygame.image.load('./MummyMaze/main_menu_assets/background_window.png').convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None

    action = open_lose_window(screen, bg)
    
    print(f"Action: {action}")

    pygame.time.delay(500)
    pygame.quit()
    sys.exit()