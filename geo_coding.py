import os,sys
from global_variables import *
from libs.esa_s3_data import processing
from osgeo import gdal,osr
import numpy as np
from libs import gdal_edit
from libs import gdal_geocoded

from libs import convert_to_toa
import libs.log as log

product = os.path.join(DATA,'S3A_OL_1_EFR____20180316T084138_20180316T084438_20180317T132229_0179_029_064_2520_LN1_O_NT_002')
pr = processing(product)
#pr.import_to_dimap(WD)
pr.set_dim_file_names(WD)
dict_list = pr.set_band_dic()
pr.import_band(dict_list)

pr.set_gcp_geolocation()
pr.set_geometry('FI')


#Size of raster
#Open latitude , longitude

#Set the geometry to input image
gcp_list = pr.gcp_grid_tp
input_file = 'C:/DATA/S3/WD/test/band_5.tif'
output_file = 'C:/DATA/S3/WD/test/band_5_tr.tif'
#gdal_geocoded.clean_image_projection(input_file,output_file)

#Import latitude tp
latitude_data = None
longitude_data = None
ds = None