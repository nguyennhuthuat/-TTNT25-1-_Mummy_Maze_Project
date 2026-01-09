import os
import json
from cryptography.fernet import Fernet


## init
SECRET_KEY = b'OfGnW-sL924t5pSokzW3ojrEwTDNe5XKoYS-t1fr3z8='

try:
    cipher = Fernet(SECRET_KEY)
except ValueError:
    print("LỖI: Key không hợp lệ! Hãy đảm bảo bạn đã copy đúng key từ Bước 1.")
    cipher = None

def save_data(data_dict, filename = "global_status.sav"):
    """
    Mã hóa dictionary và lưu vào file.
    :param filename: Tên file (vd: 'savegame.dat')
    :param data_dict: Dữ liệu dạng Dictionary cần lưu
    """
    if cipher is None: return
    try:
        # 1. Chuyển Dict -> JSON String
        json_str = json.dumps(data_dict, ensure_ascii=False)
        
        # 2. Mã hóa chuỗi JSON (cần encode sang bytes trước)
        encrypted_data = cipher.encrypt(json_str.encode('utf-8'))
        
        # 3. Ghi file (chế độ wb - write binary)
        path = os.path.join("assets", "save", filename)
        with open(path, 'wb') as f:
            f.write(encrypted_data)
            
        
    except Exception as e:
        print(f"Lỗi khi lưu game: {e}")

def load_data(filename = "global_status.sav"):
    """
    Đọc file, giải mã và trả về Dictionary.
    :param filename: Tên file cần đọc
    :return: Dictionary chứa dữ liệu hoặc None nếu lỗi
    """
    if cipher is None: return None

    # Kiểm tra file có tồn tại không
    path = os.path.join("assets", "save", filename)
    if not os.path.exists(path):
        print("Không tìm thấy file save.")
        return {}
    try:
        # 1. Đọc file mã hóa (chế độ rb - read binary)
        with open(path, 'rb') as f:
            encrypted_data = f.read()
            
        # 2. Giải mã (Decrypt)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 3. Chuyển Bytes -> JSON String -> Dictionary
        json_str = decrypted_data.decode('utf-8')
        data_dict = json.loads(json_str)
        return data_dict

    except Exception as e:
        # Trường hợp này xảy ra nếu file bị ai đó sửa bậy hoặc sai Key
        print(f"File save bị lỗi hoặc bị can thiệp: {e}")
        return {}


if __name__ == "__main__":
    data = {
            'user_name': 'Thuatdeptrai',
            'level': 0, 
            'is_playing': False, 
            'play': {'explorer_position': [0, 0], 
                    'explorer_direction': 'UP',
                    'zombie_positions': [[0, 0], [1, 1]], 
                    'zombie_directions': ['DOWN', 'LEFT'],
                    'is_opening_gate': False, 
                    'time_elapsed': 0, 
                    'hint_penalty': 0, 
                    'bonus_score': 0,
                    'history_state': [],
                    }
            }
    data2 = {
        "user_name": "Thuat",
        "Thuat": {},
    }
    save_data(data2, "global_status.sav")