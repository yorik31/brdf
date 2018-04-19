import os,sys
import global_variables
from libs.esa_s3_data import processing
from libs import convert_to_toa
import libs.log as log
import glob
from osgeo import gdal
import numpy as np

def read_s3(product):

    gv = global_variables.project_variables(mission, sites)
    pr = processing(product , mission , gv)


    dict_list = pr.set_band_dic()
    pr.import_band(dict_list)

    pr.set_gcp_geolocation()
    # Geocode TP files & set class property (sza) ... :

    pr.set_geometry('TP')
    # Geocode Full Image (FI) files :
    pr.set_geometry('FI')

    # Define geometric reference (where to find geometry information)
    reference = dict_list[0]['Radiance file']
    # Set geometry to VZA, VAA, OZA, OAA and Solar Flux file
    pr.set_geometry(dict_list[0]['Radiance file'])
    # Test : Read the dict list  for the fist record

    log.info(' Convert to TOA Reflectance')
    for rec in pr.band_dict:
        log.info(' Input files : ')
        log.info('     Band Number               : ' + str(rec['Band']))
        log.info('     Radiance Scaling factor  : ' + str(rec['Scaling factor']))
        log.info('     Radiance file             : ' + rec['Radiance file'])
        log.info('     Solar flux file           : ' + rec['Solar flux file'])
        log.info('     Sun Zenith Angle file     : ' + pr.sza)

        scaling_factor = rec['Scaling factor']
        radiance_image = rec['Radiance file']
        solar_flux_image = rec['Solar flux file']
        sun_zenith_image = pr.sza
        new_name = os.path.join(gv.WD_RES, rec['Radiance file'].replace('geo', 'toa'))
        log.info('     Output TOA File     : ' + new_name)

        if not os.path.exists(new_name):
            out_name = convert_to_toa.main(radiance_image,
                                           solar_flux_image,
                                           sun_zenith_image,
                                           scaling_factor,
                                           gv.WD_RES)
            os.rename(out_name, new_name)


    file_list = glob.glob(os.path.join(pr.tiff_import_dir, '*toa.tif'))
    geo_list = [os.path.join(pr.tiff_import_dir, 'saa.tif'),
                os.path.join(pr.tiff_import_dir, 'sza.tif'),
                os.path.join(pr.tiff_import_dir, 'vza.tif'),
                os.path.join(pr.tiff_import_dir, 'vaa.tif')]

    file_list = file_list + geo_list

    for rec in file_list:
        print rec
        crop_file = os.path.join(pr.roi_dir, os.path.basename(rec))
        if not os.path.exists(crop_file):
            cmd = gv.gdalwarp_bin + ' -q -cutline '
            cmd += shp_file + ' -crop_to_cutline -r near -of GTiff '
            cmd += rec + ' ' + crop_file
            os.system(cmd)

    file_list = glob.glob(os.path.join(pr.roi_dir, '*tif'))
    res_list = []
    for rec in file_list:
        raster = gdal.Open(rec)
        band = raster.GetRasterBand(1)
        im_data = band.ReadAsArray()
        ch = ''.join([pr.radical, ' ',
                      os.path.basename(rec), ' : ',
                      str(np.mean(im_data)), '  ',
                      str(np.std(im_data)), '  ',
                      str(np.max(im_data)),'\n'
                      ])
        with open(pr.stat_file, 'a') as f:
            f.write(ch)

        res_list.append(ch)






if __name__ == "__main__":
    print len(sys.argv)
    if len(sys.argv) == 2 :
        data_name = sys.argv[1]
    else:
        data_dir = '/media/lcheyne/DATADRIVE0/DATA/S3/Libya4/INPUT_DATA'
        s3_pdt = 'S3A_OL_1_EFR____20180316T084138_20180316T084438_20180317T132229_0179_029_064_2520_LN1_O_NT_002.SEN3'
        data_name = os.path.join(data_dir,s3_pdt)
        # Initialisation, indicate the mission :

    sites = os.path.basename(
        os.path.dirname(
        os.path.dirname(data_name))
    )
    mission = os.path.basename(
        os.path.dirname(
            os.path.dirname(os.path.dirname(data_name)))
    )
    vector = '/media/lcheyne/DATADRIVE0/DATA/VECTOR/'
    shp_file = os.path.join(vector,sites,sites+'.shp')

    print 'Data name : '+data_name
    print 'Shape File: '+shp_file
    print 'Mission   : '+mission
    print 'Sites     : '+sites

    read_s3(data_name)
#    read_s3(data_name)

