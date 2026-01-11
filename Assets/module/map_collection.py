"""
Chú thích:
- 'name': Tên của màn chơi. 
- 'map_length':  Kích thước của bản đồ (ví dụ: 5 cho bản đồ 5x5).
- 'map_data':  Mảng 2D mô tả các bức tường.
    + 't': tường trên, 'b': tường dưới, 'l': tường trái, 'r': tường phải
    + 'tl': tường trên-trái, 'tr': tường trên-phải, 'bl': tường dưới-trái, 'br': tường dưới-phải
    + 't*', 'b*', 'l*', 'r*': tường chữ T khuyết
- 'player_start':  Vị trí bắt đầu của người chơi [cột, hàng]. 
- 'stair_position': Vị trí của cầu thang thoát hiểm (cột, hàng).
- 'zombie_starts':  Danh sách các vị trí bắt đầu của zombie [[x, y, type], ...].
    + Type 0: Ưu tiên đi phải/trái (horizontal first, dumb)
    + Type 1: Ưu tiên đi lên/xuống (vertical first, dumb)
    + Type 2: Ưu tiên phải/trái, nếu bị chặn thì lên/xuống (horizontal first, smart)
    + Type 3: Ưu tiên lên/xuống, nếu bị chặn thì phải/trái (vertical first, smart)

=== GIAI ĐOẠN 1: TIỀN SẢNH KIM TỰ THÁP (15 màn) ===
Mục tiêu: Làm quen với cơ chế game
Độ khó: Dễ -> Trung bình nhẹ
Quái vật: Chỉ có Xác ướp (1-2 con)
"""

