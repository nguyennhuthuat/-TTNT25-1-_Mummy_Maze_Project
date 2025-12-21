self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
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