import math
import time

def simple_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw):
    abs_speed= speed / 111320
    next_lat = lat + abs_speed * math.sin(rotation_yaw)
    next_lon = lon + abs_speed * math.cos(rotation_yaw)
    return next_lat,next_lon

def advanced_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw,time_interval=1):
    # Convert degrees to radians
    lat = math.radians(lat)
    lon = math.radians(lon)
    yaw = math.radians(rotation_yaw)
    pitch = math.radians(pitch_degree)
    roll = math.radians(roll_degree)
    
    # Adjust yaw based on roll
    adjusted_yaw = yaw + roll
    
    # Decompose speed into horizontal and vertical components
    horizontal_speed = speed * math.cos(pitch)
    # vertical_speed = speed * math.sin(pitch) # Only needed if altitude change is relevant
    
    # Calculate the change in coordinates
    delta_lat = horizontal_speed * math.cos(adjusted_yaw) * time_interval / 6371000
    delta_lon = horizontal_speed * math.sin(adjusted_yaw) * time_interval / (6371000 * math.cos(lat))
    
    # Update latitude and longitude
    new_lat = lat + delta_lat
    new_lon = lon + delta_lon
    
    # Convert back to degrees
    new_lat = math.degrees(new_lat)
    new_lon = math.degrees(new_lon)
    
    return new_lat, new_lon
    
def high_resolution_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw,time_interval=1):
     # Earth's radius in meters
    R = 6371000  

    # Convert degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    yaw_rad = math.radians(rotation_yaw)
    pitch_rad = math.radians(pitch_degree)
    roll_rad = math.radians(roll_degree)

    # Gravitational acceleration
    g = 9.81  # m/s²

    # Check if roll angle is near ±90 degrees
    if abs(roll_degree) >= 89.9:
        omega = 0  # or handle as a special case
    else:
        omega = g * math.tan(roll_rad) / speed

    # Change in yaw over the time interval
    delta_yaw = omega * time_interval

    # Update yaw
    new_yaw_rad = yaw_rad + delta_yaw

    # Ground speed components considering pitch
    V_north = speed * math.cos(pitch_rad) * math.cos(new_yaw_rad)
    V_east = speed * math.cos(pitch_rad) * math.sin(new_yaw_rad)

    # Distance traveled
    delta_north = V_north * time_interval
    delta_east = V_east * time_interval

    # Convert distance to changes in latitude and longitude
    delta_lat = delta_north / R
    delta_lon = delta_east / (R * math.cos(lat_rad))

    # Update latitude and longitude
    new_lat = lat_rad + delta_lat
    new_lon = lon_rad + delta_lon

    # Convert back to degrees
    new_lat_deg = math.degrees(new_lat)
    new_lon_deg = math.degrees(new_lon)

    # Normalize longitude to be between -180 and 180 degrees
    new_lon_deg = (new_lon_deg + 180) % 360 - 180

    return new_lat_deg, new_lon_deg, math.degrees(new_yaw_rad)