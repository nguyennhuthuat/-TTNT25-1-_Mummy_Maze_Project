import pygame
import sys

def open_lose_window(screen):

    font_btn = pygame.font.SysFont('Arial', 22, bold=True)
    font_title = pygame.font.SysFont('Arial', 40, bold=True)
    
    COLOR_BG_OVERLAY = (0, 0, 0)
    COLOR_BORDER     = (60, 40, 20)
    COLOR_BTN        = (190, 160, 110)
    COLOR_BTN_HOVER  = (230, 200, 150)
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    #TẢI ẢNH lên
    try:
        board_img = pygame.image.load('./MummyMaze/lose_window_assets/menufront.png').convert()
        
        scale_factor = 1.22
    
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
    
        board_img = pygame.transform.scale(board_img, (new_w, new_h))
        
        board_w, board_h = board_img.get_size()

    except pygame.error as e:
        print(f"Lỗi tải ảnh: {e}")
        # Nếu lỗi tải ảnh, quay lại dùng hình chữ nhật như trước 
        board_img = None
        COLOR_BOARD = (210, 180, 140) # Màu cát (nếu không có ảnh)
        board_w, board_h = 500, 300 # Kích thước mặc định

    # Menu thông báo chính (Định vị DÙNG KÍCH THƯỚC CỦA ẢNH)
    board_rect = board_img.get_rect() if board_img else pygame.Rect(0, 0, board_w, board_h)
    board_rect.center = (center_x, center_y + 10)


    # --- Định vị các nút bấm (Phần này không đổi) ---
    btn_w, btn_h = 200, 50
    gap = 20 

    rect_retry = pygame.Rect(0, 0, btn_w, btn_h)
    rect_retry.bottomright = (center_x - gap//2 - 50, center_y + 170)
    
    rect_abandon = pygame.Rect(0, 0, btn_w, btn_h)
    rect_abandon.bottomleft = (center_x + gap//2 + 50, center_y + 170)

    rect_undo = pygame.Rect(0, 0, btn_w, btn_h)
    rect_undo.topright = (center_x - gap//2 - 50, center_y + 170 + gap)

    rect_quit = pygame.Rect(0, 0, btn_w, btn_h)
    rect_quit.topleft = (center_x + gap//2 + 50, center_y + 170 + gap)

    # Tạo lớp phủ mờ
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180) 
    overlay.fill(COLOR_BG_OVERLAY)
    
    # --- VÒNG LẶP RIÊNG CỦA CỬA SỔ THUA ---
    running = True
    user_action = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if rect_retry.collidepoint(mouse_pos):
                        user_action = "retry"
                        running = False
                    elif rect_undo.collidepoint(mouse_pos):
                        user_action = "undo"
                        running = False
                    elif rect_abandon.collidepoint(mouse_pos):
                        user_action = "abandon"
                        running = False
                    elif rect_quit.collidepoint(mouse_pos):
                        user_action = "quit"
                        running = False

        
        # 1. Vẽ lớp phủ tối màu
        screen.blit(overlay, (0, 0))

        # VẼ BẢNG THÔNG BÁO (GAME OVER)
        if board_img:
            # Nếu tải ảnh thàh công, vẽ ảnh
            screen.blit(board_img, board_rect)
        else:
            pygame.draw.rect(screen, COLOR_BOARD, board_rect, border_radius=15)
            pygame.draw.rect(screen, COLOR_BORDER, board_rect, 6, border_radius=15)
            # Thêm tiêu đề Game Over khi không có ảnh nền đẹp
            text_title_surf = font_title.render("GAME OVER", True, TEXT_COLOR)
            title_rect = text_title_surf.get_rect(center=(center_x, center_y - 20))
            screen.blit(text_title_surf, title_rect)


        # Vẽ các nút bấm 
        buttons = [
            (rect_retry, "TRY AGAIN"),
            (rect_abandon, "ABANDON HOPE"),
            (rect_undo, "UNDO MOVE"),
            (rect_quit, "SAVE AND QUIT")
        ]

        for rect, text in buttons:
            color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
            
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_BORDER, rect, 3, border_radius=8)
            
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        
    return user_action

if __name__ == "__main__":
    pygame.init()

    COLOR_TEXT = (255, 255, 255)   

    # 1. Thiết lập cửa sổ chính
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lose Window")

    try:
        main_font = pygame.font.SysFont("comic sans ms", 10)
        title_font = pygame.font.SysFont("comic sans ms", 50)
    except Exception as e:
        print(f"Không tìm thấy font, dùng font mặc định. Lỗi: {e}")
        main_font = pygame.font.Font(None, 36) # Font mặc định nếu có lỗi
        title_font = pygame.font.Font(None, 52)
    
    footer_text_surf = main_font.render("Version 1.0.3 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT)
    footer_text_rect = footer_text_surf.get_rect(
        centerx = SCREEN_WIDTH // 2,      # Căn giữa theo chiều ngang
        bottom = SCREEN_HEIGHT - 15       # Cách lề dưới 
        )

    screen.blit(footer_text_surf, footer_text_rect)

    clock = pygame.time.Clock()

    # 2. Vòng lặp game chính (Chỉ chạy một lần để hiển thị game background)
    # Background game giả lập
    screen.fill((100, 150, 100)) 
    pygame.draw.circle(screen, (200, 50, 50), (100, 100), 50) 
    pygame.draw.rect(screen, (50, 50, 200), (500, 400, 150, 100))
    pygame.display.flip()
    
    # GỌI HÀM CỬA SỔ POP-UP
    print("Opening Game Over window...")
    action = open_lose_window(screen)

    # Kết quả trả về và thoát
    print(f"The player chose: {action}")

    pygame.time.delay(500)
    pygame.quit()
    sys.exit()