import pygame
import sys
from fonts import MetricFont

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
COLOR_BG_OVERLAY = (0, 0, 0)
TEXT_COLOR       = (40, 20, 10)
HOVER_COLOR      = (255, 0, 0)
INPUT_TEXT_COLOR = (50, 50, 50)

def open_switch_account_window(screen, account_list):
    # --- KHỞI TẠO FONT ---
    try:
        # Font cho tiêu đề và nút chức năng (Headerfont)
        font_header = MetricFont(font_name="headerfont", scale_height=40)

        font_title = MetricFont(font_name="headerfont", scale_height=25)
        
        # [YÊU CẦU] Font1 cho tên người dùng trong danh sách
        font_username = MetricFont(font_name="font1", scale_height=35) 

        footer_font = pygame.font.SysFont("comic sans ms", 14)
    except Exception as e:
        font_header = pygame.font.Font(None, 40)
        font_username = pygame.font.Font(None, 35)
        footer_font = pygame.font.Font(None, 18)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # --- LOAD RESOURCE ---
    try:
        bg = pygame.image.load('./assets/images/background_window.png').convert()
        bg = pygame.transform.scale(bg, (w, h))
    except: bg = None
    
    try:
        board_img = pygame.image.load('./assets/images/window.png').convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.smoothscale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x - 250, center_y - 150, 500, 300)

    try:
        logo_img = pygame.image.load('./assets/images/menulogo.png').convert_alpha()
        logo_rect = logo_img.get_rect(center=(center_x, center_y - 230))
    except: logo_img = None

    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150)
    overlay.fill(COLOR_BG_OVERLAY)

    running = True
    result = None # Trả về: ("select", name) hoặc ("goto_register", None) hoặc ("back", None)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        interactive_items = []

        # 1. Các nút chức năng (Dưới cùng)
        # Nút New Account (Register)
        btn_reg_pos = (center_x + 290, center_y + 280)
        interactive_items.append((
            font_header.render("NEW ACCOUNT", True, TEXT_COLOR),
            btn_reg_pos,
            "goto_register"
        ))

        # Nút Back
        btn_back_pos = (center_x - 290, center_y + 280 )
        interactive_items.append((
            font_header.render("GO BACK", True, TEXT_COLOR),
            btn_back_pos,
            "back"
        ))

        # 2. Danh sách User (Ở giữa) - Dùng Font1
        delta = 200
        start_y = center_y - 50 + delta
        line_height = 60
        
        for i, acc_name in enumerate(account_list):
            if i >= 4: break # Chỉ hiện tối đa 4 user
            pos = (center_x, start_y + i * line_height)
            
            # Render tên user
            surf = font_username.render(acc_name, True, TEXT_COLOR)
            interactive_items.append((surf, pos, f"select:{acc_name}"))

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Kiểm tra click
                for surf, pos, action in interactive_items:
                    rect = surf.get_rect(center=pos)
                    if rect.collidepoint(mouse_pos):
                        if action == "goto_register":
                            result = ("goto_register", None)
                        elif action == "back":
                            result = ("back", None)
                        elif action.startswith("select:"):
                            result = ("select", action.split(":")[1])
                        running = False

        # --- DRAWING ---
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill((100, 150, 100))
        screen.blit(overlay, (0, 0))

        if logo_img: screen.blit(logo_img, logo_rect)

        if board_img: screen.blit(board_img, board_rect)
        else: pygame.draw.rect(screen, (210, 180, 140), board_rect)
        
        if logo_img: screen.blit(logo_img, logo_rect)

        # Tiêu đề
        title_surf = font_title.render("SELECT ACCOUNT", True, HOVER_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 90 + delta)))

        # Vẽ các item
        for surf, pos, action in interactive_items:
            rect = surf.get_rect(center=pos)
            
            # Xử lý Hover (Vẽ lại màu đỏ nếu hover)
            if rect.collidepoint(mouse_pos):
                # Vì MetricFont render ra ảnh, ta cần render lại màu khác hoặc dùng filter
                # Ở đây ta giả định gọi lại hàm render cho đơn giản
                if action.startswith("select:"):
                    name = action.split(":")[1]
                    surf = font_username.render(name, True, HOVER_COLOR)
                elif action == "goto_register":
                    surf = font_header.render("NEW ACCOUNT", True, HOVER_COLOR)
                elif action == "back":
                    surf = font_header.render("GO BACK", True, HOVER_COLOR)
            
            screen.blit(surf, rect)

        footer_text = footer_font.render("Version 1.0.1 | © 25TNT1", True, TEXT_COLOR)
        screen.blit(footer_text, footer_text.get_rect(centerx=w//2, bottom=h))
        
        pygame.display.flip()

    return result
