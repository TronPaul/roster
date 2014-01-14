def steam_id_to_64(steam_id):
    x, y, z = [int(s) for s in steam_id.split(':')]
    return z * 2 + 76561197960265728 + y    
