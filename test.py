# 1. Khởi tạo dict
my_dic = {"score": 0}

# 3. Hàm b nhận "chìa khóa", mở cửa và sửa đồ đạc
def b(data_dict):
    print("  -> Đang ở trong hàm b...")
    data_dict["score"] = 100  # Thay đổi trực tiếp
    print("  -> Đã sửa score thành 100")

# 2. Hàm a nhận "chìa khóa" từ bên ngoài, rồi đưa cho b
def a(data_dict):
    print("-> Đang ở trong hàm a...")
    b(data_dict) # Gọi b và truyền dict vào

# --- CHẠY CHƯƠNG TRÌNH ---
print(f"Ban đầu: {my_dic}")

a(my_dic) # Truyền biến my_dic vào

print(f"Kết quả cuối cùng: {my_dic}")
# Output: {'score': 100} -> Dữ liệu đã bị thay đổi!