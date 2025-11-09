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
COLOR_BUTTON_HOVER = (205, 92, 92)   # Màu nút khi di chuột qua
COLOR_TEXT = (255, 255, 255)      # Màu chữ

# Tải font chữ
try:
    main_font = pygame.font.SysFont("comic sans ms", 10)
    title_font = pygame.font.SysFont("comic sans ms", 50)
except Exception as e:
    print(f"Không tìm thấy font, dùng font mặc định. Lỗi: {e}")
    main_font = pygame.font.Font(None, 36) # Font mặc định nếu có lỗi
    title_font = pygame.font.Font(None, 52)

# --- 3. Class cho Button ---
class Button:
    """Lớp tổng quát cho tất cả các nút có thể nhấp chuột."""
    
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
                self.image = pygame.image.load(image_path).convert_alpha()
                # Co giãn hình ảnh vừa với kích thước nút
                self.image = pygame.transform.scale(self.image, (width, height))
                self.mask = pygame.mask.from_surface(self.image)
            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")

        self.hover_image = None
        if hover_image_path:
            try:
                self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
                self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
            except Exception as e:
                print(f"Không tải được hình ảnh hover {hover_image_path}. Lỗi: {e}")
                
    def draw(self, surface):
        """Vẽ nút lên một bề mặt (surface) nhất định."""
        #current_color = self.hover_color if self.is_hovered else self.color
        
        # 1. Ưu tiên vẽ ảnh hover nếu đang được hover và có ảnh hover
        if self.is_hovered and self.hover_image:
            surface.blit(self.hover_image, self.rect.topleft)
            
        # 2. Nếu không, vẽ ảnh bình thường 
        elif self.image:
            surface.blit(self.image, self.rect.topleft)
            
        # 3. Nếu không có ảnh nào, vẽ hình chữ nhật và text 
        else:
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
            
            if self.text != '':
                text_surf = main_font.render(self.text, True, COLOR_TEXT)
                text_rect = text_surf.get_rect(center=self.rect.center)
                surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """Kiểm tra xem chuột có đang ở trên nút không."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.mask:
            self.is_hovered = False 
            
            if self.rect.collidepoint(mouse_pos):
                
                relative_x = mouse_pos[0] - self.rect.x
                relative_y = mouse_pos[1] - self.rect.y
                
                if (0 <= relative_x < self.mask.get_size()[0]) and (0 <= relative_y < self.mask.get_size()[1]):
                    if self.mask.get_at((relative_x, relative_y)):
                        self.is_hovered = True
        
        # nếu không có ảnh
        else:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """Kiểm tra xem nút có được nhấp chuột trái không."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

# --- 4. Tạo các nút ---
BTN_WIDTH = 180
BTN_HEIGHT = 190
BTN_MARGIN = -110 # Khoảng cách giữa các nút

BTN_START_X = (SCREEN_WIDTH - BTN_WIDTH) // 2
total_height = ((BTN_HEIGHT * 4) + (BTN_MARGIN * 3)) // 1
BTN_START_Y = (SCREEN_HEIGHT - total_height) // 2 + 100

start_button = Button(BTN_START_X, BTN_START_Y, BTN_WIDTH, BTN_HEIGHT, 
                      image_path="main_menu_assets/start_icon.png",
                      hover_image_path="main_menu_assets/h_start_icon.png")
badges_button = Button(BTN_START_X, BTN_START_Y + (BTN_HEIGHT + BTN_MARGIN) * 1, BTN_WIDTH, BTN_HEIGHT, 
                       image_path="main_menu_assets/badges_icon.png",
                       hover_image_path="main_menu_assets/h_badges_icon.png")
guides_button = Button(BTN_START_X, BTN_START_Y + (BTN_HEIGHT + BTN_MARGIN) * 2, BTN_WIDTH, BTN_HEIGHT, 
                       image_path="main_menu_assets/guides_icon.png",
                       hover_image_path="main_menu_assets/h_guides_icon.png")
story_button = Button(BTN_START_X, BTN_START_Y + (BTN_HEIGHT + BTN_MARGIN) * 3, BTN_WIDTH, BTN_HEIGHT, 
                      image_path="main_menu_assets/story_icon.png",
                      hover_image_path="main_menu_assets/h_story_icon.png")
