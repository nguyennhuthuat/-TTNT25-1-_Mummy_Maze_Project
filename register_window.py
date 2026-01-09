import pygame
import sys
from fonts import MetricFont

def open_register_window(screen):
    # --- 1. KHỞI TẠO FONT & MÀU SẮC ---
    try:
        input_font = pygame.font.SysFont("arial", 28) 
        label_font = pygame.font.SysFont("comic sans ms", 18)
        footer_font = pygame.font.SysFont("comic sans ms", 14)
        
        # Font cho nút bấm (headerfont)
        font_btn = MetricFont(font_name="headerfont", scale_height=40) 
        
        # Font cho tiêu đề
        font_title = MetricFont(font_name="font1", scale_height=50)

        # Font cho mô tả
        font_word = MetricFont(font_name="font1", scale_height=20)


    except Exception as e:
        input_font = pygame.font.Font(None, 32)
        label_font = pygame.font.Font(None, 20)
        footer_font = pygame.font.Font(None, 18)
        font_btn = pygame.font.Font(None, 50)
        font_title = pygame.font.Font(None, 60)

    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)
    HOVER_COLOR      = (255, 0, 0) 
    INPUT_TEXT_COLOR = (50, 50, 50) 

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # --- 2. LOAD ẢNH RESOURCE ---
    try:
        bg = pygame.image.load('./assets/images/background_window.png').convert()
        bg = pygame.transform.scale(bg, (w, h))
    except:
        bg = None
    
    try:
        logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        pass

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
    except:
        logo_img = None

    # --- 3. LOAD ẢNH KHUNG NHẬP LIỆU ---
    try:
        input_frame_img = pygame.image.load('./assets/images/register_frame.png').convert_alpha()
        input_frame_img = pygame.transform.scale(input_frame_img, (300, 50))
    except:
        input_frame_img = None
    
    # --- 4. ĐỊNH NGHĨA VỊ TRÍ ---
    # Block Shift cho các ô nhập liệu
    BLOCK_SHIFT_X = 0  
    BLOCK_SHIFT_Y = 200   

    anchor_x = center_x + BLOCK_SHIFT_X
    anchor_y = center_y + BLOCK_SHIFT_Y

    # [MỚI] Vị trí tiêu đề "REGISTER AN ACCOUNT" (Nằm trên Username 60px)
    pos_title = (anchor_x, anchor_y - 80)

    # Username Input
    rect_user_input = pygame.Rect(0, 0, 300, 50)
    rect_user_input.center = (anchor_x, anchor_y)

    # Password Input
    rect_pass_input = pygame.Rect(0, 0, 300, 50)
    rect_pass_input.center = (anchor_x, anchor_y + 80)

    # Vị trí nút bấm (Cố định Y)
    BUTTON_FIXED_Y = center_y + 300

    # Nút BACK (Góc Trái)
    pos_back = (center_x - 290, BUTTON_FIXED_Y)

    # Nút REGISTER (Góc Phải)
    pos_register = (center_x + 290, BUTTON_FIXED_Y)

    # --- 5. BIẾN TRẠNG THÁI ---
    username_text = ""
    password_text = ""
    active_field = None 

    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150)
    overlay.fill(COLOR_BG_OVERLAY)
    
    running = True
    result_data = None 

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # --- CẤU HÌNH NÚT BẤM ---
        buttons_config = [
            ("REGISTER", pos_register, "do_register"),
            ("GO BACK", pos_back, "go_back")
        ]

        active_buttons = []
        for text, pos, action in buttons_config:
            temp_surf = font_btn.render(text, True, TEXT_COLOR)
            rect = temp_surf.get_rect(center=pos)
            active_buttons.append((rect, text, action))

        # --- XỬ LÝ SỰ KIỆN ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_user_input.collidepoint(mouse_pos):
                    active_field = 'user'
                elif rect_pass_input.collidepoint(mouse_pos):
                    active_field = 'pass'
                else:
                    active_field = None 

                for rect, _, action in active_buttons:
                    if rect.collidepoint(mouse_pos):
                        if action == "go_back":
                            result_data = None 
                            running = False
                        elif action == "do_register":
                            if username_text and password_text: 
                                result_data = (username_text, password_text)
                                running = False
                            else:
                                print("Vui lòng nhập đầy đủ thông tin!")
            
            if event.type == pygame.KEYDOWN:
                if active_field is not None:
                    if event.key == pygame.K_RETURN:
                        if active_field == 'user':
                            active_field = 'pass'
                        elif active_field == 'pass':
                            if username_text and password_text:
                                result_data = (username_text, password_text)
                                running = False
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == 'user':
                            username_text = username_text[:-1]
                        else:
                            password_text = password_text[:-1]
                    else:
                        if active_field == 'user' and len(username_text) < 15:
                            username_text += event.unicode
                        elif active_field == 'pass' and len(password_text) < 15:
                            password_text += event.unicode

        # --- VẼ GIAO DIỆN ---
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill((100, 150, 100))
        screen.blit(overlay, (0, 0))

        if logo_img: screen.blit(logo_img, logo_rect)

        if board_img:
            screen.blit(board_img, board_rect)
        else:
            pygame.draw.rect(screen, (210, 180, 140), board_rect)
        
        if logo_img: screen.blit(logo_img, logo_rect)

        # Vẽ tiêu đề 
        title_surf = font_title.render("ACCOUNT", True, HOVER_COLOR)
        title_rect = title_surf.get_rect(center=pos_title)
        screen.blit(title_surf, title_rect)

        # 3. Vẽ Khung Nhập Liệu & Text
        # --- Username ---
        if input_frame_img:
            screen.blit(input_frame_img, rect_user_input)
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect_user_input)
            pygame.draw.rect(screen, (0,0,0), rect_user_input, 2)
        
        lbl_user = font_word.render("Username", True, TEXT_COLOR)
        screen.blit(lbl_user, (rect_user_input.x, rect_user_input.y - 20))

        display_user = username_text + ("|" if active_field == 'user' and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf_user = input_font.render(display_user, True, INPUT_TEXT_COLOR)
        screen.blit(txt_surf_user, (rect_user_input.x + 10, rect_user_input.centery - txt_surf_user.get_height()//2))

        # --- Password ---
        if input_frame_img:
            screen.blit(input_frame_img, rect_pass_input)
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect_pass_input)
            pygame.draw.rect(screen, (0,0,0), rect_pass_input, 2)

        lbl_pass = font_word.render("Password", True, TEXT_COLOR)
        screen.blit(lbl_pass, (rect_pass_input.x, rect_pass_input.y - 20))

        masked_pass = "*" * len(password_text) + ("|" if active_field == 'pass' and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf_pass = input_font.render(masked_pass, True, INPUT_TEXT_COLOR)
        screen.blit(txt_surf_pass, (rect_pass_input.x + 10, rect_pass_input.centery - txt_surf_pass.get_height()//2))

        # 4. Vẽ Các Nút
        for rect, text, _ in active_buttons:
            color = TEXT_COLOR
            if rect.collidepoint(mouse_pos):
                color = HOVER_COLOR
            
            txt_surf = font_btn.render(text, True, color)
            screen.blit(txt_surf, rect)

        # 5. Footer & Logo nhỏ
        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = w // 2, bottom = h)
        screen.blit(footer_text_surf, footer_text_rect)
        
        if 'logo_icon' in locals():
            screen.blit(logo_icon, (30, h - 120))

        pygame.display.flip()
        
    return result_data

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Register Window Test")  

    data = open_register_window(screen)
    
    if data:
        print(f"Registered successfully! Username: {data[0]}, Password: {data[1]}")
    else:
        print("Back to Lobby (Back clicked)")

    pygame.quit()
    sys.exit()