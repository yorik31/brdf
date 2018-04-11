import os,sys
import log
import tempfile
import global_variables
from osgeo import gdal
import numpy as np

'''
    -- create_gcp_list        : From latitude / longitude grid create a gcp list
                                to be used by gdal to set header of raster in raw image 
                                model.                                 
    -- main                   : Set projection from a reference image to a working image
                                Add projection to any input raw image. 
    -- clean_image_projection : Develop but not use for S3 
 
 '''

def clean_image_projection(input_image,output_image) :

    if os.path.exists(output_image) :
        os.remove(output_image)
#Load DS and extract imagery data :
    raster = gdal.Open(input_image)
    band = raster.GetRasterBand(1)
    im_data = band.ReadAsArray()
#Create Empty :
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(output_image, cols, rows, 1,
                              gdal.GDT_Float32,
                              options=['COMPRESS=LZW'])
    outband = outRaster.GetRasterBand(1)
#Save into the new DS : output_image
    outband.WriteArray(im_data)
    outband.FlushCache()

def create_gcp_list(latitude,longitude,rescaling_coef = 1.0):

    n_gcp = 150  # Maximum allow GCPs
    percentage_gcp_per_line = 0.2

    latitude_ds = gdal.OpenShared(str(latitude))
    longitude_ds = gdal.OpenShared(str(longitude))
    lat = (latitude_ds.GetRasterBand(1)).ReadAsArray().astype(np.float32)
    lon = (longitude_ds.GetRasterBand(1)).ReadAsArray().astype(np.float32)
    gcp_list_o = []

    pas_pixel = np.int(
        latitude_ds.RasterXSize * percentage_gcp_per_line) + 1;
    pas_line = np.int(
        (latitude_ds.RasterYSize * latitude_ds.RasterXSize) / (n_gcp * pas_pixel)) + 1

    print latitude_ds.RasterXSize / pas_pixel, ' ', latitude_ds.RasterYSize / pas_line
    k = 0
    for line in range(0, latitude_ds.RasterYSize - 1, pas_line):
        for px in range(0, latitude_ds.RasterXSize - 1, pas_pixel):
            gcp = gdal.GCP(np.multiply(np.double(lon[line][px]), rescaling_coef),
                           np.multiply(np.double(lat[line][px]) , rescaling_coef),
                           0,
                           (px), (line))
            gcp_list_o.append(gcp)
            k = k + 1

    latitude_ds = None
    longitude_ds = None

    return gcp_list_o #Gdal osgeo gcp object



def main(workimage,refimage,DIROUT) :

    if  not refimage :
        log.warn(' Reference projection image')
        return False

    if  not workimage :
        log.warn(' Reference projection image')
        return False

    (fd, out_name) = tempfile.mkstemp(prefix='with_geometry_',dir = DIROUT,suffix='.tif')
    os.close(fd)

    ref_ds = gdal.Open(str(refimage))
    src_sds_name = ref_ds.GetSubDatasets()

    work_data = gdal.Open(workimage, gdal.GA_Update)
#	    dx_displacement_data = gdal.Open(src_sds_name[1][0], gdal.GA_Update)

# Read the reference image
    format = 'GTiff'
    driver = gdal.GetDriverByName(format)
    src_ds_prj = gdal.Open(refimage)
    projection = src_ds_prj.GetProjection()
    geotransform = src_ds_prj.GetGeoTransform()

    pixelXSize_Geo = geotransform[1]
    pixelYSize_Geo = geotransform[5]
    geotransformOut = geotransform
    scX = (np.true_divide(ref_ds.RasterXSize, work_data.RasterXSize))
    scY = (np.true_divide(ref_ds.RasterYSize, work_data.RasterYSize))
    l = list(geotransformOut)
    l[1] = pixelXSize_Geo * scX
    l[5] = pixelYSize_Geo * scY
    geotransformOut = tuple(l)

    log.info(' ')
    log.info('Origin             = ('+str(geotransform[0])+' , '+str(geotransform[3])+')')
    log.info('Input Pixel Size   = ('+str(geotransform[1])+' , '+str(geotransform[5])+')')
    log.info('Output Pixel Size  = ('+str(geotransformOut[1])+' , '+str(geotransformOut[5])+')\n')

    work_data.SetProjection(projection)
    work_data.SetGeoTransform(geotransformOut)
    dst_ds0 = driver.CreateCopy(out_name, work_data, 0)

    log.info( ' ')
    log.info('  Create    :' + out_name + '\n')
    work_data = None
    ref_ds = None

    workimageName = workimage

    gdal_edit = os.path.join('/home/saunier/swig/python/scripts/', 'gdal_edit.py')
    param = [
	'python2.7',
	gdal_edit,
	'-mo META-TAG_IMAGEDESCRIPTION="Correlation Validity Flag, Ref/work Images:',
	str(out_name),
	    '"',
	    out_name]
    cmd = ' '.join(param)
    #os.system(cmd)

    return out_name

