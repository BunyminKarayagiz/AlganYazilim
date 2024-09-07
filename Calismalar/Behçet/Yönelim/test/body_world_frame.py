import numpy as np

def rotation_matrix_euler(roll, pitch, yaw):
    """
    Roll, Pitch ve Yaw açılarına göre Euler dönüşüm matrisi oluşturur.
    """
    # Roll (Φ) dönüşüm matrisi
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])
    
    # Pitch (θ) dönüşüm matrisi
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    
    # Yaw (ψ) dönüşüm matrisi
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])
    
    # Toplam Euler dönüşüm matrisi (R_z * R_y * R_x)
    R = R_z @ R_y @ R_x
    
    return R

def transform_velocity_euler(velocity_body, roll, pitch, yaw):
    """
    Body frame'deki hız vektörünü world frame'e Euler açılarını kullanarak dönüştürür.
    """
    R = rotation_matrix_euler(roll, pitch, yaw)
    velocity_world = R @ velocity_body
    return velocity_world

def update_position_euler(position_initial, velocity_body, roll, pitch, yaw, time_elapsed):
    """
    Başlangıç pozisyonunu, body frame'deki hızı ve Euler açılarını kullanarak
    belirli bir süre sonra yeni pozisyonu hesaplar.
    """
    velocity_world = transform_velocity_euler(velocity_body, roll, pitch, yaw)
    position_new = position_initial + velocity_world * time_elapsed
    return position_new

# Örnek kullanım
if __name__ == "__main__":
    # Başlangıç pozisyonu (world frame)
    position_initial = np.array([0.0, 0.0, 0.0])  # metre cinsinden
    
    # Hız (body frame)
    speed = 100  # metre/saniye
    direction_body = np.array([1, 0, 0])  # İleri doğru birim vektör
    velocity_body = speed * direction_body
    
    # Açıları derece cinsinden tanımla ve radyana çevir
    roll_deg = 0   # derece
    pitch_deg = 0   # derece
    yaw_deg = 270    # derece
    
    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)
    
    np.set_printoptions(suppress=True)

    # Geçen zaman
    time_elapsed = 10  # saniye
    
    # Yeni pozisyonu hesapla
    position_new = update_position_euler(position_initial, velocity_body, roll, pitch, yaw, time_elapsed)
    
    print("Yeni pozisyon (world frame):", position_new)