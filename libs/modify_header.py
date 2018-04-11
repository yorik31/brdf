import os,sys
import log
import tempfile
import global_variables
from osgeo import gdal
''' workimage is an ENVI image
    for S3 img files : sza.img, 
                       saa.img
     when referring to the related '.hdr' file                                         
     The byte ordering  is "byte order = 0" intead of "byte order = 1" 
     For these files the 'hdr' file should be read a update
    '''

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

    log.info(' ')
    log.info('Origin             = ('+str(geotransform[0])+' , '+str(geotransform[3])+')')
    log.info('Input Pixel Size   = ('+str(geotransform[1])+' , '+str(geotransform[5])+')')
    geotransformOut = geotransform
    log.info('Output Pixel Size  = ('+str(geotransformOut[1])+' , '+str(geotransformOut[5])+')\n')

    work_data.SetProjection(projection)
    work_data.SetGeoTransform(geotransformOut)
    dst_ds0 = driver.CreateCopy(out_name, work_data, 0)
    log.info( ' ')
    log.info('  Create    :' + out_name + '\n')
    mask_data = None
    src_ds = None
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

