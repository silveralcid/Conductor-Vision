# conductor-vision/frontend/capture/normalize.py

def normalize_landmarks(landmarks_21):
    wrist_x, wrist_y, wrist_z = landmarks_21[0]

    normalized = []
    for (x, y, z) in landmarks_21:
        nx = x - wrist_x
        ny = y - wrist_y
        nz = z - wrist_z
        normalized.append((nx, ny, nz))

    scale_ref = landmarks_21[9]
    dist = abs(scale_ref[1] - wrist_y) + 1e-6

    scaled = [(nx / dist, ny / dist, nz / dist) for (nx, ny, nz) in normalized]
    return scaled
