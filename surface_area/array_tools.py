# Method for approximate surface area calculation drawn from:
# Jenness, J. S. (2004). Calculating landscape surface area from digital elevation models. 
# Wildlife Society Bulletin, 32(3), 829-839.
# This method yields a slightly different answer to the example shown in the paper, 
# due to rounding errors in the paper
# 
# The method divides each cell into 8 triangles and calculates the area of these triangles
# by calculating the length of each of the edges in each triangle by using the pythagorean theorem
# on the horizontal distance between cell centers and the elevation of cells.
#  
# For instance if the cell width is 10 meters, then the edge connecting the cell to a neighbor
# that is 3 meters lower in elevation is: sqrt (10**2 + 3**2) or ~ 10.44 meters
# 
# If that neighboring cell is on a diagonal, then the lenght of the edge is:
# sqrt(sqrt(10**2)**2 + 3**2)  

import numpy as np
from math import sqrt


import sys



#Example array from the paper
r = np.array([[190,170,155], [183,165,145], [175,160,122]])

directions = [(0,1),   #over 1 to the right
(1,1), #over 1 to the right and down 1
(1,0), # down 1
(-1, 1)] # 1 up and to the right


# triangles that partially make up a cell.
# the first two numbers represent position relative to the origin (0, 0)
# the third is the direction code


tris =  [[[-1, -1,  1],
        [-1, -1,  0],
        [-1,  0,  2]],

       [[ -1, 0,  2],
        [ -1, 0,  0],
        [ 0,  0,  3]],

       [[-1, -1,  2],
        [0,  -1,  0],
        [-1, -1,  1]],

       [[0,  0,    3],
        [-1, 1,   2],
        [ 0,  0,  0]],

       [[ 0, -1,  0],
        [ 0, -1,  2],
        [ 1, -1,  3]],

       [[ 0, 0,  0],
        [ 0,  1, 2],
        [ 0, 0,  1]],

       [[ 1,  -1,  3],
        [ 0,  0,  2],
        [ 1, -1, 0]],

       
       [[ 0,  0,  2],
        [ 0,  0,  1],
        [ 1,  0,  0]]]





def generate_edge_array(r, cell_y, cell_x):
    '''Generate an array of edge-lengths between cells in the raster. 
    returns: A 3-d array. First two dimensions correspond to the position 
    of the starting point, the 3rd axis is the direction, corresponding to the 
    order in the list (directions). 
    The directions are {0: right, 
                        1: down and to the right,
                        2: down;
                        3: up and to the right}

    e.g. the value located at edge_array[y,x, 1] corresponds to the length of the
    edge that connect scell y, x and cell y+1, x+1 .

    
    '''

    edge_array = np.zeros((r.shape[0], r.shape[1], 4))

    #horizontal lengths associated with the directions:   
    # sqrt(2 * cell_size**2) for diagonal
    lens = [cell_y, 
    sqrt(cell_y**2 + cell_x**2), 
    cell_x, 
    sqrt(cell_y**2 + cell_x**2)] 
    
    #fill in the 4 sub-arrays representing each direction
    for i, (di, len_ ) in enumerate(zip(directions, lens)):
        start_y = max(di[0], 0)
        start_x = max(di[1], 0)
        end_y =  r.shape[0]-start_y
        end_x =  r.shape[1] - start_x
        shift_array = r[start_y:, start_x:]
        sub_array = r[0: end_y, 0: end_x]
        

        edges = np.sqrt((shift_array - sub_array)**2 + len_**2)

        #half the length of each edge is in the pixel,
        #half is not, 
        edges = edges * .5
        edge_array[0: end_y, 0:end_x,i] = edges
    return edge_array



def nan_array(shape):
    arr = np.empty(shape)
    arr[:] = np.nan
    return arr


    

