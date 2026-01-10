import pygame
import sys

try:
    from fonts import MetricFont
except ImportError:
    class MetricFont:
        def __init__(self, font_name, scale_height):
            self.font = pygame.font.Font(None, scale_height)
        def render(self, text, antialias, color):
            return self.font.render(text, antialias, color)

def open_register_window(screen):
    # --- 1. KHỞI TẠO FONT & MÀU SẮC ---
    try:
        input_font = pygame.font.SysFont("arial", 28)
        # Font cho nút bấm
        font_btn = MetricFont(font_name="headerfont", scale_height=40)
        # Font cho tiêu đề lớn
        font_title = MetricFont(font_name="font1", scale_height=30)
        # Font cho label nhỏ (Enter In-game Name)
        font_word = MetricFont(font_name="font1", scale_height=20)
        # Font cho dòng chú thích rank chart
        font_note = pygame.font.SysFont("comic sans ms", 16, italic=True) 
        # Font footer
        footer_font = pygame.font.SysFont("comic sans ms", 14)

    except:
        input_font = pygame.font.Font(None, 32)
        font_btn = pygame.font.Font(None, 50)
        font_title = pygame.font.Font(None, 60)
        font_word = pygame.font.Font(None, 30)
        font_note = pygame.font.Font(None, 20)
        footer_font = pygame.font.Font(None, 18)

    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)
    HOVER_COLOR      = (255, 0, 0)
    INPUT_TEXT_COLOR = (50, 50, 50)
    NOTE_COLOR       = (80, 60, 50) # Màu cho dòng chú thích (nhạt hơn chút)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # --- 2. LOAD ẢNH RESOURCE ---
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

    try:
        input_frame_img = pygame.image.load('./assets/images/input_frame.png').convert_alpha()
        input_frame_img = pygame.transform.scale(input_frame_img, (300, 50))
    except: input_frame_img = None

    # --- 3. ĐỊNH NGHĨA VỊ TRÍ ---
    
    # Dịch chuyển khối nhập liệu. 
    IGN_SHIFT_X = 0    
    IGN_SHIFT_Y = 200 

    anchor_ign_x = center_x + IGN_SHIFT_X
    anchor_ign_y = center_y + IGN_SHIFT_Y

    # Vị trí ô nhập In-game Name
    rect_ign_input = pygame.Rect(0, 0, 300, 50)
    rect_ign_input.center = (anchor_ign_x, anchor_ign_y) 

    # Vị trí tiêu đề "CHARACTER NAME"
    pos_title = (anchor_ign_x, anchor_ign_y - 80)
    
    # Vị trí nút bấm (Cố định ở dưới đáy window)
    BUTTON_FIXED_Y = center_y + 200 # Đẩy lên một chút cho gọn
    pos_back = (center_x - 300, BUTTON_FIXED_Y + 100)
    pos_confirm = (center_x + 300, BUTTON_FIXED_Y + 100)

    # --- 4. LOGIC LOOP ---
    ign_text = ""
    active = True # Mặc định focus vào ô này luôn
    
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150)
    overlay.fill(COLOR_BG_OVERLAY)

    running = True
    final_ign = None

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        buttons_config = [
            ("CONFIRM", pos_confirm, "do_confirm"),
            ("BACK", pos_back, "go_back")
        ]
        
        # --- XỬ LÝ SỰ KIỆN ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_ign_input.collidepoint(mouse_pos):
                    active = True
                else:
                    active = False
                
                # Check nút bấm
                for text, pos, action in buttons_config:
                    temp_surf = font_btn.render(text, True, TEXT_COLOR)
                    btn_rect = temp_surf.get_rect(center=pos)
                    if btn_rect.collidepoint(mouse_pos):
                        if action == "go_back":
                            running = False 
                        elif action == "do_confirm":
                            if len(ign_text) > 0:
                                final_ign = ign_text
                                running = False
            
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if len(ign_text) > 0:
                            final_ign = ign_text
                            running = False
                    elif event.key == pygame.K_BACKSPACE:
                        ign_text = ign_text[:-1]
                    else:
                        if len(ign_text) < 12: # Giới hạn 12 ký tự
                            ign_text += event.unicode

        # --- VẼ GIAO DIỆN ---
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill((100, 150, 100))
        screen.blit(overlay, (0, 0))

        # Vẽ bảng (Board)
        if board_img: screen.blit(board_img, board_rect)
        else: pygame.draw.rect(screen, (210, 180, 140), board_rect)
        
        # Vẽ Logo lớn (Menu Logo)
        if logo_img: screen.blit(logo_img, logo_rect)
        # Vẽ Logo nhỏ góc trái
        if 'logo_icon' in locals(): screen.blit(logo_icon, (30, h - 120))

        # 1. Tiêu đề
        title_surf = font_title.render("CHARACTER NAME", True, HOVER_COLOR)
        title_rect = title_surf.get_rect(center=pos_title)
        screen.blit(title_surf, title_rect)

        # 2. Ô nhập liệu
        if input_frame_img:
            screen.blit(input_frame_img, rect_ign_input)
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect_ign_input)
            pygame.draw.rect(screen, (0,0,0), rect_ign_input, 2)
        
        # Label "Enter Name" (nhỏ phía trên ô nhập)
        lbl_ign = font_word.render("Enter In-Game Name", True, TEXT_COLOR)
        screen.blit(lbl_ign, (rect_ign_input.x, rect_ign_input.y - 25))

        # Text người dùng nhập
        display_text = ign_text + ("|" if active and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf = input_font.render(display_text, True, INPUT_TEXT_COLOR)
        # Căn giữa text theo chiều dọc (center Y) và cách lề trái 10px
        screen.blit(txt_surf, (rect_ign_input.x + 15, rect_ign_input.centery - txt_surf.get_height()//2))

        # [MỚI] 3. Dòng chú thích Rank Chart
        note_text = "This name is used for displaying with your rank on the chart."
        note_surf = font_note.render(note_text, True, NOTE_COLOR)
        # Đặt ngay dưới ô nhập liệu 10 pixel
        note_rect = note_surf.get_rect(centerx=rect_ign_input.centerx, top=rect_ign_input.bottom + 10)
        screen.blit(note_surf, note_rect)

        # 4. Vẽ nút (Confirm / Back)
        for text, pos, action in buttons_config:
            temp_surf = font_btn.render(text, True, TEXT_COLOR)
            rect = temp_surf.get_rect(center=pos)
            color = HOVER_COLOR if rect.collidepoint(mouse_pos) else TEXT_COLOR
            real_surf = font_btn.render(text, True, color)
            screen.blit(real_surf, rect)

        # 5. Footer
        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = w // 2, bottom = h - 10)
        screen.blit(footer_text_surf, footer_text_rect)

        pygame.display.flip()

    return final_ign

# --- HÀM MAIN ĐỂ CHẠY THỬ ---
if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("In-Game Name Input")   

    # Gọi hàm nhập tên
    ingame_name = open_register_window(screen)
    
    if ingame_name:
        print(f"Success! Player Name: {ingame_name}")
    else:
        print("User cancelled (Clicked Back or Close).")

    pygame.quit()
    sys.exit()