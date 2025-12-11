import pygame
import json
import os

# --- Setup ---
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.RESIZABLE)
pygame.display.set_caption("Mummy Maze - Đăng nhập")

# --- Colors (Mystic Theme) ---
COLOR_WHITE = (235, 235, 235)
COLOR_GOLD = (255, 215, 0)
COLOR_SEMI_TRANSPARENT_WHITE = (255, 255, 255, 150) # For input box border
COLOR_SEMI_TRANSPARENT_GOLD = (255, 215, 0, 180) # For active input box border

# --- Fonts (Mystic Theme) ---
try:
    FONT_PATH = os.path.join('Assets', 'Fonts', 'VT323-Regular.ttf')
    TITLE_FONT = pygame.font.Font(FONT_PATH, 70)
    INPUT_FONT = pygame.font.Font(FONT_PATH, 28)
    BUTTON_FONT = pygame.font.Font(FONT_PATH, 40)
except FileNotFoundError:
    print("Không tìm thấy phông chữ 'VT323-Regular.ttf'. Sử dụng phông chữ mặc định.")
    FONT_PATH = None
    TITLE_FONT = pygame.font.Font(FONT_PATH, 80)
    INPUT_FONT = pygame.font.Font(FONT_PATH, 32)   
    BUTTON_FONT = pygame.font.Font(FONT_PATH, 45)

# --- Assets ---
try:
    BACKGROUND_IMAGE = pygame.image.load(os.path.join('Assets', 'Images', 'background.jpg')).convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    print("Không tìm thấy 'background_mystic.jpg', sử dụng nền đen.")
    BACKGROUND_IMAGE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    BACKGROUND_IMAGE.fill((10, 10, 20))

# --- Data File ---
USER_DATA_FILE = 'users.json'

# --- UI Element Classes (Updated with Blinking Cursor) ---
class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.placeholder = text
        self.text = ''
        self.active = False
        self.is_password = is_password
        self.txt_surface = INPUT_FONT.render('', True, COLOR_WHITE)
        # Thuộc tính cho con trỏ nhấp nháy
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def update(self):
        # Cứ mỗi 500ms thì đảo ngược trạng thái hiển thị của con trỏ
        if pygame.time.get_ticks() - self.cursor_timer > 500:
            self.cursor_timer = pygame.time.get_ticks()
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        
        border_color = COLOR_SEMI_TRANSPARENT_GOLD if self.active else COLOR_SEMI_TRANSPARENT_WHITE
        pygame.draw.line(s, border_color, (0, self.rect.h - 5), (self.rect.w, self.rect.h - 5), 2)

        if self.text:
            display_text = '*' * len(self.text) if self.is_password else self.text
            self.txt_surface = INPUT_FONT.render(display_text, True, COLOR_WHITE)
        else:
            self.txt_surface = INPUT_FONT.render(self.placeholder, True, COLOR_SEMI_TRANSPARENT_WHITE)
        
        s.blit(self.txt_surface, (5, 5))
        
        if self.active and self.cursor_visible:
            cursor_pos_x = self.txt_surface.get_width() + 5 if self.text else 5
            cursor_height = self.txt_surface.get_height()
            pygame.draw.line(s, COLOR_WHITE, (cursor_pos_x, 5), (cursor_pos_x, 5 + cursor_height), 2)

        screen.blit(s, (self.rect.x, self.rect.y))

class Button:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.is_hovered = False

    def draw(self, screen):
        border_color = COLOR_GOLD if self.is_hovered else COLOR_WHITE
        text_color = COLOR_GOLD if self.is_hovered else COLOR_WHITE
        pygame.draw.rect(screen, border_color, self.rect, 2, 10)
        
        txt_surface = BUTTON_FONT.render(self.text, True, text_color)
        screen.blit(txt_surface, (self.rect.x + (self.rect.w - txt_surface.get_width()) / 2,
                                 self.rect.y + (self.rect.h - txt_surface.get_height()) / 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos): return True
        return False

# --- Backend Functions ---
def load_users():
    if not os.path.exists(USER_DATA_FILE): return {}
    try:
        with open(USER_DATA_FILE, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return {}

def check_login(username, password):
    users = load_users()
    return username in users and users[username]['password'] == password

# --- Main Loop ---
def main():
    clock = pygame.time.Clock()
    
    title_text = TITLE_FONT.render("MUMMY MAZE", True, COLOR_WHITE)
    
    username_box = InputBox(SCREEN_WIDTH/2 - 225, SCREEN_HEIGHT/2 - 50, 450, 40, 'Tên đăng nhập')
    password_box = InputBox(SCREEN_WIDTH/2 - 225, SCREEN_HEIGHT/2 + 20, 450, 40, 'Mật khẩu', is_password=True)
    login_button = Button(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 + 100, 300, 60, "Đăng nhập")
    
    input_boxes = [username_box, password_box]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for box in input_boxes: box.handle_event(event)
            if login_button.handle_event(event):
                if check_login(username_box.text, password_box.text):
                    print(f"Đăng nhập thành công: {username_box.text}")
                else:
                    print("Tên đăng nhập hoặc mật khẩu không đúng!")

        for box in input_boxes:
            box.update()

        SCREEN.blit(BACKGROUND_IMAGE, (0, 0))
        SCREEN.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 150))
        for box in input_boxes: box.draw(SCREEN)
        login_button.draw(SCREEN)

        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()