import pygame
import sys
from fonts import MetricFont

def open_win_window(screen):
    # Tải backdrop và nền next level
    try:
        # 1. Load ảnh nền gốc (640x480)
        bg_original = pygame.image.load('./assets/images/backdropwithbutton.png').convert()
        
        # 2. Load ảnh Next Level
        next_level_img = pygame.image.load('./assets/images/nextlevel.png').convert_alpha()
        
        # 3. Tính toán kích thước để khớp vào khung (212, 78) -> (573, 439)
        target_width = 573 - 212
        target_height = 439 - 78
        
        # 4. Scale ảnh Next Level theo kích thước vừa tính
        next_level_scaled = pygame.transform.scale(next_level_img, (target_width, target_height))
        
        # 5. Vẽ ảnh đã scale vào đúng vị trí góc trên bên trái (212, 78)
        bg_original.blit(next_level_scaled, (212, 78))
        
        # 6. Cuối cùng mới scale toàn bộ "bức tranh" lên kích thước màn hình lớn
        bg = pygame.transform.scale(bg_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
    except Exception as e:
        print(f"Error loading images: {e}")
        bg = None

    try:
        logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")

    next_level_img = pygame.image.load('./assets/images/nextlevel.png').convert_alpha()

    try:
        noti_font = MetricFont(font_name="scorefont", scale_height = 40)

        main_font = pygame.font.SysFont("comic sans ms", 24) 
        footer_font = pygame.font.SysFont("comic sans ms", 14)
        font_btn = pygame.font.SysFont('Arial', 50, bold = 30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    #TẢI TÊN GAME
    scale_size = 0.15
    logo_img = pygame.image.load('./assets/images/mumlogo.png').convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (logo_img.get_width() * scale_size, logo_img.get_height() * scale_size))
    logo_rect = logo_img.get_rect(center=(center_x - 460, center_y - 270))

    # Định vị nút bấm
    btn_w, btn_h = 300, 100
    gap = 60            
    
    running = True
    user_action = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                user_action = "quit"

        mouse_pos = pygame.mouse.get_pos()

        # 1. Vẽ ảnh nền Game trước
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((100, 150, 100))

        screen.blit(logo_img, logo_rect)
        
        # Vẽ tên game
        screen.blit(logo_img, logo_rect)

        #Vẽ các chữ
        text_str = 'You have escaped the maze'
        text_w = noti_font.get_width(text_str)
        noti_font.render(screen, text_str, center_x - (text_w // 2), center_y - 250)
        
        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)

        #screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))

        pygame.display.flip()
        
    return user_action

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mummy Maze - 25TNT1 - Dudes Chase Money")  

    action = open_win_window(screen)
    
    print(f"Action: {action}")

    pygame.time.delay(500)
    pygame.quit()
    sys.exit()
