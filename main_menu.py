import pygame
import math
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 1. Import Pygame và Pygame Mixe để chèn nhạc ---
pygame.init()
pygame.mixer.init()

# Set display 
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 670
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mummy Maze - 25TNT1 - Dudes Chase Money")  

clock = pygame.time.Clock()

# --- 2. Set màu sắc và Font chữ ---
COLOR_BACKGROUND = (30, 30, 30)       # Màu nền 
COLOR_BUTTON = (139, 105, 20)         # Màu nút
COLOR_BUTTON_HOVER = (205, 92, 92)    # Màu nút khi di chuột qua
COLOR_TEXT = (255, 255, 255)      # Màu chữ

# Tải font chữ
try:
    main_font = pygame.font.SysFont("comic sans ms", 24) 
    footer_font = pygame.font.SysFont("comic sans ms", 14) 
    title_font = pygame.font.SysFont("Arial", 25, bold = True)
except Exception as e:
    main_font = pygame.font.Font(None, 36)
    footer_font = pygame.font.Font(None, 18) 
    title_font = pygame.font.Font(None, 52)

# --- TẢI ÂM THANH ---
try:
    # 1. Nhạc nền (Music) - Thường dùng cho nhạc dài
    pygame.mixer.music.load("./assets/music/game.it")
    pygame.mixer.music.set_volume(0.5) # Độ lớn từ 0.0 đến 1.0
    
    # 2. Hiệu ứng âm thanh (Sound) - Thường dùng cho tiếng động ngắn
    click_sound = pygame.mixer.Sound("./assets/sounds/click.ogg")
    finish_sound = pygame.mixer.Sound("./assets/sounds/click.ogg")
except Exception as e:
    print(f"Lỗi tải âm thanh: {e}")
    click_sound = None
    finish_sound = None

# Tải thanh loading
LOADING_BAR_X = 280 
LOADING_BAR_Y = 546 

# Kích thước mục tiêu
BAR_TARGET_WIDTH = 630
BAR_TARGET_HEIGHT = 22

try:
    # 1. Load ảnh gốc (340x24)
    img_orig = pygame.image.load("./assets/images/titlebar.png").convert_alpha()
    
    # 2. Kéo dài nó ra đúng kích thước khung rỗng (630x22)
    loading_bar_img = pygame.transform.scale(img_orig, (BAR_TARGET_WIDTH, BAR_TARGET_HEIGHT))
    
    # 3. Lưu lại kích thước mới để dùng cho hàm chạy
    loading_bar_w = BAR_TARGET_WIDTH
    loading_bar_h = BAR_TARGET_HEIGHT
    
except Exception as e:
    loading_bar_img = None
    print(f"Lỗi tải ảnh loading: {e}")

