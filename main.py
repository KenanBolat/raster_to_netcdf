import xarray as xr
import numpy as np
import pandas as pd
import os
import glob
import datetime
import geopandas
from shapely.geometry import mapping
import rioxarray
import matplotlib.pyplot as plt
# initiate script
start = datetime.datetime.now()
# define path
processing_path = r"/home/knn/Desktop/Berkay_RasterVePolygon"

tif_files = [os.path.join(processing_path, row) for row in glob.glob1(processing_path, "*.tif")]
# river_mask_file_name = "Inundation Boundary (PF 1 Value_0).shp"
river_mask_file_name = "extent_reversed.shp"
river_mask = geopandas.read_file(os.path.join(processing_path, river_mask_file_name), crs="epsg:4326")

dims = []
for tif_file in tif_files:
    tag = int(tif_file.split("(PF ")[1].split(")")[0])
    dims.append(tag)
    print(tif_file, str(tag))

chunks = {'x': 3452, 'y': 7147, 'band': 1}
da = xr.concat([xr.open_rasterio(f, chunks=chunks) for f in tif_files], dim=dims)

clipped = da.rio.clip(river_mask.geometry.apply(mapping), river_mask.crs, drop=False)
f = clipped.where(clipped < 0, other=1)
g = f.where(f > 0, other=0)
cumulative_sum = g.sum(dim='concat_dim')
cumulative_sum.rio.to_raster("cumulative_sum.tif")
clipped.to_netcdf("rasters_netcdf.nc")
end = datetime.datetime.now()
print("Start:", start, " Duration: ", str(end - start))
