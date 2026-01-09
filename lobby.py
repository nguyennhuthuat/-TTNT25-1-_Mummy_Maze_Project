import pygame
import sys
from fonts import MetricFont

# Import 2 hàm từ file register_window.py vừa tạo
from register_window import open_register_window
from switch_account_window import open_switch_account_window

# --- Dữ liệu giả lập danh sách tài khoản (để test) ---
# Thử xóa hết tên trong list này để test trường hợp chưa có tài khoản
EXISTING_ACCOUNTS = ["ProPlayer1", "DragonSlayer", "NoobMaster"] 

def open_lobby(screen):
    try:
        footer_font = pygame.font.SysFont("comic sans ms", 14)
        font_btn = MetricFont(font_name="headerfont", scale_height=40) 
    except Exception as e:
        footer_font = pygame.font.Font(None, 18)
        font_btn = pygame.font.Font(None, 50)

    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)
    HOVER_COLOR      = (255, 0, 0)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # Load Resources
    try:
        bg = pygame.image.load('./assets/images/background_window.png').convert()
        bg = pygame.transform.scale(bg, (w, h))
    except: bg = None
    try:
        logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except: pass
    try:
        board_img = pygame.image.load('./assets/images/window.png').convert_alpha()
        scale_factor = 1.48; new_w = int(board_img.get_width()*scale_factor); new_h = int(board_img.get_height()*scale_factor)
        board_img = pygame.transform.smoothscale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None; board_rect = pygame.Rect(center_x-250, center_y-150, 500, 300)
    
    logo_img = pygame.image.load('./assets/images/menulogo.png').convert_alpha()
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 230))

    btn_w, btn_h = 300, 100; gap = 60            
    pos_classic   = (center_x - (btn_w//2 + gap), center_y + 190)
    pos_reg       = (center_x - (btn_w//2 + gap), center_y + 190 + 90)
    pos_tut       = (center_x + (btn_w//2 + gap), center_y + 190)
    pos_quit      = (center_x + (btn_w//2 + gap), center_y + 190 + 90)

    # Cấu hình nút: Action "btn_register_click" để xử lý riêng
    buttons_config = [
        ("CLASSIC MODE", pos_classic, "enter classic mode"),
        ("TUTORIALS", pos_tut, "open tutorials"),
        ("REGISTER", pos_reg, "btn_register_click"),
        ("QUIT GAME", pos_quit, "quit game")
    ]

    overlay = pygame.Surface((w, h)); overlay.set_alpha(150); overlay.fill(COLOR_BG_OVERLAY)
    running = True; user_action = None

    while running:
        mouse_pos = pygame.mouse.get_pos()
        active_buttons = []
        for txt, p, act in buttons_config:
            s = font_btn.render(txt, True, TEXT_COLOR)
            active_buttons.append((s, s.get_rect(center=p), act))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for _, r, action in active_buttons:
                    if r.collidepoint(mouse_pos):
                        
                        # --- LOGIC XỬ LÝ NÚT REGISTER ---
                        if action == "btn_register_click":
                            if len(EXISTING_ACCOUNTS) > 0:
                                # A. Đã có tài khoản -> Mở Switch Account Window
                                switch_res = open_switch_account_window(screen, EXISTING_ACCOUNTS)
                                
                                if switch_res:
                                    status, data = switch_res
                                    if status == "goto_register":
                                        # Người dùng chọn "New Account" từ danh sách
                                        reg_data = open_register_window(screen)
                                        if reg_data: 
                                            print(f"New User Registered: {reg_data}")
                                            user_action = "register_success"
                                            running = False
                                    elif status == "select":
                                        print(f"User switched to: {data}")
                                        user_action = f"login_{data}"
                                        running = False
                                    elif status == "back":
                                        pass # Quay lại lobby
                            else:
                                # B. Chưa có tài khoản -> Mở Register Window trực tiếp
                                reg_data = open_register_window(screen)
                                if reg_data:
                                    print(f"Registered: {reg_data}")
                                    user_action = "register_success"
                                    running = False
                        
                        else:
                            # Các nút khác (Classic, Tutorial...)
                            user_action = action
                            running = False

        if bg: screen.blit(bg, (0,0))
        else: screen.fill((100,150,100))
        screen.blit(overlay, (0,0))
        if logo_img: screen.blit(logo_img, logo_rect)
        if board_img: screen.blit(board_img, board_rect)
        else: pygame.draw.rect(screen, (210,180,140), board_rect)
        if logo_img: screen.blit(logo_img, logo_rect)

        for s, r, _ in active_buttons:
            col = HOVER_COLOR if r.collidepoint(mouse_pos) else TEXT_COLOR
            for txt, pos_orig, act_orig in buttons_config:
                if r.center == pos_orig: # So khớp vị trí để tìm text
                    s_colored = font_btn.render(txt, True, col)
                    screen.blit(s_colored, r)
                    break

        footer = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        screen.blit(footer, footer.get_rect(centerx=w//2, bottom=h))
        if 'logo_icon' in locals(): screen.blit(logo_icon, (30, h-120))

        pygame.display.flip()
        
    return user_action

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mummy Maze - 25TNT1 - Dudes Chase Money")  

    action = open_lobby(screen)
    
    print(f"Action: {action}")

    pygame.time.delay(500)
    pygame.quit()
    sys.exit()