import os,sys
import log
import tempfile
import global_variables
import numpy as np
from libs.rios import applier
from libs.rios import pixelgrid

from osgeo import gdal
''' geocoded_image : Add projection to any input raw image '''

def main(input_image,
         solar_irradiance_image,
         sza_image,
         rescaling_factor,
         DIROUT):


    (fd, out_name) = tempfile.mkstemp(prefix='with_geometry_',dir = DIROUT,suffix='.tif')
    os.close(fd)
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    controls = applier.ApplierControls()

    referencePixgrid = pixelgrid.pixelGridFromFile(input_image)
    controls.setReferencePixgrid(referencePixgrid)
    controls.setResampleMethod('near')
    controls.setOutputDriverName('GTiff')  # See http://www.gdal.org/formats_list.html for detail format
    driver = gdal.GetDriverByName(applier.DEFAULTDRIVERNAME)
    ext = driver.GetMetadataItem('DMD_EXTENSION')
    defaultExtension = '.' + 'tif'
    infiles.image_1 = input_image
    infiles. solar_irradiance= solar_irradiance_image
    infiles.sza = sza_image
    outfiles.image_1 = out_name
    otherargs.coef = rescaling_factor
    applier.apply(basic_func_tc1, infiles, outfiles, otherargs, controls=controls)



    return out_name


def basic_func_tc1(info,inputs,outputs,otherargs):
    in1 = np.asarray(inputs.image_1)
    sol = np.asarray(inputs.solar_irradiance)
    sza = np.asarray(inputs.sza)
    sc = np.float(otherargs.coef)
    cte = np.divide(np.pi,180.0)
    denom = np.multiply(sol,np.cos(sza*cte))
    out = np.divide(np.pi * (sc * in1),
                        ( denom ))
    outputs.image_1 = out


