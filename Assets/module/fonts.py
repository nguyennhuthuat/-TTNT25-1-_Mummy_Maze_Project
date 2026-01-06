import pygame
import sys
import os

class MetricFont:
    def __init__(self, font_name="font1", scale_height=None):
        self.chars = {}
        
        # 0. Thiết lập tên font
        if font_name in ["font1", "biggestfont", "headerfont", "pyramidfont", "scorefont"]:
            image_path = os.path.join("assets", "fonts", f"{font_name}.png")
            metrics_file = os.path.join("assets", "fonts", "data", f"{font_name}.txt")
            metrics_data = read_metrics_from_file(metrics_file)
        else:
            print(f"Lỗi:  Tên font '{font_name}' không hợp lệ.")
            return

        # 1. Load ảnh
        try:
            self.sheet = pygame.image.load(image_path).convert_alpha()
            self.sheet.set_colorkey((0, 0, 0))
            print(f"Kích thước ảnh font '{font_name}': {self.sheet.get_size()}")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file ảnh '{image_path}'")
            return

        # 2. Xử lý dữ liệu metrics (Được truyền vào từ file text)
        parts = metrics_data.split()
        
        if len(parts) < 2:
            print("Lỗi: File metrics không đúng định dạng hoặc bị rỗng.")
            return

        # Lấy thông số chung
        self.default_space = int(parts[0])
        self.font_height = int(parts[1])
        
        raw_data = parts[2:] 
        
        # 3. Tính tỷ lệ Scale
        self. scale_ratio = 1
        if scale_height is not None: 
            self.scale_ratio = scale_height / self.font_height
            self.line_height = scale_height
            self.space_width = self.default_space * self.scale_ratio
        else:
            self.line_height = self.font_height
            self.space_width = self.default_space
            
        # 4. Cắt hình
        current_x = 0
        
        # Duyệt từng cặp (Ký tự - Độ rộng)
        for i in range(0, len(raw_data), 2):
            if i + 1 >= len(raw_data): 
                break
            
            char_key = raw_data[i]
            try: 
                char_width = int(raw_data[i+1])
            except ValueError:
                continue 

            rect = (current_x, 0, char_width, self.font_height)
            
            if current_x + char_width <= self.sheet.get_width():
                original = self.sheet.subsurface(rect)
                
                if self. scale_ratio != 1:
                    new_w = int(char_width * self.scale_ratio)
                    new_h = int(self.font_height * self.scale_ratio)
                    final_img = pygame. transform.scale(original, (new_w, new_h))
                else:
                    final_img = original
                
                self.chars[char_key] = final_img
            
            current_x += char_width

        print(f"MetricFont:  Đã load {len(self.chars)} ký tự.")

    def render(self, text, antialias, color, background=None):
        """
        Render text thành Surface - GIỐNG CHÍNH XÁC pygame.font.Font. render()
        
        Args: 
            text: Chuỗi text cần render
            antialias: Không sử dụng (để tương thích với pygame.font)
            color: Màu của text (RGB tuple hoặc Color object)
            background: Màu nền (RGB tuple), None để trong suốt
            
        Returns:
            pygame.Surface chứa text đã render
        """
        # Chuyển color về tuple nếu là Color object
        if isinstance(color, pygame.Color):
            color = (color.r, color.g, color.b, color.a)
        elif len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        
        # Tính tổng chiều rộng của text
        total_width = 0
        for char in text:
            if char in self. chars:
                total_width += self.chars[char].get_width() + int(1 * self.scale_ratio)
            elif char == " ":
                total_width += int(self.space_width)
        
        # Loại bỏ khoảng cách thừa ở cuối
        if total_width > 0:
            total_width -= int(1 * self.scale_ratio)
        
        # Đảm bảo width tối thiểu là 1
        if total_width <= 0:
            total_width = 1
        
        # Tạo surface mới
        if background is not None: 
            # Chuyển background về tuple nếu là Color object
            if isinstance(background, pygame.Color):
                background = (background.r, background.g, background.b)
            surface = pygame.Surface((total_width, int(self.line_height)))
            surface.fill(background)
        else:
            surface = pygame.Surface((total_width, int(self.line_height)), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))  # Trong suốt
        
        # Vẽ từng ký tự lên surface
        current_x = 0
        for char in text:
            if char in self.chars:
                img = self.chars[char].copy()
                
                # Áp dụng màu lên ảnh
                # Tạo một surface với màu mong muốn
                colored_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                colored_img.fill(color)
                
                # Sử dụng alpha của ảnh gốc làm mask
                # Nhân alpha của màu với alpha của ảnh gốc
                for x in range(img.get_width()):
                    for y in range(img.get_height()):
                        pixel_color = img.get_at((x, y))
                        if pixel_color[3] > 0:  # Nếu pixel không trong suốt
                            new_color = (color[0], color[1], color[2], pixel_color[3])
                            colored_img.set_at((x, y), new_color)
                        else:
                            colored_img.set_at((x, y), (0, 0, 0, 0))
                
                surface.blit(colored_img, (current_x, 0))
                current_x += img. get_width() + int(1 * self.scale_ratio)
            elif char == " ": 
                current_x += int(self.space_width)
        
        return surface

    def get_rect(self, text="", **kwargs):
        """
        TẠO rect từ text - Để sử dụng như:  txt_surf.get_rect(center=...)
        
        QUAN TRỌNG: Hàm này chỉ để tạo rect với kích thước đúng. 
        Trong thực tế, bạn nên gọi từ Surface đã render: 
        
        txt_surf = font. render(text, True, color)
        txt_rect = txt_surf.get_rect(center=rect.center)  # Gọi từ Surface
        
        Args:
            text: Text để tính kích thước
            **kwargs: Các tham số vị trí như center, topleft, midtop, etc. 
            
        Returns:
            pygame.Rect object
        """
        # Tính tổng chiều rộng của text
        total_width = 0
        for char in text:
            if char in self.chars:
                total_width += self.chars[char].get_width() + int(1 * self.scale_ratio)
            elif char == " ":
                total_width += int(self.space_width)
        
        # Loại bỏ khoảng cách thừa ở cuối
        if total_width > 0:
            total_width -= int(1 * self.scale_ratio)
        
        # Đảm bảo width tối thiểu là 1
        if total_width <= 0:
            total_width = 1
        
        # Tạo rect với kích thước tính được
        rect = pygame.Rect(0, 0, total_width, int(self.line_height))
        
        # Áp dụng các tham số vị trí
        for key, value in kwargs.items():
            setattr(rect, key, value)
        
        return rect
    
    def size(self, text):
        """
        Lấy kích thước của text - GIỐNG pygame.font.Font. size()
        
        Args: 
            text: Text cần đo
            
        Returns:
            Tuple (width, height)
        """
        total_width = 0
        for char in text:
            if char in self.chars:
                total_width += self.chars[char].get_width() + int(1 * self.scale_ratio)
            elif char == " ": 
                total_width += int(self.space_width)
        
        # Loại bỏ khoảng cách thừa ở cuối
        if total_width > 0:
            total_width -= int(1 * self.scale_ratio)
        
        if total_width <= 0:
            total_width = 1
        
        return (total_width, int(self.line_height))
    
    def get_height(self):
        """Lấy chiều cao của font"""
        return int(self.line_height)
    
    def get_linesize(self):
        """Lấy khoảng cách giữa các dòng"""
        return int(self.line_height)