def select_triangle_edge(edge_array, r, index):
    '''Choose an array of edges from the edge_array based on an index'''

    y_start = index[0] * -1
    
    
    x_start = index[1] * -1
    
    
    y2 = index[0]
    x2 = index[1]
    
    data = edge_array[max(y2, 0): min(r.shape[0] + y2, r.shape[0], ), 
                max(x2, 0): min( r.shape[1]+ x2, r.shape[1], ), index[2]]

    tri_array = nan_array(r.shape)
    tri_array[max(y_start, 0): min(r.shape[0] + y_start, r.shape[0], ), 
                max(x_start, 0): min( r.shape[1] + x_start, r.shape[1], )] = data

    

    return tri_array


def calc_tot_area_2(r, edge_array, cell_y, cell_x):
    areas = np.zeros(r.shape, dtype = np.longdouble)
    
    for row, shift in zip(tris[4:], 
    [(1, -1),(1, 1), (1,-1), (1,1)]):
        a = select_triangle_edge(edge_array, r, list(row[0]))
        b = select_triangle_edge(edge_array, r, list(row[1]))
        c = select_triangle_edge(edge_array, r, list(row[2]))
        
        s = (a+b+c)/2
        values =  np.sqrt(s * (s-a) * (s-b) * (s-c) )   
        values[np.isnan(values)] = 0
        areas += values
        areas += shift_array(values, shift[0], shift[1])
        del a, b, c, s, values
        

    # inflate the values for the edges
    # on the edges of the raster, only 4 triangles are calculated, 
    # so double the calculated area. In corners only 2 are calculated, 
    # so they are doubled 2x by being doubled with two edges.
    
    areas[0] = areas[0] *2; areas[-1] = areas[-1] *2 
    areas[:, 0] = areas[:,0] *2; areas[:, -1] = areas[:, -1] *2


    #enforce that no cell can have smaller surface area than planar area
    min_area = cell_y * cell_x
    areas = np.where(areas<min_area, min_area, areas)
    return areas


def shift_array(a, shift_y, shift_x, default_array = 0) :
    out = np.zeros(a.shape)
    start_y_out = max(shift_y, 0)
    start_x_out = max(shift_x, 0)
    start_y_in = max(shift_y * -1, 0)
    start_x_in = max(shift_x * -1, 0)
    
    end_y_out = a.shape[0] - start_y_in
    end_x_out = a.shape[1] - start_x_in
    

    end_y_in = a.shape[0] - max(shift_y,0)
    end_x_in = a.shape[1] - max(shift_x,0)

    out [start_y_out: end_y_out, start_x_out: end_x_out
    ] = a[start_y_in:end_y_in, start_x_in: end_x_in]
    
    return out
         

def calculate_total_area(r, edge_array, cell_y, cell_x):
    '''Use the edge array to calculate the cell-by-cell 
    surface area of the raster r.'''


    #blank raster for the areas
    areas = np.zeros(r.shape, dtype = np.longdouble)

    for i, row in enumerate(tris):
        
            
        #get the 3 edges of the triangle, for each cell in the raster
        a = select_triangle_edge(edge_array, r, list(row[0]))
        b = select_triangle_edge(edge_array, r, list(row[1]))
        c = select_triangle_edge(edge_array, r, list(row[2]))
        
        #calculate the size of that triangle
        s = (a+b+c)/2
        values =  np.sqrt(s * (s-a) * (s-b) * (s-c) )
        
        values[np.isnan(values)] = 0

        # add the area of that triangle to the area raster
        areas+= values
        del a, b, c, s, values
        #triangles_calced += values!=0
        

    # inflate the values for the edges
    # on the edges of the raster, only 4 triangles are calculated, 
    # so double the calculated area. In corners only 2 are calculated, 
    # so they are doubled 2x by being doubled with two edges.
    
    areas[0] = areas[0] *2; areas[-1] = areas[-1] *2 
    areas[:, 0] = areas[:,0] *2; areas[:, -1] = areas[:, -1] *2


    #enforce that no cell can have smaller surface area than planar area
    min_area = cell_y * cell_x
    areas = np.where(areas<min_area, min_area, areas)
    return areas






def surface_area(dem, cell_y, cell_x):
    edge_array = generate_edge_array(dem, cell_y, cell_x)

    areas = calc_tot_area_2(dem, edge_array, cell_y, cell_x)
    return areas