# --- 3. Class cho Button ---
class Button:
    
    def __init__(self, x, y, width, height, text='', image_path=None, hover_image_path=None, color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.mask = None
        
        # Tải hình ảnh cho nút
        self.image = None
        if image_path:
            try:
                img_orig = pygame.image.load(image_path).convert_alpha()
                orig_w, orig_h = img_orig.get_size()
                aspect_ratio = orig_w / orig_h
                # Tính width mới để giữ đúng tỉ lệ ảnh dựa trên height bạn nhập
                new_width = int(height * aspect_ratio)
                
                self.image = pygame.transform.scale(img_orig, (new_width, height))
                # Cập nhật rect khớp với kích thước ảnh thực tế
                self.rect = pygame.Rect(x, y, new_width, height)
                self.mask = pygame.mask.from_surface(self.image)
            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")

        self.hover_image = None
        if hover_image_path:
            try:
                h_orig = pygame.image.load(hover_image_path).convert_alpha()
                # Ép ảnh hover theo đúng kích thước rect đã tính
                self.hover_image = pygame.transform.scale(h_orig, (self.rect.width, self.rect.height))
            except Exception as e:
                print(f"Không tải được hình ảnh hover {hover_image_path}. Lỗi: {e}")
                
    def draw(self, surface):
        # Trường hợp 1: Có hình ảnh
        if self.image:
            surface.blit(self.image, self.rect.topleft)
            # Vẽ đè ảnh hover lên nếu đang hover
            if self.is_hovered and self.hover_image:
                surface.blit(self.hover_image, self.rect.topleft)
        
        # Trường hợp 2: Không có hình ảnh (hoặc ảnh lỗi), vẽ hình chữ nhật màu
        else:
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2) # Viền trắng
        
        # Luôn vẽ Text nếu có (để debug hoặc dùng cho nút không ảnh)
        if self.text != "":
            text_surf = main_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """Kiểm tra xem chuột có đang ở trên nút không (theo vùng hình chữ nhật)."""
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def is_clicked(self, event):
        """Kiểm tra xem nút có được nhấp chuột trái không."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

# --- 4. Tạo các nút ---
BTN_WIDTH = 200
BTN_HEIGHT = 50
GAP = 20        # Khoảng cách giữa các nút
OFFSET_X = 50   # Độ lệch ra hai bên so với tâm
OFFSET_Y = 170  # Độ lệch xuống dưới so với tâm màn hình (để vào giữa bảng đá)

center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
start_button = Button(
    0, # X tạm thời là 0
    center_y + 260, # Điều chỉnh số này để nút lên/xuống đúng vị trí bảng đá
    100, # Width 
    35,  # Height
    text="", 
    image_path="./assets/images/click_here_to_enter_button.png",
    hover_image_path="./assets/images/h_click_here_to_enter_button.png"
)

start_button.rect.centerx = SCREEN_WIDTH // 2

main_menu_buttons = [start_button]


def run_loading_screen():
    # Phát nhạc nền (số -1 có nghĩa là lặp vô tận)
    if pygame.mixer.music.get_busy() == False:
        pygame.mixer.music.play(-1)

    progress = 0
    loading = True

    # Hàm nội bộ để vẽ chữ sóng
    def draw_wave_text(surface, text, font, color, outline_color, start_pos):
        base_x, base_y = start_pos
        current_x = base_x
        
        time_now = pygame.time.get_ticks()

        for i, char in enumerate(text):
            # --- TOÁN HỌC CHO HIỆU ỨNG SÓNG ---
            bounce_y = math.sin(time_now * 0.01 + i * 0.5) * 3
            
            # Vị trí của từng chữ cái cụ thể
            char_pos = (current_x, base_y + bounce_y)

            # Vẽ viền cho từng chữ cái
            offsets = [(-2,0), (2,0), (0,-2), (0,2)]
            for ox, oy in offsets:
                char_outline = font.render(char, True, outline_color)
                surface.blit(char_outline, (char_pos[0] + ox, char_pos[1] + oy))

            # Vẽ chữ cái chính
            char_surf = font.render(char, True, color)
            surface.blit(char_surf, char_pos)

            # Cập nhật tọa độ X cho chữ cái tiếp theo
            current_x += font.size(char)[0]
    
    # Tải background để vẽ (cho giống menu)
    try:
        bg_img = pygame.image.load("./assets/images/mummymazedeluxetitle.png")
        bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg_img = None

    while loading:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if progress < 100:
            progress += 0.45
        else:
            if loading: # Chỉ phát 1 lần duy nhất khi vừa đầy
                if finish_sound: finish_sound.play()
            loading = False

        # Vẽ Background
        screen.fill(COLOR_BACKGROUND)
        if bg_img: screen.blit(bg_img, (0, 0))
        
        # Vẽ Logo (Nếu muốn)
        try:
            logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (130, 130))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))
        except:
            pass

        # 1. Vẽ Thanh Loading (Kéo dài 630x22)
        if loading_bar_img:
            current_w = int(BAR_TARGET_WIDTH * (progress / 100))
            if current_w > 0:
                screen.blit(loading_bar_img, (LOADING_BAR_X, LOADING_BAR_Y), (0, 0, current_w, BAR_TARGET_HEIGHT))

        # 2. VẼ CHỮ NHẢY KIỂU SÓNG TRUYỀN
        text_str = f"Loading... {int(progress)}%"
        
        start_x = 280 
        start_y = 546 - 45 # Cách bên trên thanh bar 45 pixel
        
        draw_wave_text(screen, text_str, title_font, (255, 255, 255), (0, 0, 0), (start_x, start_y))

        pygame.display.flip()

# --- 5. Vòng lặp chính ---
def main_menu():
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if start_button.is_clicked(event):
                if click_sound: 
                    click_sound.set_volume(1.0)
                    click_sound.play() # Phát tiếng click
                print("ACTION: Enter!")

        for button in main_menu_buttons:
            button.check_hover(mouse_pos)

        screen.fill(COLOR_BACKGROUND)

        try:
            background_image = pygame.image.load("./assets/images/mummymazedeluxetitle.png")
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(background_image, (0, 0))
        except:
            pass

        try:
            logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (130, 130))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))
        except:
            pass

        for button in main_menu_buttons: 
            button.draw(screen) 

        if loading_bar_img:
            # Vẽ trực tiếp ảnh đã scale vào đúng vị trí X, Y
            screen.blit(loading_bar_img, (LOADING_BAR_X, LOADING_BAR_Y))

        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_loading_screen()
    main_menu()