import pygame

# --- KHỞI TẠO ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hiệu ứng Đèn Pin - Demo")
clock = pygame.time.Clock()

# --- HÀM VẼ ĐÈN PIN (Masking) ---
def draw_spotlight(surface, pos, radius):
    # pygame.SRCALPHA cho phép tạo surface với kênh alpha (độ trong suốt)
    mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 255)) 

    hole = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(hole, (255, 255, 255, 255), pos, radius)

    # special_flags=pygame.BLEND_RGBA_SUB sẽ trừ màu trắng (255) khỏi mask, tạo lỗ hổng trong suốt
    mask.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surface.blit(mask, (0, 0))

# --- VÒNG LẶP GAME ---
running = True
while running:
    # 1. Xử lý sự kiện thoát
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Lấy vị trí chuột
    mouse_pos = pygame.mouse.get_pos()

    # 3. VẼ MỌI THỨ
    # BƯỚC QUAN TRỌNG: Tô nền màu SÁNG (để thấy hiệu ứng đục lỗ)
    screen.fill((50, 150, 50)) # Màu xanh lá cây
    
    # Vẽ vài hình lung tung làm nền để nhìn cho rõ
    pygame.draw.rect(screen, (255, 0, 0), (200, 200, 100, 100)) # Hình vuông Đỏ
    pygame.draw.rect(screen, (0, 0, 255), (500, 300, 80, 150))  # Hình chữ nhật Xanh Dương
    pygame.draw.circle(screen, (255, 255, 0), (400, 300), 50)   # Hình tròn Vàng giữa màn hình

    # 4. GỌI HÀM VẼ ĐÈN PIN (Vẽ cuối cùng để nó đè lên tất cả)
    draw_spotlight(screen, mouse_pos, 150) # Bán kính 150 pixel

    # 5. Cập nhật màn hình
    pygame.display.flip()
    clock.tick(60)

pygame.quit()