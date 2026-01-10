import pygame
import sys
# Đảm bảo file fonts.py nằm cùng thư mục
from fonts import MetricFont 

# --- CÁC BIẾN TOÀN CỤC ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 670
COLOR_BG_OVERLAY = (0, 0, 0)
TEXT_COLOR       = (40, 20, 10)
HOVER_COLOR      = (255, 0, 0)
SCROLLBAR_COLOR  = (150, 100, 50)
SCROLLBAR_BG     = (200, 180, 160)

def open_switch_account_window(screen, account_list):
    # --- [TEST MODE] ---
    if len(account_list) < 6:
        test_list = account_list + [f"User_Test_{i}" for i in range(1, 10)]
    else:
        test_list = account_list
    # -------------------

    # --- 1. KHỞI TẠO FONT ---
    try:
        font_header = MetricFont(font_name="headerfont", scale_height=40)
        font_title = MetricFont(font_name="headerfont", scale_height=25)
        font_username = pygame.font.SysFont('comic sans ms', 20) 
        footer_font = pygame.font.SysFont("arial", 14)
    except Exception as e:
        font_header = pygame.font.Font(None, 40)
        font_title = pygame.font.Font(None, 35)
        font_username = pygame.font.Font(None, 35)
        footer_font = pygame.font.Font(None, 18)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # --- 2. LOAD RESOURCE ---
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

    # =========================================================================
    # --- 3. THIẾT LẬP VỊ TRÍ & SCROLL (CÓ BIẾN ĐIỀU CHỈNH) ---
    # =========================================================================
    
    # Kích thước khung danh sách
    list_w = 200
    list_h = 180 
    
    # >>>>> BIẾN TRUNG GIAN ĐỂ DỊCH CHUYỂN DANH SÁCH & SCROLLBAR <<<<<
    # Tăng Y: Dịch xuống | Giảm Y: Dịch lên
    # Tăng X: Dịch phải  | Giảm X: Dịch trái
    LIST_OFFSET_X = 0   
    LIST_OFFSET_Y = 130
    
    # Tính toán vị trí dựa trên tâm + biến offset
    list_x = (center_x - list_w // 2) + LIST_OFFSET_X
    list_y = center_y + LIST_OFFSET_Y
    
    list_rect_clip = pygame.Rect(list_x, list_y, list_w, list_h)
    
    item_height = 50 
    total_content_height = len(test_list) * item_height 
    
    scroll_y = 0
    max_scroll = max(0, total_content_height - list_h)
    
    dragging_scrollbar = False
    mouse_y_offset = 0
    
    running = True
    result = None 

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        
        # --- LOGIC SCROLLBAR ---
        scrollbar_w = 12
        # Scrollbar tự động bám theo list_x và list_y
        scrollbar_x = list_x + list_w + 5
        scrollbar_h = list_h
        
        safe_max_scroll = max_scroll if max_scroll > 0 else 1

        if total_content_height > list_h:
            thumb_h = max(30, int((list_h / total_content_height) * list_h))
            thumb_y = list_y + (scroll_y / safe_max_scroll) * (list_h - thumb_h)
        else:
            thumb_h = list_h
            thumb_y = list_y
            
        scrollbar_rect = pygame.Rect(scrollbar_x, list_y, scrollbar_w, scrollbar_h)
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_w, thumb_h)

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEWHEEL:
                # Chỉ cuộn khi chuột nằm trong vùng list hoặc scrollbar
                # (Optional: giúp UX tốt hơn)
                if list_rect_clip.collidepoint(mouse_pos) or scrollbar_rect.collidepoint(mouse_pos):
                    scroll_y -= event.y * 20
                    scroll_y = max(0, min(scroll_y, max_scroll))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    # 1. Click Scrollbar
                    if thumb_rect.collidepoint(mouse_pos) and total_content_height > list_h:
                        dragging_scrollbar = True
                        mouse_y_offset = mouse_y - thumb_y
                    elif scrollbar_rect.collidepoint(mouse_pos) and total_content_height > list_h:
                        ratio = (mouse_y - list_y) / list_h
                        scroll_y = ratio * max_scroll
                        scroll_y = max(0, min(scroll_y, max_scroll))

                    # 2. Click User List
                    elif list_rect_clip.collidepoint(mouse_pos):
                        relative_y = (mouse_y - list_y) + scroll_y
                        index = int(relative_y // item_height)
                        if 0 <= index < len(test_list):
                            result = ("select", test_list[index])
                            running = False

                    # 3. Click Buttons (Giữ nguyên vị trí cũ hoặc chỉnh riêng nếu cần)
                    btn_y_pos = center_y + 300 
                    
                    # Nút Register
                    temp_surf = font_header.render("NEW ACCOUNT", True, TEXT_COLOR)
                    btn_reg_rect = temp_surf.get_rect(center=(center_x + 290, btn_y_pos))
                    if btn_reg_rect.collidepoint(mouse_pos):
                        result = ("goto_register", None)
                        running = False
                    
                    # Nút Back
                    temp_surf_back = font_header.render("GO BACK", True, TEXT_COLOR)
                    btn_back_rect = temp_surf_back.get_rect(center=(center_x - 290, btn_y_pos))
                    if btn_back_rect.collidepoint(mouse_pos):
                        result = ("back", None)
                        running = False

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_scrollbar = False
                
            if event.type == pygame.MOUSEMOTION:
                if dragging_scrollbar and max_scroll > 0:
                    new_thumb_y = mouse_y - mouse_y_offset
                    scroll_ratio = (new_thumb_y - list_y) / (list_h - thumb_h)
                    scroll_y = scroll_ratio * max_scroll
                    scroll_y = max(0, min(scroll_y, max_scroll))

        # --- DRAWING ---
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill((100, 150, 100))
        screen.blit(overlay, (0, 0))

        if board_img: screen.blit(board_img, board_rect)
        else: pygame.draw.rect(screen, (210, 180, 140), board_rect)
        
        if logo_img: screen.blit(logo_img, logo_rect)

        # Tiêu đề (VỊ TRÍ CỐ ĐỊNH - KHÔNG BỊ ẢNH HƯỞNG BỞI OFFSET)
        title_text = "SELECT ACCOUNT"
        title_surf = font_title.render(title_text, True, HOVER_COLOR)
        # Vẫn dùng center_y gốc để giữ nguyên vị trí
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 90 + 200))) 

        # --- VẼ DANH SÁCH ---
        old_clip = screen.get_clip()
        screen.set_clip(list_rect_clip)
        
        start_index = int(scroll_y // item_height)
        end_index = start_index + int(list_h // item_height) + 2
        
        for i in range(start_index, min(end_index, len(test_list))):
            name = test_list[i]
            # y_pos tự động tính theo list_y (đã có offset)
            y_pos = list_y + (i * item_height) - scroll_y
            
            # Tính Rect
            item_rect = pygame.Rect(list_x, y_pos, list_w, item_height)
            is_hovered = item_rect.collidepoint(mouse_pos) and list_rect_clip.collidepoint(mouse_pos)
            c_color = HOVER_COLOR if is_hovered else TEXT_COLOR
            
            name_surf = font_username.render(name, True, c_color)
            name_rect = name_surf.get_rect(center=(center_x + LIST_OFFSET_X, y_pos + item_height//2))
            screen.blit(name_surf, name_rect)

        screen.set_clip(old_clip)

        # Vẽ Scrollbar 
        if total_content_height > list_h:
            pygame.draw.rect(screen, SCROLLBAR_BG, scrollbar_rect, border_radius=5)
            pygame.draw.rect(screen, SCROLLBAR_COLOR, thumb_rect, border_radius=5)

        # --- VẼ NÚT ---
        btn_y_pos = center_y + 300

        # Nút Register
        reg_txt = "NEW ACCOUNT"
        reg_surf_temp = font_header.render(reg_txt, True, TEXT_COLOR) 
        reg_rect = reg_surf_temp.get_rect(center=(center_x + 270, btn_y_pos))
        
        reg_col = HOVER_COLOR if reg_rect.collidepoint(mouse_pos) else TEXT_COLOR
        reg_surf = font_header.render(reg_txt, True, reg_col)
        screen.blit(reg_surf, reg_rect)

        # Nút Back
        back_txt = "GO BACK"
        back_surf_temp = font_header.render(back_txt, True, TEXT_COLOR)
        back_rect = back_surf_temp.get_rect(center=(center_x - 290, btn_y_pos))
        
        back_col = HOVER_COLOR if back_rect.collidepoint(mouse_pos) else TEXT_COLOR
        back_surf = font_header.render(back_txt, True, back_col)
        screen.blit(back_surf, back_rect)

        # Footer
        footer_text = footer_font.render("Version 1.0.1 | © 25TNT1", True, TEXT_COLOR)
        screen.blit(footer_text, footer_text.get_rect(centerx=w//2, bottom=h))
        
        pygame.display.flip()

    return result