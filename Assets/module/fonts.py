import pygame
import sys
import os

class MetricFont:
    def __init__(self, image_path, metrics_data, scale_height=None):
        self.chars = {}
        
        # 1. Load ảnh
        try:
            self.sheet = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file ảnh '{image_path}'")
            return

        # 2. Xử lý dữ liệu metrics (Được truyền vào từ file text)
        # Tách chuỗi thành list dựa trên khoảng trắng
        parts = metrics_data.split()
        
        if len(parts) < 2:
            print("Lỗi: File metrics không đúng định dạng hoặc bị rỗng.")
            return

        # Lấy thông số chung
        self.default_space = int(parts[0])
        self.font_height = int(parts[1])
        
        raw_data = parts[2:] 
        
        # 3. Tính tỷ lệ Scale
        self.scale_ratio = 1
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
            if i + 1 >= len(raw_data): break # Tránh lỗi nếu file thiếu số cuối
            
            char_key = raw_data[i]
            try:
                char_width = int(raw_data[i+1])
            except ValueError:
                continue 

            rect = (current_x, 0, char_width, self.font_height)
            
            if current_x + char_width <= self.sheet.get_width():
                original = self.sheet.subsurface(rect)
                
                if self.scale_ratio != 1:
                    new_w = int(char_width * self.scale_ratio)
                    new_h = int(self.font_height * self.scale_ratio)
                    final_img = pygame.transform.scale(original, (new_w, new_h))
                else:
                    final_img = original
                
                self.chars[char_key] = final_img
            
            current_x += char_width

        print(f"MetricFont: Đã load {len(self.chars)} ký tự.")

    def render(self, surface, text, x, y):
        current_x = x
        for char in text:
            if char in self.chars:
                img = self.chars[char]
                surface.blit(img, (current_x, y))
                current_x += img.get_width() + (1 * self.scale_ratio)
            elif char == " ":
                current_x += self.space_width

# --- HÀM ĐỌC FILE ---
def read_metrics_from_file(filename):
    """Đọc toàn bộ nội dung file text và trả về chuỗi string"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read().strip() # .strip() để xóa dòng trắng thừa ở cuối
            return data
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file '{filename}'")
        return ""

# --- MAIN ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    
    # 1. Tên file cấu hình
    font_img_file = os.path.join("assets", "fonts", "font1.png")  # Ảnh font của bạn
    metrics_file = os.path.join("assets", "fonts","data", "font1.txt")        # File chứa số liệu
    
    # 2. Đọc dữ liệu từ file txt
    data_str = read_metrics_from_file(metrics_file)
    
    # 3. Khởi tạo Font (Chỉ chạy khi có dữ liệu)
    my_font = None
    if data_str:
        # Scale chữ lên cao 30px
        my_font = MetricFont(font_img_file, data_str)
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
        if my_font:
            my_font.render(screen, "Load from font1.txt success!", 50, 100)
            my_font.render(screen, "A + B = C", 50, 150)
            my_font.render(screen, "Special: # $ % &", 50, 200)
            my_font.render(screen, "Space      cac  test", 50, 250)
        
        pygame.display.flip()
    pygame.quit()