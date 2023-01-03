import sys
import os


from inspect import getargspec

from contextlib import contextmanager
from .errors import NotRasterError
from .array_tools import surface_area

# Try to import the arcpy api.
# If arcpy is not available, import the rasterio api

try:
    from . import sa_arcpy
    from .sa_arcpy import prep_data, save_outputs, aggregate_areas
    import arcpy

except ModuleNotFoundError:
        try:
            from . import sa_rasterio
            from .sa_rasterio import aggregate_areas, prep_data, save_outputs
            import rasterio
        
        
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Surface Area requires arcpy or rasterio for raster data handling")



def filter_kwargs(function):
    def wrapper(*args, **kwargs):
        keep_kwargs = {k:v for k,v in kwargs.items() if k in getargspec(function).args}
        
        return function(*args, **keep_kwargs)
    return wrapper

@contextmanager
def cwd(dir_):
    '''Change a directory to dir_, do some things, then change it back.'''

    orig_dir = os.getcwd()
    os.chdir(dir_)
    try:
        yield
    finally:
        os.chdir(orig_dir)

assert save_outputs

def load_and_run(function):
    global save_outputs
    save = filter_kwargs(save_outputs)
    def wrapper(raster_path, out_raster, **function_kwargs):
        dict_ = prep_data(raster_path)
        new_rast = function(**dict_)
        save(new_rast, out_raster = out_raster, **dict_)
        return new_rast
    return wrapper


gen_sa_raster = load_and_run(filter_kwargs(surface_area))



def sa_raster_dir(directory):
    '''Make surface-area rasters for all rasters in the given directory.
    '''



    with cwd(directory):
        if not os.path.exists('surface_area'):
            os.makedirs('surface_area')
        files = [f for f in os.listdir() if os.isfile(f)]
        for f in files:
            name, ext = f.split('.')
            out_path = name + 'sa.' + ext
            
            try:
                gen_sa_raster(in_path, out_path)
            except NotRasterError:
                pass
            except Exception as e:
                print(f'Could not make a surface area raster for {f}')
                print(e)


print('Loading')
if __name__ == '__main__':
    args = sys.argv[1:]
    if args[0] == '-d':
        directory = True
        in_path = args[1]
    else:
        directory = False
        in_path = args[0]
        out_path = args[1]
    
    if directory:
        sa_raster_dir(in_path)
    else:
         gen_sa_raster(in_path, out_path)