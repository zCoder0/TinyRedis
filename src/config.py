import os 

class Settings:

    root_data_folder = 'db'
    redis_data_path = os.path.join(root_data_folder,"redis_data.json")
    expiry_data_path = os.path.join(root_data_folder,"expiry_data.json")
    os.makedirs(root_data_folder, exist_ok=True)

    if not os.path.exists(redis_data_path):
        with open(redis_data_path, 'w'):
            pass 

    if not os.path.exists(expiry_data_path):
        with open(expiry_data_path, 'w'):
            pass 