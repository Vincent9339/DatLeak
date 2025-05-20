import numpy as np

def summary(matrix):
    
    f_l = (np.concatenate([arr[arr >= 0.99999] for arr in np.nanmax(matrix,axis=1)]).shape[0] / 
                    (matrix.shape[0] - np.isnan(np.nanmax(matrix,axis=1)).sum())) * 100
    try:
        avg_p_l = np.nanmean(matrix)
    except ValueError:
        avg_p_l= np.inf
    try:
        max_p_l = np.nanmax(matrix)
    except ValueError:
        max_p_l= np.inf
    try:
        min_p_l = np.nanmin(matrix)
    except ValueError:
        min_p_l= np.inf
        
    return f_l, avg_p_l, min_p_l,max_p_l

def cubeT(data, cube_size=16, stride=4):
    x_max, y_max, z_max, t_max = data.shape
    patches = []

    for x in range(0, x_max - cube_size + 1, stride):
        for y in range(0, y_max - cube_size + 1, stride):
            for z in range(0, z_max - cube_size + 1, stride):
                cube = data[
                    x : x + cube_size,
                    y : y + cube_size,
                    z : z + cube_size,
                    :
                ]  
                patches.append(cube)
    return patches
