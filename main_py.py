import os,sys
import global_variables
from libs.vito_proba_data import processing
import libs.log as log
import glob
from osgeo import gdal
import numpy as np


#Initialisation, indicate the mission :
mission = 'PROBA-V'
gv = global_variables.project_variables(mission)

product = os.path.join(gv.DATA,'PROBAV_L2A_20180224_000153_2_100M_V101')
pr = processing(product)

# To import S3 Data into DIMAP Products :
#pr.import_to_dimap(gv.WD)
pr.set_dim_file_names(WD)
dict_list = pr.set_band_dic()
pr.import_band(dict_list)

#pr.set_gcp_geolocation()
#Geocode TP files & set class property (sza) ... :
#
#pr.set_geometry('TP')
#Geocode Full Image (FI) files :
#pr.set_geometry('FI')

#Define geometric reference (where to find geometry information)
reference = dict_list[0]['Radiance file']
#Set geometry to VZA, VAA, OZA, OAA and Solar Flux file
pr.set_geometry(dict_list[0]['Radiance file'])
#Test : Read the dict list  for the fist record

log.info(' Convert to TOA Reflectance')
for rec in pr.band_dict :
    log.info(' Input files : ')
    log.info('     Band Number               : '+str(rec['Band']))
    log.info('     Radiance Scaling factor  : '+str(rec['Scaling factor']))
    log.info('     Radiance file             : '+rec['Radiance file'])
    log.info('     Solar flux file           : '+rec['Solar flux file'])
    log.info('     Sun Zenith Angle file     : '+pr.sza)

    scaling_factor = rec['Scaling factor']
    radiance_image = rec['Radiance file']
    solar_flux_image = rec['Solar flux file']
    sun_zenith_image =  pr.sza
    new_name = os.path.join(gWD_RES,rec['Radiance file'].replace('geo','toa'))
    log.info('     Output TOA File     : '+new_name)

#    if not os.path.exists(new_name) :
#        out_name = convert_to_toa.main(radiance_image,
#                        solar_flux_image,
#                        sun_zenith_image,
#                        scaling_factor,
#                        WD_RES)
#        os.rename(out_name,new_name)

shp = 'C:\DATA\LANDSAT\LS08_libya4\she_file_l4_roi\shape_file_cnes.shp'
OUTDIR = os.path.join(WD,'ROI')

file_list = glob.glob(os.path.join(WD_RES,'*toa.tif'))
geo_list = [os.path.join(WD_RES,'saa.tif'),
            os.path.join(WD_RES, 'sza.tif'),
            os.path.join(WD_RES, 'vza.tif'),
            os.path.join(WD_RES, 'vaa.tif')]

file_list = file_list + geo_list

for rec in file_list :
    print rec
    crop_file = os.path.join(OUTDIR,os.path.basename(rec))
    if not os.path.exists(crop_file) :
        cmd = gdalwarp_bin+' -q -cutline '
        cmd+= shp+' -crop_to_cutline -r near -of GTiff '
        cmd+= rec+' '+crop_file
        os.system(cmd)


file_list = glob.glob(os.path.join(OUTDIR,'*tif'))
for rec in file_list :
    raster = gdal.Open(rec)
    band = raster.GetRasterBand(1)
    im_data = band.ReadAsArray()
    print os.path.basename(rec),' : ',np.mean(im_data),'  ',np.std(im_data),'  ',np.max(im_data)

