# Danh sách các nút chính
main_menu_buttons = [start_button, badges_button, guides_button, story_button]

# Tạo các icon bên phải
ICON_SIZE = 90
ICON_X = SCREEN_WIDTH - ICON_SIZE - 15 # Căn lề phải
setting_icon = Button(ICON_X, 50, ICON_SIZE, ICON_SIZE, "", 
                      image_path="main_menu_assets/setting_icon.png",
                      hover_image_path="main_menu_assets/h_setting_icon.png")
account_icon = Button(ICON_X, 150, ICON_SIZE, ICON_SIZE, "", 
                      image_path="main_menu_assets/account_icon.png",
                      hover_image_path="main_menu_assets/h_account_icon.png")
sound_icon = Button(ICON_X, 250, ICON_SIZE, ICON_SIZE, "", 
                    image_path="main_menu_assets/sound_icon.png",
                    hover_image_path="main_menu_assets/h_sound_icon.png")
lang_icon = Button(ICON_X, 350, ICON_SIZE, ICON_SIZE, "", 
                   image_path="main_menu_assets/language_icon.png",
                   hover_image_path="main_menu_assets/h_language_icon.png")

icon_buttons = [account_icon, sound_icon, lang_icon, setting_icon]

# --- 5. Vòng lặp chính ---
def main_menu():
    """Hàm chạy vòng lặp chính của menu."""
    while True:
        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()

        # 1. Xử lý Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Kiểm tra sự kiện click cho từng nút
            if start_button.is_clicked(event):
                print("ACTION: Start the game!")
            
            if badges_button.is_clicked(event):
                print("ACTION: Let's see your achievements!")

            if story_button.is_clicked(event):
                print("ACTION: Let's read the plots!")

            if sound_icon.is_clicked(event):
                print("ACTION: On/Off the sound!")

        # 2. Cập nhật trạng thái (Update)
        # Cập nhật trạng thái hover cho tất cả các nút
        for button in main_menu_buttons + icon_buttons:
            button.check_hover(mouse_pos)

        # 3. Vẽ lên màn hình (Render)
        
        # Nền
        screen.fill(COLOR_BACKGROUND)
        background_image = pygame.image.load("main_menu_assets/background.png")
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(background_image, (0, 0))

        # Tải logo
        try:
            logo_image = pygame.image.load("main_menu_assets/MummyMaze_logo.png").convert_alpha()
    
            LOGO_WIDTH = 250
            LOGO_HEIGHT = 250

            logo_icon = pygame.transform.scale(logo_image, (LOGO_WIDTH, LOGO_HEIGHT))

            # Vị trí logo
            logo_rect = logo_icon.get_rect()
            logo_x = (SCREEN_WIDTH - logo_rect.width) // 2
            logo_y = 20
            logo_loaded_successfully = True # Dùng cờ (flag) để báo tải thành công
        except pygame.error as e:
            print(f"Lỗi: Không thể tải file logo 'MummyMaze_logo.png'. {e}")
            logo_loaded_successfully = False # Báo tải thất bại

        # Vẽ "User email/account"
        #user_text = main_font.render("dudeschasemoney@gmail.com", True, COLOR_TEXT)
        #screen.blit(user_text, (SCREEN_WIDTH - user_text.get_width() - 20, 20))

        # Vẽ tất cả các nút
        for button in main_menu_buttons + icon_buttons:
            button.draw(screen)
        
        if logo_loaded_successfully:
            screen.blit(logo_icon, (logo_x, logo_y))

        footer_text_surf = main_font.render("Version 1.0.0 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT)
        footer_text_rect = footer_text_surf.get_rect(
            centerx = SCREEN_WIDTH // 2,      # Căn giữa theo chiều ngang
            bottom = SCREEN_HEIGHT - 15       # Cách lề dưới 
        )
        
        screen.blit(footer_text_surf, footer_text_rect)

        # 4. Cập nhật màn hình
        pygame.display.flip()

        # Giới hạn FPS
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
