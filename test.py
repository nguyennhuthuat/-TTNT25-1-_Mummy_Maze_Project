import pygame

# 1. Khởi tạo
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Tải ảnh nền hoặc tự vẽ gì đó để test
bg_color = (0, 120, 0) # Màu xanh cỏ
player_rect = pygame.Rect(WIDTH//2, HEIGHT//2, 30, 30)

# --- PHẦN QUAN TRỌNG NHẤT ---
def draw_spotlight(surface, pos, radius):
    # Bước 1: Tạo một lớp phủ (mask) có hỗ trợ độ trong suốt (SRCALPHA)
    # Kích thước bằng màn hình
    darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Bước 2: Tô đen lớp phủ này (Độ mờ tuỳ chỉnh, ở đây là 255 - tối đen)
    # Nếu muốn mờ mờ kiểu trời tối (vẫn thấy đường) thì để khoảng 200
    darkness.fill((0, 0, 0, 255)) 
    
    # Bước 3: "Đục lỗ"
    # Vẽ một hình tròn trong suốt (alpha = 0) tại vị trí pos
    # BLEND_RGBA_MIN: Sẽ lấy giá trị alpha thấp nhất giữa lớp phủ (255) và hình tròn (0)
    # Kết quả -> Vùng giao nhau sẽ có alpha = 0 (nhìn xuyên qua được)
    pygame.draw.circle(darkness, (0, 0, 0, 0), pos, radius)
    
    # Bước 4: Vẽ lớp phủ đã đục lỗ lên màn hình chính
    # Dùng cờ BLEND_RGBA_MIN để áp dụng phép trừ alpha
    surface.blit(darkness, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

# Vòng lặp game
running = True
while running:
    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Lấy vị trí chuột (để làm đèn pin)
    mouse_pos = pygame.mouse.get_pos()

    # --- VẼ ---
    # 1. Vẽ thế giới game trước
    screen.fill(bg_color) 
    pygame.draw.rect(screen, (255, 0, 0), player_rect) # Vẽ nhân vật màu đỏ
    
    # Vẽ vài hình lung tung để thấy hiệu ứng
    pygame.draw.rect(screen, (0, 0, 255), (100, 100, 50, 50))
    pygame.draw.rect(screen, (255, 255, 0), (600, 400, 80, 80))

    # 2. Vẽ hiệu ứng đèn pin đè lên trên cùng
    draw_spotlight(screen, mouse_pos, 150) # Bán kính 150

    pygame.display.flip()
    clock.tick(60)

pygame.quit()