maps_collection = [
    # ==========================================
    # GIAI ĐOẠN 1: TIỀN SẢNH KIM TỰ THÁP
    # Màn 1-15: Làm quen cơ chế, độ khó dễ
    # Kích thước: 6x6 và 8x8
    # ==========================================
    
    # --- MÀN 1: L-Shape Trap (6x6) ---
    # Tường tạo hình chữ L, zombie bị chặn đi trái
    # Mục tiêu: Học cách né zombie type 1 (vertical first)
    {
        "name":  "Level 1: L-Shape Trap",
        "map_length": 6,
        "map_data": [
            ["", "b", "", "r", "l", ""],
            ["", "t", "r", "", "", ""],
            ["r", "l", "", "", "l", ""],  # Tường chặn zombie ở (5,3) không đi sang trái
            ["", "b", "", "r", "l", ""],
            ["", "t", "", "", "", ""],
            ["", "", "r", "l", "", ""],
        ],
        "player_start":  [3, 3],  # Player ở giữa bản đồ
        "stair_position": (0, 3),  # Cầu thang bên trái
        "zombie_starts": [[5, 3, 1]],  # 1 zombie type 1 (vertical) bị tường chặn
        "scorpion_starts": [],
        "trap_pos": [],
        "gate_pos": [],
        "key_pos": [],
    },
    
    # --- MÀN 2: Simple Cross (6x6) ---
    # Map đơn giản với vài tường ngang
    # Zombie smart type 2, học cách dự đoán đường đi
    {
        "name": "Level 2: Simple Cross",
        "map_length": 6,
        "map_data": [
            ['', 'l', '', '', '', ''],
            ['', '', '', '', '', ''],
            ['', 'l', '', '', '', ''],
            ['t', '', '', '', '', 't'],
            ['', '', '', '', '', ''],
            ['', '', '', '', '', ''],
        ],
        "player_start": [5, 3],
        "stair_position": (6, 0),
        "zombie_starts":  [[2, 4, 2]],  # Zombie type 2 (horizontal smart)
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000,
    },
    
    # --- MÀN 3: First Trap (6x6) ---
    # Giới thiệu bẫy - ô trap ở vị trí [4, 2]
    # Tránh bẫy và né zombie type 0
    {
        "name":  "Level 3: First Trap",
        "map_length":  6,
        "map_data": [
            ['', '', '', '', 'l', ''],
            ['b', 'b', '', '', '', 'l'],
            ['', 'b', '', 'tl', 't', ''],
            ['', 'T', '', '', 'l', 'l'],  # T = Trap symbol
            ['', '', '', 'l', 't', ''],
            ['', '', '', '', 'l', 'l'],
        ],
        "player_start": [4, 6],
        "stair_position": (0, 5),
        "zombie_starts":  [[5, 3, 0]],  # Zombie type 0 (horizontal dumb)
        "scorpion_starts": [],
        "trap_pos": [[4, 2]],  # Bẫy tại vị trí (4, 2)
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000,
    },
    
    # --- MÀN 4: Corner Puzzle (6x6) ---
    # Bản đồ nhiều góc, yêu cầu tính toán đường đi
    {
        "name": "Level 4: Corner Puzzle",
        "map_length": 6,
        "map_data": [
            ['', 'l', '', '', '', ''],
            ['', '', '', '', '', ''],
            ['', 't', 'l', 't', 'l', ''],
            ['', '', 't', 'tl', 'l', ''],
            ['', 't', 'l', '', 'tl', ''],
            ['', 't', 't', 't', '', ''],
        ],
        "player_start": [5, 2],
        "stair_position": (0, 1),
        "zombie_starts":  [[2, 2, 2]],
        "scorpion_starts":  [],
        "trap_pos":  [],
        "key_pos":  [],
        "gate_pos":  [],
        "level_score":  1000,
    },
    
    # --- MÀN 5: Tight Spaces (6x6) ---
    # Nhiều tường góc chật hẹp, luyện kỹ năng di chuyển
    {
        "name": "Level 5: Tight Spaces",
        "map_length": 6,
        "map_data": [
            ['', '', '', '', '', ''],
            ['', 't', 'l', 't', '', ''],
            ['', 't', 't', 't', '', 'l'],
            ['', 'tl', 'l', '', 't', ''],
            ['', '', 't', '', '', 't'],
            ['', 't', 't', 'tl', 't', ''],
        ],
        "player_start": [2, 2],
        "stair_position": (3, 7),
        "zombie_starts":  [[4, 2, 2]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000,
    },
    
    # --- MÀN 6: Open Arena (6x6) ---
    # Không gian rộng, ít tường - phụ thuộc timing và reflexes
    {
        "name": "Level 6: Open Arena",
        "map_length":  6,
        "map_data": [
            ['', '', '', '', '', ''],
            ['', 't', '', '', 'l', ''],
            ['', 't', 'l', '', 'l', 't'],
            ['', '', '', 't', '', 'l'],
            ['', '', '', '', '', ''],
            ['', '', '', '', '', ''],
        ],
        "player_start": [4, 2],
        "stair_position": (7, 6),
        "zombie_starts":  [[3, 6, 2]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000,
    },
    
    # --- MÀN 7: Zigzag Path (6x6) ---
    # Đường đi hình zigzag qua các tường
    {
        "name": "Level 7: Zigzag Path",
        "map_length": 6,
        "map_data":  [
            ['', '', '', '', '', ''],
            ['', 'l', 't', '', 't', ''],
            ['', '', '', '', 'tl', ''],
            ['t', 'l', 't', '', 't', ''],
            ['', 'l', 'l', 't', '', ''],
            ['', '', 't', 'l', '', ''],
        ],
        "player_start": [3, 3],
        "stair_position": (5, 0),
        "zombie_starts":  [[1, 1, 2]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000,
    },
    
    # --- MÀN 8: First Light Hard (6x6) ---
    # Biến thể khó hơn của màn đầu
    {
        "name": "Level 8: First Light Hard",
        "map_length": 6,
        "map_data": [
            ["", "b", "", "", "", ""],
            ["r", "l", "t", "t", "b", ""],
            ["", "", "tr", "l", "", ""],
            ["", "b", "", "", "t", ""],
            ["", "", "r", "l", "b", ""],
            ["", "", "", "", "", ""],
        ],
        "player_start": [1, 3],
        "stair_position": (7, 3),
        "zombie_starts":  [[4, 2, 0]],
        "scorpion_starts": [],
        "trap_pos": [],
        "gate_pos": [],
        "key_pos": [],
    },
    
    # --- MÀN 9: Key & Gate Intro (6x6) ---
    # Giới thiệu cơ chế chìa khóa (K) và cổng (G)
    # Cần lấy key trước khi đến gate, có 1 zombie và 1 scorpion
    {
        "name": "Level 9: Key & Gate Intro",
        "map_length": 6,
        "map_data": [
            ['', '', 'l', 'T', '', 'l'],  # T = Trap
            ['', '', '', '', 'l', ''],
            ['t', 'K', 't', 't', 'l', 'l'],  # K = Key
            ['t', 't', '', 't', 'l', ''],
            ['t', 'r', 'G', 'tl', '', ''],  # G = Gate
            ['', 'tl', '', '', 'l', ''],
        ],
        "player_start": [3, 4],
        "stair_position": (7, 5),
        "zombie_starts":  [[1, 6, 2]],
        "scorpion_starts": [[6, 5, 0]],  # Giới thiệu scorpion
        "trap_pos": [[1, 4]],
        "key_pos": [3, 2],  # Vị trí chìa khóa
        "gate_pos": [5, 3],  # Vị trí cổng
        "level_score": 1000,
    },
    
    # --- MÀN 10: Medium Maze (8x8) ---
    # Map 8x8 đầu tiên, 2 zombie và 1 trap
    # Độ phức tạp tăng lên
    {
        "name": "Level 10: Medium Maze",
        "map_length": 8,
        "map_data": [
            ['', '', 'l', '', '', '', 'l', ''],
            ['t', 'l', '', '', 'l', 'l', 'l', 't'],
            ['', '', 'tl', '', '', '', 'l', ''],
            ['T', '', '', 't', 'tl', '', '', 'l'],  # T = Trap
            ['', 't', 't', '', 'l', 'tl', '', 't'],
            ['t', '', 'l', 'l', 'l', 'tl', '', 't'],
            ['', 't', 'l', '', 'l', 'l', 't', 'l'],
            ['', 'tl', '', '', '', 't', 't', ''],
        ],
        "player_start": [2, 1],
        "stair_position": (7, 9),
        "zombie_starts":  [[6, 5, 2], [7, 8, 2]],  # 2 zombie smart
        "scorpion_starts": [],
        "trap_pos": [[4, 1]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # --- MÀN 11: Key Hunt (8x8) ---
    # Tìm key để mở gate, có zombie smart
    {
        "name":  "Level 11: Key Hunt",
        "map_length": 8,
        "map_data": [
            ['', '', '', 'G', 'l', '', '', 'l'],  # G = Gate
            ['', '', 'l', 'l', 't', '', 'tl', ''],
            ['', '', 't', 't', '', '', 't', 'l'],
            ['', 't', 'l', '', '', 't', 'l', ''],
            ['', 't', 'l', 'l', 'l', 'l', '', 'K'],  # K = Key ở góc xa
            ['', '', 'l', 'l', 'l', 't', 'l', 'l'],
            ['', 't', 't', '', 't', '', '', ''],
            ['t', '', 'l', '', '', '', 't', ''],
        ],
        "player_start": [1, 2],
        "stair_position": (0, 6),
        "zombie_starts":  [[7, 7, 2]],
        "scorpion_starts":  [],
        "trap_pos":  [],
        "key_pos":  [5, 8],
        "gate_pos": [1, 4],
        "level_score":  3000,
    },
    
    # --- MÀN 12: Trap Corridor (8x8) ---
    # Hành lang có bẫy, tập trung né trap
    {
        "name":  "Level 12: Trap Corridor",
        "map_length": 8,
        "map_data": [
            ['', '', 'l', '', '', '', '', 'b'],
            ['', '', '', '', '', '', 'r', 'T'],  # T = Trap
            ['', 't', '', '', '', '', 't', ''],
            ['', '', 't', 'l', '', '', '', ''],
            ['t', '', '', '', 'tl', 'l', '', ''],
            ['', '', 'l', 'l', '', 'l', '', ''],
            ['', '', 'l', '', '', 't', '', ''],
            ['', 't', '', 'l', '', 't', '', ''],
        ],
        "player_start":  [3, 6],
        "stair_position": (9, 5),
        "zombie_starts":  [[5, 6, 2]],
        "scorpion_starts": [],
        "trap_pos": [[2, 8]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # --- MÀN 13: Gate Puzzle (8x8) ---
    # Giải đố với key-gate, zombie và scorpion
    {
        "name": "Level 13: Gate Puzzle",
        "map_length": 8,
        "map_data": [
            ['', '', '', '', '', '', '', ''],
            ['', 'l', '', 't', 't', '', '', ''],
            ['', 'tr', 'K', '', 'l', '', 'l', ''],  # K = Key
            ['', '', '', '', '', 'l', '', 'tl'],
            ['', '', '', '', '', '', 'l', ''],
            ['', '', 'G', '', 'l', '', '', 'l'],  # G = Gate
            ['t', '', '', '', '', '', '', 'l'],
            ['', '', '', '', '', '', 'l', ''],
        ],
        "player_start": [3, 7],
        "stair_position": (9, 8),
        "zombie_starts":  [[8, 4, 2]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [3, 3],
        "gate_pos":  [6, 3],
        "level_score":  3000,
    },
    
    # --- MÀN 14: Scorpion Encounter (8x8) ---
    # Đối đầu với scorpion và zombie, có trap và key-gate
    {
        "name": "Level 14: Scorpion Encounter",
        "map_length": 8,
        "map_data": [
            ['', '', '', '', '', '', '', 'l'],
            ['', '', '', '', '', '', '', ''],
            ['', '', 'r', 'K', '', '', '', ''],  # K = Key
            ['', 'l', '', '', 'l', 't', 't', 't'],
            ['', 'tl', 'G', '', '', '', 'l', ''],  # G = Gate
            ['', '', '', 'l', 't', 'l', '', ''],
            ['', '', '', '', 't', 't', '', 't'],
            ['T', 'l', 't', 'l', '', '', '', ''],  # T = Trap
        ],
        "player_start":  [2, 4],
        "stair_position": (2, 9),
        "zombie_starts":  [[7, 6, 2]],
        "scorpion_starts": [[8, 2, 0]],  # Scorpion type 0
        "trap_pos": [[8, 1]],
        "key_pos": [[3, 4]],
        "gate_pos": [5, 3],
        "level_score": 3000,
    },
    
    # --- MÀN 15: Double Threat (8x8) ---
    # 2 zombie type 3 (vertical smart) cùng lúc, có trap
    {
        "name": "Level 15: Double Threat",
        "map_length": 8,
        "map_data": [
            ['', '', '', '', '', '', '', ''],
            ['', '', 'l', 't', '', 'l', 'l', ''],
            ['t', '', '', 'l', 'l', 'l', '', ''],
            ['', 'tl', '', '', '', '', '', ''],
            ['', '', 'l', 'l', 't', 't', 'b', ''],
            ['', '', 't', '', 't', 'l', 'T', 'l'],  # T = Trap
            ['', 't', '', 'tl', '', 'tl', '', ''],
            ['', 't', '', 'l', 'l', '', 'l', 't'],
        ],
        "player_start": [8, 1],
        "stair_position": (6, 9),
        "zombie_starts": [[1, 5, 3], [7, 5, 3]],  # 2 zombie vertical smart
        "scorpion_starts": [],
        "trap_pos": [[6, 7]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # ==========================================
    # GIAI ĐOẠN 2: SÂU TRONG KIM TỰ THÁP
    # Màn 16-30: Độ khó trung bình cao
    # Kích thước: 8x8, 10x10
    # ==========================================
    
    # --- MÀN 16: Serpent Trail (8x8) ---
    # Đường đi uốn lượn như rắn, zombie + scorpion + trap
    {
        "name": "Level 16: Serpent Trail",
        "map_length": 8,
        "map_data": [
            ['', '', '', 'l', 'l', '', 'l', ''],
            ['', '', 'tl', '', 'tl', '', 'l', ''],
            ['', '', 'l', '', 't', '', 'l', ''],
            ['', '', '', 't', '', 't', '', 't'],
            ['t', '', '', '', 'l', 't', 'l', 't'],
            ['', '', 'l', '', 'l', 'tl', '', 't'],
            ['', 'l', 't', '', 't', 'tl', 'T', ''],  # T = Trap
            ['t', '', '', 'l', 't', '', '', ''],
        ],
        "player_start": [2, 4],
        "stair_position": (0, 1),
        "zombie_starts":  [[3, 1, 0]],
        "scorpion_starts": [[8, 6, 0]],
        "trap_pos": [[7, 7]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # --- MÀN 17: H-Chamber (8x8) ---
    # Phòng hình chữ H, 2 zombie type 1 ở 2 đầu
    {
        "name": "Level 17: H-Chamber",
        "map_length": 8,
        "map_data": [
            ["", "b", "", "r", "l", "", "b", ""],
            ["", "t", "r", "", "", "l", "t", ""],
            ["", "", "r", "b", "b", "l", "", ""],
            ["", "", "", "t", "t", "", "", ""],
            ["", "r", "l", "", "", "r", "l", ""],
            ["", "", "r", "", "", "l", "", ""],
            ["", "b", "", "t", "t", "l", "b", ""],
            ["", "t", "", "", "", "", "t", ""],
        ],
        "player_start": [1, 4],
        "stair_position": (9, 4),
        "zombie_starts":  [[4, 1, 1], [4, 8, 1]],  # 2 zombie vertical dumb
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # --- MÀN 18: Four Corners (8x8) ---
    # 4 góc với 2 zombie, map cân đối
    {
        "name": "Level 18: Four Corners",
        "map_length": 8,
        "map_data": [
            ["", "r", "", "r", "", "r", "", ""],
            ["", "", "", "t", "", "", "b", ""],
            ["", "b", "", "", "b", "r", "l", ""],
            ["", "t", "r", "l", "", "", "t", ""],
            ["", "", "", "b", "", "b", "", ""],
            ["", "r", "l", "", "", "r", "l", ""],
            ["", "", "", "b", "", "", "", ""],
            ["", "r", "l", "t", "t", "r", "l", ""],
        ],
        "player_start": [5, 4],
        "stair_position": (5, 0),
        "zombie_starts":  [[2, 2, 0], [7, 7, 0]],  # 2 zombie horizontal dumb
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 3000,
    },
    
    # --- MÀN 19: Mini Boss (8x8) ---
    # Cuộc chiến nhỏ với 2 zombie, tường chặn chiến thuật
    {
        "name":  "Level 19: Mini Boss",
        "map_length": 8,
        "map_data": [
            ["", "b", "", "r", "l", "", "b", ""],
            ["", "t", "r", "", "", "l", "t", ""],
            ["", "", "", "b", "b", "", "", ""],
            ["", "r", "l", "t", "t", "r", "l", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "b", "r", "", "", "l", "b", ""],
            ["", "t", "", "r", "l", "", "t", ""],  # Tường chặn zombie
            ["", "", "", "", "", "", "", ""],
        ],
        "player_start": [1, 4],
        "stair_position": (9, 4),
        "zombie_starts": [[2, 7, 0], [7, 7, 0]],
        "scorpion_starts":  [],
        "trap_pos":  [],
        "key_pos":  [],
        "gate_pos":  [],
        "level_score":  3000,
    },
    
    # --- MÀN 20: Big Arena (10x10) ---
    # Map 10x10 đầu tiên!  Zombie + scorpion + trap
    {
        "name": "Level 20: Big Arena",
        "map_length": 10,
        "map_data":  [
            ['', 'l', '', '', '', 'l', '', '', '', 'l'],
            ['', '', '', 't', '', 't', '', '', '', ''],
            ['', 'tl', '', '', '', 't', 't', 't', 'l', 't'],
            ['', '', '', '', 't', '', 't', '', 'l', 't'],
            ['', '', '', '', '', '', '', 't', 'l', ''],
            ['', 't', 't', '', '', '', 'T', 'l', 't', ''],  # T = Trap
            ['', '', 'l', 't', 'l', 'l', '', '', '', ''],
            ['', '', '', 'l', 'l', '', 'l', '', 'l', 't'],
            ['', 't', 'l', 'l', '', '', '', '', 'l', 't'],
            ['', 'l', '', '', 't', '', '', '', '', 't'],
        ],
        "player_start": [10, 10],
        "stair_position": (0, 1),
        "zombie_starts":  [[2, 4, 3]],  # Zombie vertical smart
        "scorpion_starts": [[9, 6, 1]],
        "trap_pos": [[6, 7]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 5000,
    },
    
    # --- MÀN 21: Complex Walls (10x10) ---
    # Map nhiều tường phức tạp, có key-gate system
    {
        "name":  "Level 21: Complex Walls",
        "map_length":  10,
        "map_data": [
            ['', '', '', '', '', '', 'l', '', '', 'l'],
            ['', 'l', '', 'tl', 'l', '', '', '', '', ''],
            ['T', 't', '', 'l', 't', 't', 't', '', '', ''],  # T = Trap
            ['', 'l', '', '', '', 'tl', '', 'l', 'l', 't'],
            ['t', 't', 'l', 't', '', 't', 't', '', 'l', ''],
            ['t', '', 't', 't', 'l', 'l', '', '', '', ''],
            ['', 'l', 't', 'l', 't', '', 'G', '', 't', 'l'],  # G = Gate
            ['', 't', '', 'tl', '', 'tl', '', 't', 't', 'l'],
            ['', 't', 'l', 'tr', 'K', 'l', '', 'l', '', 't'],  # K = Key
            ['', 't', 'l', '', 'l', '', '', 't', 't', 't'],
        ],
        "player_start": [6, 7],
        "stair_position": (11, 7),
        "zombie_starts":  [[5, 10, 2]],
        "scorpion_starts":  [],
        "trap_pos": [[3, 1]],
        "key_pos": [[9, 5]],
        "gate_pos": [7, 7],
        "level_score":  5000,
    },
    
    # --- MÀN 22: Large Chamber (10x10) ---
    # Phòng rộng, 2 zombie smart + trap
    {
        "name": "Level 22: Large Chamber",
        "map_length":  10,
        "map_data": [
            ['', 'l', '', '', 'l', '', '', '', '', 'l'],
            ['', 'l', '', 'l', 'tl', 't', '', 'l', '', ''],
            ['', 'tl', 'l', '', 't', '', '', '', 'tl', ''],
            ['', '', '', '', '', '', '', 't', 't', ''],
            ['', 't', 't', 'l', '', 'l', '', '', 't', ''],
            ['', '', '', 'l', 'tl', '', 'l', 't', 'l', ''],
            ['', '', '', 'l', '', 'tl', 'r', 'T', '', 'tl'],  # T = Trap
            ['', 'l', '', '', 't', '', 'l', '', 't', ''],
            ['t', '', 't', 'tl', '', '', '', '', '', ''],
            ['t', '', '', '', '', '', '', '', 'l', 't'],
        ],
        "player_start": [3, 4],
        "stair_position": (0, 1),
        "zombie_starts": [[5, 8, 3], [9, 2, 3]],  # 2 zombie vertical smart
        "scorpion_starts": [],
        "trap_pos": [[7, 8]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 5000,
    },
    
    # --- MÀN 23: Strategic Blocks (10x10) ---
    # Các khối tường chiến lược, key-gate + nhiều kẻ địch
    {
        "name": "Level 23: Strategic Blocks",
        "map_length": 10,
        "map_data": [
            ['', '', '', 'l', '', 'l', '', '', '', ''],
            ['t', '', '', 'l', '', 'tl', 't', 't', 't', ''],
            ['', 'l', 'l', '', 'l', '', 'l', '', 'l', ''],
            ['', 't', '', '', '', '', '', '', 'r', 'K'],  # K = Key
            ['', '', 'l', 'l', '', 't', 't', 'l', 't', 't'],
            ['', 'tl', 't', 't', 't', '', 't', '', '', ''],
            ['', '', '', 'T', 'l', '', '', '', 't', ''],  # T = Trap
            ['', 'l', 't', 'l', 't', '', '', '', '', 't'],
            ['t', '', 't', '', 'G', 't', '', 'tl', 'l', ''],  # G = Gate
            ['', '', 't', 'l', 't', 't', 'l', '', '', 't'],
        ],
        "player_start": [7, 8],
        "stair_position": (10, 0),
        "zombie_starts":  [[1, 10, 2], [9, 3, 2]],  # 2 zombie smart
        "scorpion_starts":  [[9, 10, 0]],
        "trap_pos": [[7, 4]],
        "key_pos": [[4, 10]],
        "gate_pos": [9, 5],
        "level_score":  5000,
    },
    
    # --- MÀN 24: Boss Stage (10x10) ---
    # Màn boss của giai đoạn 2, 2 zombie smart
    {
        "name":  "Level 24: Boss Stage",
        "map_length": 10,
        "map_data": [
            ['', 'l', '', '', 'l', '', '', '', '', 'l'],
            ['', 'l', '', 'l', 'tl', 't', '', 'l', '', ''],
            ['', 'tl', '', '', 't', '', '', '', 'tl', ''],
            ['', '', '', '', '', '', '', 't', 't', ''],
            ['', 't', 't', 'l', '', 'l', '', '', 't', ''],
            ['', '', '', 'l', 'tl', '', 'l', 't', 'l', ''],
            ['', '', '', 'l', '', 'tl', '', 'T', '', 'tl'],  # T = Trap
            ['', 'l', '', '', 't', '', 'l', '', 't', ''],
            ['t', '', 't', 'tl', 'l', 'l', '', '', '', ''],
            ['t', '', '', '', 't', '', '', '', 'l', 't'],
        ],
        "player_start": [3, 4],
        "stair_position": (0, 1),
        "zombie_starts": [[5, 8, 3], [9, 2, 3]],
        "scorpion_starts":  [],
        "trap_pos":  [[7, 8]],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 5000,
    },
    
    # ==========================================
    # GIAI ĐOẠN 3: ĐIỆN THỜ HOÀNG GIA
    # Màn 25-40: Độ khó cao
    # Kích thước:  10x10, 12x12
    # ==========================================
    
    # --- MÀN 25: Royal Arena (10x10) ---
    # Đấu trường hoàng gia với 2 zombie
    {
        "name": "Level 25: Royal Arena",
        "map_length": 10,
        "map_data":  [
            ["", "", "r", "", "", "", "l", "", "", ""],
            ["", "", "b", "", "", "", "", "b", "", ""],
            ["", "", "t", "", "r", "l", "", "t", "", ""],
            ["", "r", "", "", "", "", "", "", "l", ""],
            ["", "", "", "", "b", "b", "", "", "", ""],
            ["", "", "r", "", "t", "t", "", "l", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["", "b", "", "r", "", "", "l", "", "b", ""],
            ["", "t", "", "", "", "", "", "", "t", ""],
            ["", "", "", "r", "", "", "l", "", "", ""],
        ],
        "player_start":  [1, 10],
        "stair_position": (11, 1),
        "zombie_starts":  [[4, 3, 0], [7, 8, 1]],
        "scorpion_starts":  [],
        "trap_pos":  [],
        "key_pos":  [],
        "gate_pos":  [],
        "level_score":  5000,
    },
    
    # --- MÀN 26: Wall Labyrinth (10x10) ---
    # Mê cung tường bất đối xứng với 2 zombie
    {
        "name": "Level 26: Wall Labyrinth",
        "map_length": 10,
        "map_data":  [
            ["", "", "", "", "", "", "", "", "", ""],
            ["", "b", "", "", "", "", "", "b", "", ""],
            ["", "t", "", "", "r", "", "", "t", "", ""],
            ["", "", "", "b", "", "", "", "", "", ""],
            ["", "r", "", "t", "", "", "b", "", "", ""],
            ["", "", "", "", "", "", "t", "", "", ""],
            ["", "", "b", "", "", "", "", "", "l", ""],
            ["", "", "t", "", "", "b", "", "", "", ""],
            ["", "", "", "", "", "t", "", "r", "", ""],
            ["", "", "", "r", "", "", "", "", "", ""],
        ],
        "player_start": [5, 5],
        "stair_position": (6, 0),
        "zombie_starts":  [[1, 8, 0], [8, 1, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 5000,
    },
    
    # --- MÀN 27: Twisted Corridors (10x10) ---
    # Hành lang xoắn ốc
    {
        "name": "Level 27: Twisted Corridors",
        "map_length": 10,
        "map_data": [
            ["", "", "", "b", "", "", "", "", "", ""],
            ["", "r", "", "t", "", "", "", "", "l", ""],
            ["", "", "", "", "", "r", "", "", "", ""],
            ["", "b", "", "", "", "", "", "b", "", ""],
            ["", "t", "", "", "", "b", "", "t", "", ""],
            ["", "", "", "", "", "t", "", "", "", ""],
            ["", "", "r", "", "", "", "", "", "l", ""],
            ["", "b", "", "", "", "", "", "", "", ""],
            ["", "t", "", "", "", "", "", "", "r", ""],
            ["", "", "", "r", "", "", "", "", "", ""],
        ],
        "player_start": [1, 5],
        "stair_position": (11, 5),
        "zombie_starts":  [[4, 8, 0], [8, 3, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 5000,
    },
    
    # --- MÀN 28: Grand Hall (12x12) ---
    # Đại sảnh 12x12 với layout phức tạp
    {
        "name": "Level 28: Grand Hall",
        "map_length": 12,
        "map_data": [
            ["", "", "", "r", "", "", "", "", "b", "", "", ""],
            ["", "b", "", "", "", "", "", "", "t", "", "l", ""],
            ["", "t", "", "", "", "r", "", "", "", "", "", ""],
            ["", "", "", "b", "", "", "", "", "", "", "", ""],
            ["", "r", "", "t", "", "", "", "", "", "", "b", ""],
            ["", "", "", "", "", "", "b", "", "l", "", "t", ""],
            ["", "", "b", "", "", "", "t", "", "", "", "", ""],
            ["", "", "t", "", "", "", "", "r", "", "", "", ""],
            ["", "", "", "", "", "b", "", "", "", "b", "", ""],
            ["", "b", "", "", "", "t", "", "", "", "t", "", ""],
            ["", "t", "", "r", "", "", "", "", "", "", "l", ""],
            ["", "", "", "", "", "", "r", "", "", "", "", ""],
        ],
        "player_start": [6, 6],
        "stair_position": (7, 0),
        "zombie_starts":  [[3, 3, 0], [9, 9, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 29: Dense Maze (12x12) ---
    # Mê cung dày đặc với nhiều zombie và scorpion
    {
        "name": "Level 29: Dense Maze",
        "map_length": 12,
        "map_data": [
            [""  , ""  , "l" , ""  , ""  , ""  , ""  , "l" , ""  , ""  , ""  , ""  ],
            [""  , ""  , "l" , "t" , "l" , "l" , "tl", ""  , "t" , "tl", ""  , "l" ],
            [""  , "t" , ""  , "t" , "l" , "l" , "l" , "t" , "tl", ""  , "tl", ""  ],
            ["t" , "t" , "tl", ""  , "l" , "l" , "t" , "l" , "l" , "t" , "l" , "t" ],
            [""  , ""  , "l" , "tl", ""  , ""  , "l" , ""  , "tl", ""  , "tl", "l" ],
            [""  , "t" , ""  , "l" , "t" , "tl", "t" , "t" , "l" , "t" , "l" , ""  ],
            [""  , "t" , "t" , "t" , "l" , "l" , "t" , "l" , "tl", ""  , "t" , "l" ],
            [""  , "t" , "l" , "tl", ""  , "l" , "l" , "l" , ""  , "tl", ""  , "l" ],
            ["t" , ""  , "l" , ""  , "t" , "t" , "l" , "l" , ""  , "l" , "t" , "t" ],
            [""  , "tl", "t" , "t" , "t" , "l" , ""  , "l" , "l" , "t" , ""  , "l" ],
            [""  , ""  , "tl", "tl", ""  , "tl", ""  , "tl", ""  , "tl", ""  , "l" ],
            [""  , ""  , ""  , ""  , "t" , ""  , "l" , ""  , "tl", ""  , "t" , ""  ]
        ],
        "player_start": [2, 1],
        "stair_position": [5, 13],
        "zombie_starts":  [
            [2, 5, 3],
            [7, 9, 3]
        ],
        "scorpion_starts": [
            [11, 10, 3],
            [10, 6, 3],
            [7, 4, 3]
        ],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000
    },
    
    # --- MÀN 30: Serpent's Lair (12x12) ---
    # Hang rắn với đường uốn khúc, 3 zombie
    {
        "name": "Level 30: Serpent's Lair",
        "map_length": 12,
        "map_data": [
            ["", "", "", "", "r", "", "", "", "", "b", "", ""],
            ["", "b", "", "", "", "", "b", "", "", "t", "", ""],
            ["", "t", "", "r", "", "", "t", "", "", "", "l", ""],
            ["", "", "", "", "", "", "", "", "b", "", "", ""],
            ["", "", "b", "", "", "r", "", "", "t", "", "", ""],
            ["", "", "t", "", "", "", "", "", "", "", "r", ""],
            ["", "r", "", "", "b", "", "", "l", "", "", "", ""],
            ["", "", "", "", "t", "", "", "", "", "b", "", ""],
            ["", "", "", "", "", "", "r", "", "", "t", "", ""],
            ["", "b", "", "", "", "", "", "", "", "", "l", ""],
            ["", "t", "", "r", "", "b", "", "", "", "", "", ""],
            ["", "", "", "", "", "t", "", "r", "", "", "", ""],
        ],
        "player_start": [3, 6],
        "stair_position": (0, 6),
        "zombie_starts":  [[9, 3, 1], [5, 9, 0], [7, 5, 0]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 31: Ancient Labyrinth (12x12) ---
    # Mê cung cổ đại
    {
        "name": "Level 31: Ancient Labyrinth",
        "map_length": 12,
        "map_data": [
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "b", "", "", "", "", "", "", "", "", "", ""],
            ["", "t", "", "", "", "", "", "r", "", "", "", ""],
            ["", "", "", "b", "", "", "", "r", "", "", "", ""],
            ["", "r", "", "t", "", "", "", "", "", "b", "", ""],
            ["", "", "", "", "", "", "", "", "", "t", "", ""],
            ["", "", "b", "", "", "", "", "", "", "", "", ""],
            ["", "", "t", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "b", "", "", ""],
            ["", "b", "", "", "", "", "", "", "t", "", "", ""],
            ["", "t", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
        ],
        "player_start": [6, 6],
        "stair_position": (7, 0),
        "zombie_starts": [[3, 10, 0], [10, 3, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 32: Dragon's Path (12x12) ---
    # Đường của rồng
    {
        "name": "Level 32: Dragon's Path",
        "map_length": 12,
        "map_data": [
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "b", "", "", "", "r", "", "", "", "b", "", ""],
            ["", "t", "", "r", "", "", "", "", "", "t", "", ""],
            ["", "", "", "", "", "", "b", "", "", "", "", ""],
            ["", "", "b", "", "", "", "t", "", "r", "", "", ""],
            ["", "", "t", "", "", "", "", "", "", "", "", ""],
            ["", "r", "", "", "", "", "", "", "", "b", "", ""],
            ["", "", "", "", "b", "", "", "", "", "t", "", ""],
            ["", "", "", "", "t", "", "", "r", "", "", "", ""],
            ["", "", "r", "", "", "", "", "", "", "", "l", ""],
            ["", "b", "", "", "", "", "b", "", "", "", "", ""],
            ["", "t", "", "", "", "", "t", "", "", "", "", ""],
        ],
        "player_start":  [10, 10],
        "stair_position": (0, 1),
        "zombie_starts":  [[3, 3, 0], [8, 6, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 33: Master Maze (12x12) ---
    # Mê cung bậc thầy với nhiều quái và scorpion
    {
        "name": "Level 33: Master Maze",
        "map_length": 12,
        "map_data": [
            [""  , ""  , "l" , ""  , ""  , ""  , ""  , "l" , ""  , ""  , ""  , ""  ],
            [""  , ""  , "l" , "t" , "l" , "l" , "tl", ""  , "t" , "tl", ""  , "l" ],
            [""  , "t" , ""  , "t" , "l" , "l" , "l" , "t" , "tl", ""  , "tl", ""  ],
            ["t" , "t" , "tl", ""  , "l" , "l" , "t" , "l" , "l" , "t" , "l" , "t" ],
            [""  , ""  , "l" , "tl", ""  , ""  , "l" , ""  , "tl", ""  , "tl", "l" ],
            [""  , "t" , ""  , "l" , "t" , "tl", "t" , "t" , "l" , "t" , "l" , ""  ],
            [""  , "t" , "t" , "t" , "l" , "l" , "t" , "l" , "tl", ""  , "t" , "l" ],
            [""  , "t" , "l" , "tl", ""  , "l" , "l" , "l" , ""  , "tl", ""  , "l" ],
            ["t" , ""  , "l" , ""  , "t" , "t" , "l" , "l" , ""  , "l" , "t" , "t" ],
            [""  , "tl", "t" , "t" , "t" , "l" , ""  , "l" , "l" , "t" , ""  , "l" ],
            [""  , ""  , "tl", "tl", ""  , "tl", ""  , "tl", ""  , "tl", ""  , "l" ],
            [""  , ""  , ""  , ""  , "t" , ""  , "l" , ""  , "tl", ""  , "t" , ""  ]
        ],
        "player_start": [2, 1],
        "stair_position": [5, 13],
        "zombie_starts": [
            [2, 5, 3],
            [7, 9, 3]
        ],
        "scorpion_starts": [
            [11, 10, 3],
            [10, 6, 3],
            [7, 4, 3]
        ],
        "trap_pos":  [],
        "key_pos":  [],
        "gate_pos":  [],
        "level_score":  1000
    },
    
    # --- MÀN 34: Crossroads Temple (12x12) ---
    # Ngôi đền ngã tư
    {
        "name":  "Level 34: Crossroads Temple",
        "map_length": 12,
        "map_data": [
            ["", "", "", "", "r", "", "", "", "", "b", "", ""],
            ["", "b", "", "", "", "", "b", "", "", "t", "", ""],
            ["", "t", "", "r", "", "", "t", "", "", "", "l", ""],
            ["", "", "", "r", "", "", "", "", "b", "", "", ""],
            ["", "", "b", "", "", "r", "", "", "t", "", "", ""],
            ["", "", "t", "", "", "", "", "", "", "", "r", ""],
            ["", "r", "", "", "b", "", "", "l", "", "", "", ""],
            ["", "", "", "", "t", "", "", "", "", "b", "", ""],
            ["", "", "", "", "", "", "r", "", "", "t", "", ""],
            ["", "b", "", "", "", "", "", "", "", "", "l", ""],
            ["", "t", "", "r", "", "b", "", "", "", "", "", ""],
            ["", "", "", "", "", "t", "", "r", "", "", "", ""],
        ],
        "player_start": [6, 6],
        "stair_position": (7, 0),
        "zombie_starts": [[3, 4, 0], [9, 8, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 35: Shadow Realm (12x12) ---
    # Vương quốc bóng tối
    {
        "name": "Level 35: Shadow Realm",
        "map_length": 12,
        "map_data": [
            ["", "", "r", "", "", "", "", "", "b", "", "", ""],
            ["", "b", "", "", "", "r", "", "", "t", "", "l", ""],
            ["", "t", "", "b", "", "", "", "", "", "", "", ""],
            ["", "", "", "t", "", "", "b", "", "r", "", "", ""],
            ["", "r", "", "", "", "", "t", "", "", "", "b", ""],
            ["", "", "", "", "r", "", "", "", "l", "", "t", ""],
            ["", "", "b", "", "", "", "", "", "", "", "", ""],
            ["", "", "t", "", "", "b", "", "r", "", "", "", ""],
            ["", "", "", "", "", "t", "", "", "", "b", "", ""],
            ["", "b", "", "r", "", "", "", "", "", "t", "", ""],
            ["", "t", "", "", "", "", "r", "", "", "", "l", ""],
            ["", "", "", "", "r", "", "", "", "", "", "", ""],
        ],
        "player_start": [5, 6],
        "stair_position": (0, 6),
        "zombie_starts":  [[3, 10, 1], [9, 3, 0]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
    # --- MÀN 36: Arena of Trials (12x12) ---
    # Đấu trường thử thách
    {
        "name": "Level 36: Arena of Trials",
        "map_length": 12,
        "map_data":  [
            ["", "", "", "", "", "", "", "", "b", "", "", ""],
            ["", "b", "", "", "", "", "r", "", "t", "", "", ""],
            ["", "t", "", "", "", "", "", "", "", "", "l", ""],
            ["", "", "", "b", "", "", "", "", "", "", "", ""],
            ["", "", "", "t", "", "r", "", "", "", "", "b", ""],
            ["", "r", "", "", "", "", "", "", "", "", "t", ""],
            ["", "", "", "", "b", "", "", "", "", "", "", ""],
            ["", "", "b", "", "t", "", "", "", "", "", "", ""],
            ["", "", "t", "", "", "", "", "", "", "b", "", ""],
            ["", "", "", "", "r", "", "", "", "", "t", "l", ""],
            ["", "b", "", "", "", "", "", "", "", "", "", ""],
            ["", "t", "", "r", "", "", "", "", "r", "", "", ""],
        ],
        "player_start":  [1, 6],
        "stair_position": (13, 6),
        "zombie_starts":  [[4, 4, 0], [9, 9, 1]],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 7000,
    },
    
        # ==========================================
    # GIAI ĐOẠN 4: CUỐI CÙNG - MEGA MAPS
    # Màn 37-40: Maps khổng lồ 16x16
    # ==========================================
    
    # --- MÀN 37: Mega Fortress (16x16) ---
    # Pháo đài khổng lồ 16x16 với 1 zombie và 1 scorpion
    # Độ khó:  Rất cao - Map siêu rộng
    {
        "name": "Level 37: Mega Fortress",
        "map_length": 16,
        "map_data": [
            [""  , ""  , ""  , "l" , ""  , ""  , ""  , ""  , "l" , ""  , ""  , ""  , ""  , ""  , ""  , "l" ],
            ["t" , "t" , ""  , "l" , "tl", "t" , "tl", ""  , "l" , "tl", "l" , "tl", ""  , "t" , "l" , ""  ],
            ["t" , ""  , "l" , "l" , ""  , "l" , "t" , "t" , ""  , "l" , "l" , "l" , "tl", "l" , "tl", "l" ],
            [""  , "l" , "l" , "t" , "t" , "t" , "t" , "l" , "tl", ""  , "l" , "l" , ""  , "l" , "l" , ""  ],
            [""  , "tl", "t" , "t" , ""  , "tl", ""  , "l" , "l" , "l" , "l" , "t" , "l" , "l" , "l" , "t" ],
            [""  , ""  , "t" , "l" , "t" , "l" , "tl", ""  , ""  , ""  , "t" , "l" , ""  , "l" , "tl", "l" ],
            [""  , "tl", ""  , "tl", ""  , "l" , "t" , "t" , "tl", ""  , "tl", ""  , "t" , ""  , "l" , "l" ],
            [""  , ""  , "t" , "l" , "t" , "t" , "tl", ""  , "l" , "tl", "l" , "tl", "t" , ""  , ""  , "l" ],
            [""  , "t" , "l" , "tl", ""  , "tl", ""  , "tl", ""  , ""  , "l" , "l" , "tl", ""  , "l" , ""  ],
            ["t" , ""  , "l" , "l" , "l" , "l" , "t" , "tl", "t" , "t" , ""  , "l" , "l" , "t" , "tl", "t" ],
            [""  , "tl", ""  , "l" , "l" , "t" , "l" , ""  , "tl", "t" , "t" , "l" , "t" , "l" , "t" , "l" ],
            [""  , ""  , "l" , "l" , "t" , "l" , "tl", "t" , ""  , "tl", "l" , "l" , "l" , "t" , "l" , ""  ],
            ["t" , "tl", ""  , "t" , "l" , "l" , "l" , "l" , "tl", ""  , ""  , "t" , "t" , ""  , ""  , "l" ],
            [""  , ""  , "tl", "tl", ""  , "l" , "t" , ""  , "t" , ""  , "tl", ""  , "l" , "t" , "l" , "l" ],
            [""  , "t" , ""  , "l" , "tl", ""  , "tl", "t" , "l" , "t" , ""  , "t" , "t" , ""  , "l" , "l" ],
            [""  , "t" , ""  , "l" , "t" , "t" , ""  , "l" , "t" , ""  , "t" , "t" , "t" , ""  , "t" , ""  ]
        ],
        "player_start": [5, 1],
        "stair_position": [16, 17],
        "zombie_starts":  [
            [12, 15, 0]  # 1 zombie horizontal dumb
        ],
        "scorpion_starts": [
            [8, 15, 0]  # 1 scorpion
        ],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 1000
    },
    
    # --- MÀN 38: Ultimate Maze (16x16) ---
    # Mê cung tối thượng với 3 zombie thông minh
    # Độ khó: Cực cao
    {
        "name": "Level 38: Ultimate Maze",
        "map_length": 16,
        "map_data": [
            ['', '', 'l', 'l', 'tl', '', 'l', 't', 'tl', 't', 'l', 'l', 't', 't', '', 'l'],
            ['t', '', '', 'l', 'l', 't', 'tl', '', 'l', 'tl', '', 'tl', 't', 't', 't', ''],
            ['', 'l', 'tl', '', 't', 't', 'l', 'tl', '', 'l', 't', '', 't', 'l', 't', 't'],
            ['', 'l', 'l', 'tl', 't', 'l', '', 'l', 'tl', '', 'l', 'tl', '', 'l', 't', 'l'],
            ['', 'l', 'l', 't', '', 't', 't', '', '', 'l', 'l', 't', 't', 't', 'l', 'l'],
            ['', '', 'l', 'l', 'tl', 'l', 'l', 'tl', 't', '', 't', 'tl', 't', 'l', 'l', 'l'],
            ['', 't', 'l', '', 'l', 'l', 'l', 'l', 't', 'tl', 'l', '', '', 'l', '', 'l'],
            ['t', 'l', 'tl', 't', '', '', 't', 't', '', 'l', 'l', '', 'l', 't', 'tl', ''],
            ['', 'l', 'tl', 't', 'tl', '', 'tl', 't', 't', '', 'tl', '', 'l', 'l', '', 'l'],
            ['', 'l', '', 'l', '', 'l', 'l', '', 'l', 't', '', 'tl', '', 'tl', '', 'l'],
            ['', 't', 'tl', 't', 't', 'l', '', 'tl', 't', 't', 'tl', '', 'tl', '', 't', ''],
            ['', 'l', 'l', 'l', 't', 'l', 'l', '', 'tl', '', 'l', 't', 'l', 't', 't', 'tl'],
            ['', 't', '', 'tl', 'l', '', 'tl', '', 't', 'tl', 't', 'l', 't', 'tl', 'l', ''],
            ['', 't', 't', 'l', 't', 't', 'l', 'tl', 'l', '', 'l', 'l', '', 'l', 't', 'l'],
            ['t', 't', '', '', '', 'l', '', '', 't', 't', '', 't', '', 'l', 'l', ''],
            ['']*16,
        ],
        "player_start":  [1, 1],
        "stair_position": [11, 17],
        "zombie_starts":  [
            [8, 13, 1],   # Zombie vertical dumb
            [16, 1, 2],   # Zombie horizontal smart
            [12, 11, 2]   # Zombie horizontal smart
        ],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 10000
    },

    # --- MÀN 39: Final Gauntlet (16x16) ---
    # Thử thách cuối cùng với 4 zombie và mê cung phức tạp
    # Độ khó: Nightmare
    {
        "name": "Level 39: Final Gauntlet",
        "map_length": 16,
        "map_data": [
            ['', 'l', 'l', '', 'l', '', '', '', '', '', '', '', '', '', '', ''],
            ['', '', '', 'l', '', '', '', 'tl', '', 'tl', 't', '', 'l', 'l', 'l', 'l'],
            ['', '', 'tl', 't', 'l', 'tl', 't', 'l', 't', 'l', 'tl', '', 'l', 't', '', 'l'],
            ['t', 'l', 'l', 'l', 't', '', 'l', 'l', 'l', 'l', 'l', 't', '', 't', 'tl', ''],
            ['', 'l', 'l', 'tl', 't', 't', '', 'l', 'l', '', 't', 'tl', 't', '', 'l', 'tl'],
            ['', '', 'l', 'tl', 't', 't', 'l', 't', '', 't', 't', '', 'tl', 't', 'l', ''],
            ['', 't', '', '', 't', 'l', 't', 't', 'tl', 't', 'tl', 't', 'l', 't', 't', 'l'],
            ['t', 'l', 'l', 'tl', '', 't', 'tl', '', 'l', 'l', 't', 'l', '', 't', 'l', 'l'],
            ['', 'l', 't', '', 'tl', '', 'l', 't', '', 't', 'l', 't', 'tl', 't', '', 'l'],
            ['', 't', 't', 't', 'l', 't', 't', 't', '', 'l', 't', 'l', 'l', 't', 't', ''],
            ['', 'tl', 'l', 'tl', 't', 't', 't', 'tl', '', 'tl', 't', 'l', '', 't', 't', 't'],
            ['', 'l', 'l', 'l', 't', 'tl', '', 'l', 't', 'l', 'l', 'l', 'tl', 't', 't', ''],
            ['', '', '', 't', '', 'l', 'tl', 't', 'l', '', 'l', 'l', '', 'l', 'tl', ''],
            ['t', 'l', 'tl', 't', 't', 'l', '', '', 'tl', 't', '', 'tl', 't', '', 'l', 'l'],
            ['', 'l', 'l', 'l', 'l', 't', 'l', 'l', '', 'tl', 't', 't', 't', 't', 'l', 'l'],
            ['', '', 't', '', 'tl', '', '', 't', 't', 't', 't', '', 'tl', '', '', 'l'],
        ],
        "player_start":  [1, 16],
        "stair_position": [15, 0],
        "zombie_starts":  [
            [4, 7, 2],    # Zombie horizontal smart
            [15, 7, 0],   # Zombie horizontal dumb
            [10, 8, 2],   # Zombie horizontal smart
            [6, 2, 2]     # Zombie horizontal smart
        ],
        "scorpion_starts": [],
        "trap_pos": [],
        "key_pos": [],
        "gate_pos": [],
        "level_score": 10000,
    }
]