# --- HÀM ĐỌC FILE ---
def read_metrics_from_file(filename):
    """Đọc toàn bộ nội dung file text và trả về chuỗi string"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read().strip()
            return data
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file '{filename}'")
        return ""


# --- DEMO:  SO SÁNH MetricFont vs pygame.font. Font ---
if __name__ == "__main__": 
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("MetricFont vs pygame.font - Giống hệt nhau!")
    
    # Tạo 2 loại font
    pygame_font = pygame.font.Font(None, 36)  # Font mặc định pygame
    metric_font = MetricFont(font_name="biggestfont", scale_height=36)  # Font custom

    # Màu sắc
    TEXT_COLOR = (255, 255, 255)
    BG_COLOR = (50, 50, 100)
    BUTTON_COLOR = (100, 100, 200)
    
    # Tạo button rect
    button_rect = pygame. Rect(200, 150, 400, 80)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # ===== CÁCH DÙNG GIỐNG HỆT NHAU =====
        
        # 1. VẼ VỚI pygame.font.Font
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
        
        text = "PYGAME FONT"
        txt_surf = pygame_font.render(text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=button_rect.center)
        screen.blit(txt_surf, txt_rect)
        
        # 2. VẼ VỚI MetricFont - CODE GIỐNG HỆT
        button_rect2 = pygame.Rect(200, 300, 400, 80)
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect2)
        pygame.draw.rect(screen, (255, 255, 255), button_rect2, 2)
        
        text = "METRIC FONT"
        txt_surf = metric_font.render(text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=button_rect2.center)
        screen.blit(txt_surf, txt_rect)
        
        # 3. DEMO THÊM - Với background color
        button_rect3 = pygame.Rect(200, 450, 400, 80)
        pygame.draw.rect(screen, (200, 100, 100), button_rect3)
        pygame.draw.rect(screen, (255, 255, 255), button_rect3, 2)
        
        text = "WITH BACKGROUND"
        txt_surf = metric_font.render(text, True, (255, 255, 0), (200, 100, 100))
        txt_rect = txt_surf.get_rect(center=button_rect3.center)
        screen.blit(txt_surf, txt_rect)
        
        # Hiển thị hướng dẫn
        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render("Code giống hệt nhau cho cả 2 font!", True, (255, 255, 0))
        screen.blit(info_text, (200, 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()