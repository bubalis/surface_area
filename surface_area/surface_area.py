
import rasterio
import os

import numpy as np
from argparse import ArgumentParser
from contextlib import contextmanager
from .array_tools import surface_area
from .errors import NotRasterError



def parse_args():
    parser = ArgumentParser(description= "Tool to generate a raster of pixel-by-pixel surface area from a digital elevation model.")
    parser.add_argument('in_path', type = str, required = True, help = "Path to raster or directory of rasters to perform the routine on.")
    parser.add_argument('-o', '--out_path', type = str, help = 'Out path to save the file to.')
    parser.add_argument('-d', '--is_directory', type = str, help = 'Run the routine on all .tif files in the directory; in_path must be a directory.')
    return parser.parse_args()
    
@contextmanager
def cwd(dir_):
    '''Change a directory to dir_, do some things, then change it back.'''

    orig_dir = os.getcwd()
    os.chdir(dir_)
    try:
        yield
    finally:
        os.chdir(orig_dir)


def prep_data(raster_path):
    '''Load in data for the surface area routine.'''
    try:
        with rasterio.open(raster_path) as rast:
            meta = rast.meta.copy()
            dem = rast.read(1)
            dem = np.where(dem == meta['nodata'], np.nan, dem)
    except:
        raise NotRasterError(f'rasterio could not read file {raster_path}')

    cell_x = meta['transform'][0]; cell_y = abs(meta['transform'][-2])
    
    return dem, cell_y, cell_x, meta



def save_ouputs(areas, meta, dem, out_raster):
    '''Save the outputs from the surface_area routine to the out-raster.'''
    meta.update({'dtype': areas.dtype})
    areas[dem == meta['nodata']] = meta['nodata']
    with rasterio.open(out_raster, 'w+', **meta) as dst:
        dst.write(np.array([areas]))





def gen_sa_raster(raster_path, out_raster):
    '''Make a surface-area raster and save it as to the path given as out-raster.'''    
    dem, cell_y, cell_x, meta = prep_data(raster_path)
    areas = surface_area(dem, cell_y, cell_x)
    save_ouputs(areas, meta, dem, out_raster)


    return areas




def sa_raster_dir(directory):
    '''Make surface-area rasters for all rasters in the given directory.
    '''



    with cwd(directory):
        if not os.path.exists('surface_area'):
            os.makedirs('surface_area')
        files = [f for f in os.listdir() if os.isfile(f)]
        for f in files:
            name, ext = f.split('.')
            out_path = os.path.join('surface_area', name + 'sa.' + ext)
            
            try:
                gen_sa_raster(f, out_path)
            except NotRasterError:
                pass
            except Exception as e:
                print(f'Could not make a surface area raster for {f}')
                print(e)



def main():
    args = parse_args()
    if args.is_directory:
        
    
    
        sa_raster_dir(args.in_path)
    else:
         gen_sa_raster(args.in_path, args.out_path)
    