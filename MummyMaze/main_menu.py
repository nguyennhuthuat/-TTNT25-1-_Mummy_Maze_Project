import pygame
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 1. Import Pygame và tạo settings ---
pygame.init()

# Set display 
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
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
    footer_font = pygame.font.SysFont("comic sans ms", 14) # Thêm dòng này (size 14 thay vì 24)
    title_font = pygame.font.SysFont("comic sans ms", 50)
except Exception as e:
    main_font = pygame.font.Font(None, 36)
    footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
    title_font = pygame.font.Font(None, 52)

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
        """Kiểm tra xem chuột có đang ở trên nút không."""
        if self.mask:
            self.is_hovered = False 
            if self.rect.collidepoint(mouse_pos):
                relative_x = mouse_pos[0] - self.rect.x
                relative_y = mouse_pos[1] - self.rect.y
                if (0 <= relative_x < self.mask.get_size()[0]) and (0 <= relative_y < self.mask.get_size()[1]):
                    if self.mask.get_at((relative_x, relative_y)):
                        self.is_hovered = True
        else:
            # Nếu chỉ có text, tính hover dựa trên rect của text để khít
            text_surf = main_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            self.is_hovered = text_rect.collidepoint(mouse_pos)

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
    center_y + 235, # Điều chỉnh số này để nút lên/xuống đúng vị trí bảng đá
    100, # Width 
    35,  # Height
    text="", 
    image_path="./main_menu_assets/click_here_to_enter_button.png",
    hover_image_path="./main_menu_assets/h_click_here_to_enter_button.png"
)

start_button.rect.centerx = SCREEN_WIDTH // 2

main_menu_buttons = [start_button]

# Tạo các icon bên phải
'''ICON_SIZE = 90
ICON_X = SCREEN_WIDTH - ICON_SIZE - 15 
setting_icon = Button(ICON_X, 100, ICON_SIZE, ICON_SIZE, "", 
                      image_path="main_menu_assets/setting_icon.png",
                      hover_image_path="main_menu_assets/h_setting_icon.png")
account_icon = Button(ICON_X, 175, ICON_SIZE, ICON_SIZE, "", 
                      image_path="main_menu_assets/account_icon.png",
                      hover_image_path="main_menu_assets/h_account_icon.png")
sound_icon = Button(ICON_X, 250, ICON_SIZE, ICON_SIZE, "", 
                    image_path="main_menu_assets/sound_icon.png",
                    hover_image_path="main_menu_assets/h_sound_icon.png")
lang_icon = Button(ICON_X, 325, ICON_SIZE, ICON_SIZE, "", 
                   image_path="main_menu_assets/language_icon.png",
                   hover_image_path="main_menu_assets/h_language_icon.png")

icon_buttons = [account_icon, sound_icon, lang_icon, setting_icon]'''

# --- 5. Vòng lặp chính ---
def main_menu():
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if start_button.is_clicked(event):
                print("ACTION: Enter!")
            '''if quit_button.is_clicked(event):
                pygame.quit()
                sys.exit()'''

        for button in main_menu_buttons:
            button.check_hover(mouse_pos)
        '''+ icon_buttons:'''

        screen.fill(COLOR_BACKGROUND)
        try:
            background_image = pygame.image.load("./main_menu_assets/mummymazedeluxetitle.png")
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(background_image, (0, 0))
        except:
            pass

        try:
            logo_image = pygame.image.load("main_menu_assets/MummyMaze_logo.png").convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (160, 160))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 150))
        except:
            pass

        for button in main_menu_buttons: 
            button.draw(screen) 
        '''+ icon_buttons'''

        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()