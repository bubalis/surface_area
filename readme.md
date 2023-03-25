A tool for calculating a by-pixel surface area raster from a digital elevation model.

For use in a python script:
	```
	from surface_area import gen_sa_raster
	gen_sa_raster(dem_path, out_path)
	```

Or from the command line:
	```
	surface_area {dem_path} {out_path}
	```
Or run on all whole directory of dem rasters:
```
surface_area {dem_directory} -d

This tool implements the method described in:

Jenness, J. S. (2004). Calculating landscape surface area from digital elevation models. 
Wildlife Society Bulletin, 32(3), 829-839.