def convert_ascii_map_no_border(ascii_map_str):
    # 1. Làm sạch và tách dòng
    lines = [line.strip() for line in ascii_map_str.strip().split('\n') if line.strip()]
    if not lines: return []

    # 2. Tính kích thước map
    # (H-1)/2 và (W-1)/2
    source_height = len(lines)
    source_width = len(lines[0])
    rows = (source_height - 1) // 2
    cols = (source_width - 1) // 2
    
    map_data = []

    # 3. Duyệt từng ô
    for r in range(rows):
        row_data = []
        for c in range(cols):
            # Tọa độ tâm ô trong ASCII
            center_y = 2 * r + 1
            center_x = 2 * c + 1
            
            walls = []
            
            # --- LOGIC QUAN TRỌNG: CHỈ CHECK TƯỜNG NẾU KHÔNG PHẢI BIÊN ---
            
            # 1. Check TOP (chỉ kiểm tra nếu r > 0, tức là không phải hàng đầu tiên)
            if r > 0:
                if lines[center_y - 1][center_x] == '%':
                    walls.append('t')
            
            # 2. Check BOTTOM (chỉ kiểm tra nếu chưa phải hàng cuối)
            if r < rows - 1:
                if lines[center_y + 1][center_x] == '%':
                    walls.append('b')
                    
            # 3. Check LEFT (chỉ kiểm tra nếu c > 0, không phải cột đầu)
            if c > 0:
                if lines[center_y][center_x - 1] == '%':
                    walls.append('l')
            
            # 4. Check RIGHT (chỉ kiểm tra nếu chưa phải cột cuối)
            if c < cols - 1:
                if lines[center_y][center_x + 1] == '%':
                    walls.append('r')

            # --- MAPPING SANG CODE CỦA BẠN ---
            tile_id = ""
            
            # Sắp xếp để dễ xử lý logic
            # Thứ tự ưu tiên check: 3 tường -> 2 tường -> 1 tường
            
            w_set = set(walls)
            
            # Trường hợp 3 tường (T-Junctions)
            # Logic: l* nghĩa là T hướng sang trái (có tường trên, dưới, trái)
            if len(w_set) == 3:
                if 't' in w_set and 'b' in w_set and 'l' in w_set: tile_id = "l*"
                elif 't' in w_set and 'b' in w_set and 'r' in w_set: tile_id = "r*"
                elif 'l' in w_set and 'r' in w_set and 't' in w_set: tile_id = "t*"
                elif 'l' in w_set and 'r' in w_set and 'b' in w_set: tile_id = "b*"
            
            # Trường hợp 2 tường (Góc hoặc song song)
            elif len(w_set) == 2:
                # Góc
                if 't' in w_set and 'l' in w_set: tile_id = "tl"
                elif 't' in w_set and 'r' in w_set: tile_id = "tr"
                elif 'b' in w_set and 'l' in w_set: tile_id = "bl"
                elif 'b' in w_set and 'r' in w_set: tile_id = "br"
                # Song song (Hành lang thẳng) - Nếu game bạn có hỗ trợ
                elif 't' in w_set and 'b' in w_set: tile_id = "tb" # Có thể cần map function
                elif 'l' in w_set and 'r' in w_set: tile_id = "lr" # Có thể cần map function
            
            # Trường hợp 1 tường
            elif len(w_set) == 1:
                tile_id = walls[0]
            
            # Trường hợp 0 tường (Ô trống hoặc ngã tư thông thoáng)
            else:
                tile_id = ""

            row_data.append(tile_id)
        
        map_data.append(row_data)

    return map_data

# ===============================================
# INPUT: Dữ liệu map gốc của bạn
# ===============================================
input_ascii = """
%%%%%%%%%%%%%
S           %
%           %
%           %
%  %     %  %
%     %     %
%    % %    %
% % %     % %
%    %     %%
%           %
%%          %
%    T      %
%%%%%%%%%%%%%
"""

# Chạy chuyển đổi
final_map = convert_ascii_map_no_border(input_ascii)

# In kết quả chuẩn format Python List
print("MAP DATA CHO GAME CỦA BẠN:")
print("[")
for row in final_map:
    # Format chuỗi in ra cho giống code mẫu của bạn
    items = [f'"{x}"' if x else '""' for x in row]
    print(f"    [{', '.join(items)}],")
print("]")