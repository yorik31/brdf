import sys,os
import log
import glob
import numpy as np
from libs import gdal_geocoded
from xml.dom import minidom
import tempfile
from osgeo import gdal,osr

class processing:
            def __init__(self,product,gv):
                if os.path.exists(product):
                    self.gv = gv #global variables
                    main_dir = glob.glob(os.path.join(product,'*.SEN3'))
                    if len(main_dir) > 0 :
                        self.product = main_dir[0]
                        print self.product
                else :
                    log.warn(' Input product does not exist')
                    print product
                    return

                self.dim_file = ''
                self.dim_file_exist = False
                self.dim_data = ''
                self.dim_data_exist = True
                self.band_dict = [] #list to dictionnaly to indicate location of each band, coef, parameters ....
                self.band_dict_exist = False
                self.sza = '' #File of sun zenith angle from tie point grid
                self.saa = ''
                self.vza = ''
                self.vaa = ''
                self.latitude_tp = '' #Name of latitude Tie Point data
                self.longitude_tp = ''#Name of longitude Tie Point data
                self.latitude = '' #Name of latitude  data
                self.longitude = ''#Name of longitude  data
                self.elevation = ''  # Name of elevation  data
                self.gcp_grid_tp = [] #GCP grid given with tie points (small size)
                self.gcp_grid_tp_set = False
                self.gcp_grid = []    #GCP grid given with the full images
                self.gcp_grid_set = False

            def import_to_dimap(self,out):
                '''use snap to convert input product into dim product'''
                '''out : output repository, WD'''
                cmd = SNAP_COMMAND
                cmd += ' -f dim '
                cmd += self.product + ' '
                cmd += ' -o ' + out
                os.system(cmd)

            def set_dim_file_names(self,out):
                self.dim_file = glob.glob(os.path.join(out, '*.dim'))[0]
                if len(self.dim_file) > 0 :
                    self.dim_exist = True
                    rad = self.dim_file.replace('.dim','.data')
                    if os.path.exists(rad) :
                        self.dim_data = rad
                        self.dim_data_exist = True
                    else :
                        self.dim_data_exist = False
                else :
                    self.dim_exist = False

                if len(self.dim_data) > 0 :
                    self.dim_exist = True
                else :
                    self.dim_exist = False

                self.tp_grid_data = os.path.join(self.dim_data,'tie_point_grids')
                self.sza = os.path.join(self.tp_grid_data, 'SZA.img')
                self.saa = os.path.join(self.tp_grid_data, 'SAA.img')
                self.vza = os.path.join(self.tp_grid_data, 'OZA.img')
                self.vaa = os.path.join(self.tp_grid_data, 'OAA.img')
                self.oz = os.path.join(self.tp_grid_data, 'total_ozone.img')
                self.tcwv = os.path.join(self.tp_grid_data, 'total_columnar_water_vapour.img')
                self.slp = os.path.join(self.tp_grid_data, 'sea_level_pressure.img')
                self.hum = os.path.join(self.tp_grid_data, 'humidity.img')
                self.atmo_temp_profile = glob.glob(
                    os.path.join(self.tp_grid_data,'atmospheric_temperature_profile_pressure_level_*.img'))


            def set_band_dic(self):
                list_o = []
                #dict {'Band':'','Radiance file:' '','Solar flux file:' '','Lambda file:'  ''}
                print self.dim_file
                xmldoc = minidom.parse(self.dim_file)

                if self.dim_data_exist :
                    input_list = glob.glob(os.path.join(self.dim_data,'*radiance*img'))
                    for k,rec in enumerate(input_list) :
                        dict = {}
                        file_name = os.path.basename(rec)
                        radical = file_name.replace('.hdr','')
                        scaling_factor = (xmldoc.getElementsByTagName('Spectral_Band_Info')[k]).getElementsByTagName('SCALING_FACTOR')[0].firstChild.data
                        bd = (np.int((os.path.basename(rec).split('_')[0]).replace('Oa','')))
                        dict['Band'] = bd
                        dict['Radiance file'] = input_list[k]
                        dict['Scaling factor'] = scaling_factor
                        dict['Solar flux file'] = glob.glob(os.path.join(self.dim_data,'solar_flux_band_'+str(bd)+'.img'))[0]
                        list_o.append(dict)
                    self.band_dict = list_o
                    self.band_dict_exist = True
                    return list_o
                else :
                    log.warn(' Dim data does not exist')

            def import_band(self,list) :
                #Browse the dic and apply convert to put band geotiff into <out>
                gv = self.gv
                list_o = list
                for k,dict in enumerate(list):
                    band = dict['Band']
                    log.info(" processing of bands : " + str(band))
                    input_image = dict['Radiance file']
                    new_file = os.path.join(gv.WD_RES, 'band_' + str(band) + '.tif')
                    #Check if file already import and geocoded
                    geo_file = os.path.join(gv.WD_RES, 'band_' + str(band) + '_geo.tif')
                    if not os.path.exists (geo_file):
                        cmd = gv.gdal_translate_bin + ' '
                        cmd += '-of GTiff '
                        cmd += '-ot Float32 '
                        cmd += input_image + ' '
                        cmd += new_file + ' '
                        os.system(cmd)
                    else :
                        log.warn(' Geo Radiance File already processed')
                        log.info(' File exist :'+new_file)
                    dict['Radiance file'] = new_file
                    log.info('  Radiance file : ' + (list_o[k])['Radiance file'])


            def set_gcp_geolocation(self):
                '''
                set the GCP List for the given object, Tie Points and Full grid
                Use function set_tp_gcp and set_gcp_list
                :return:
                '''
                tp_grid = os.path.join(self.dim_data,'tie_point_grids')
                self.latitude_tp = os.path.join(tp_grid, 'TP_latitude.img')
                self.longitude_tp = os.path.join(tp_grid, 'TP_longitude.img')
                self.set_tp_gcp_list()

                grid = os.path.join(self.dim_data)
                self.latitude = os.path.join(grid, 'latitude.img')
                self.longitude = os.path.join(grid, 'longitude.img')
                self.altitude = os.path.join(grid, 'altitude.img')

                self.set_gcp_list()

            def set_tp_gcp_list(self):
                gv = self.gv
                (fd, latitude_im) = tempfile.mkstemp(prefix='with_geometry_', dir=WD, suffix='.tif')
                os.close(fd)
                (fd, longitude_im) = tempfile.mkstemp(prefix='with_geometry_', dir=WD, suffix='.tif')
                os.close(fd)

                # read image latitude
                cmd = gv.gdal_translate_bin + ' '
                cmd += '-of GTiff '
                cmd += self.latitude_tp + ' '
                cmd += latitude_im + ' '
                os.system(cmd)
                cmd = gv.gdal_translate_bin + ' '
                cmd += '-of GTiff '
                cmd += self.longitude_tp + ' '
                cmd += longitude_im + ' '
                os.system(cmd)
                self.gcp_grid_tp = gdal_geocoded.create_gcp_list(latitude_im,
                                                                longitude_im)
                os.remove(latitude_im)
                os.remove(longitude_im)
                self.gcp_grid_tp_set = True


            def set_gcp_list(self):
                (fd, latitude_im) = tempfile.mkstemp(prefix='with_geometry_', dir=WD, suffix='.tif')
                os.close(fd)
                (fd, longitude_im) = tempfile.mkstemp(prefix='with_geometry_', dir=WD, suffix='.tif')
                os.close(fd)
                (fd, altitude_im) = tempfile.mkstemp(prefix='with_geometry_', dir=WD, suffix='.tif')
                os.close(fd)

                log.info(' Read latitude image grid  : ')
                cmd = gdal_translate_bin + ' '
                cmd += '-of GTiff '
                cmd += self.latitude + ' '
                cmd += latitude_im + ' '
                os.system(cmd)

                log.info(' Read longitude image grid  : ')
                cmd = gdal_translate_bin + ' '
                cmd += '-of GTiff '
                cmd += self.longitude + ' '
                cmd += longitude_im + ' '
                os.system(cmd)

                log.info(' Read altitude image grid  : ')
                cmd = gdal_translate_bin + ' '
                cmd += '-of GTiff '
                cmd += self.altitude + ' '
                cmd += altitude_im + ' '
                os.system(cmd)

                rescaling_coef = 0.000001
                self.gcp_grid = gdal_geocoded.create_gcp_list(latitude_im,
                                                                longitude_im,
                                                              rescaling_coef)
                os.remove(latitude_im)
                os.remove(longitude_im)
                self.altitude = altitude_im
                self.gcp_grid_set = True

            def set_geometry(self,grid_type = 'TP'):
                '''
                 Set the geometry to the input and applied mapping
                 As grid type, discern
                    -- TP (Tie Point images as SZA, SAA ...)
                    -- FI (Full Images)

                 The purpose of the func. is therefore to :
                  - reading
                  - processing
                '''

                #return sza, vza , saa, vaa in Gtif with geometry added
                gv = self.gv
                if grid_type == 'TP' :
                    gcp_list = self.gcp_grid_tp
                    if (self.gcp_grid_tp_set == False) :
                        log.warn('gcp list TP not set')
                        return
                    else :
                        collection_list = [self.sza,
                                           self.saa,
                                           self.vza,
                                           self.vaa,
                                           self.oz,
                                           self.tcwv,
                                           self.slp,
                                           self.hum
                                           ]
                        collection_out = []
                        file_name = ['sza.tif','saa.tif','vza.tif','vaa.tif',
                                     'oz.tif', 'tcwv.tif', 'slp.tif', 'hum.tif']
                        for k,rec in enumerate(collection_list) :
                            print 'In processing : '+rec
                            collection_out.append(self.geocoded_file(
                                                                rec,
                                                                os.path.join(gv.WD_RES,file_name[k]),
                                                                gcp_list))

                        self.sza = collection_out[0]

                if grid_type == 'FI' :
                    gcp_list = self.gcp_grid
                    if (self.gcp_grid_set == False) :
                        log.warn('gcp list not set')
                        return
                    else :
                        if self.band_dict_exist :
                            log.info(' Read solar flux files for each band')
                            for k,rec in enumerate(self.band_dict):
                                log.info(' Processing of : '+rec['Solar flux file'])
                                out_name = os.path.basename(rec['Solar flux file']).replace('img','tif')
                                out = os.path.join(WD_RES,out_name)
                                if not os.path.exists(out):
                                    self.geocoded_file(
                                                    rec['Solar flux file'],
                                                    out,
                                                    gcp_list)
                                else:
                                    log.warn(' Solar Flux file already processed' )
                                self.band_dict[k]['Solar flux file'] = out

                            for k,rec in enumerate(self.band_dict):
                                log.info(' Processing of : '+rec['Radiance file'])
                                out_name = os.path.basename(rec['Radiance file']).replace('.tif','_geo.tif')
                                out = os.path.join(gv.WD_RES,out_name)
                                if not os.path.exists(out):
                                    self.geocoded_file(
                                                    rec['Radiance file'],
                                                    out,
                                                    gcp_list)
                                    os.remove(rec['Radiance file'])
                                else:
                                    log.warn(' Geo Radiance File already processed' )
                                self.band_dict[k]['Radiance file'] = out
                            log.info(' Processing of altitude files : ')
                            out_name = os.path.basename('altitude_geo.tif')
                            out = os.path.join(gv.WD_RES, out_name)
                            if not os.path.exists(out):
                                self.geocoded_file(
                                self.altitude,
                                out,
                                gcp_list)

            def geocoded_file(self,input_image,output_image,gcp_list):
            #    input  : dim file
            #    output : EPSG 4326 File
                gv = self.gv
                if not os.path.exists(output_image):
                    (fd, out_name) = tempfile.mkstemp(prefix='with_geometry_',dir = gv.WD,suffix='.tif')
                    os.close(fd)

            #read image
                    cmd = gv.gdal_translate_bin + ' '
                    cmd += '-of GTiff '
                    cmd += '-co \"COMPRESS=LZW\" '

                    cmd += input_image + ' '
                    cmd += out_name + ' '
                    print cmd
                    os.system(cmd)

                    print "output temp image : "+out_name
                    ds_name = out_name
                    ds = gdal.Open(ds_name, gdal.GA_Update)

                    # Get raster projection
                    epsg = 4326
                    srs = osr.SpatialReference()
                    srs.ImportFromEPSG(epsg)
                    wkt = srs.ExportToWkt()

                    ds.SetGCPs(gcp_list, wkt)
                    #set no data value
                    band = ds.GetRasterBand(1)
                    band.SetNoDataValue(0)
                    ds = None


                    if not os.path.exists(output_image):
                        (fd, out_name2) = tempfile.mkstemp(prefix='with_geometry_', dir=gv.WD, suffix='.tif')
                        os.close(fd)

                    cmd = gv.gdalwarp_bin + ' '
                    cmd += ' -tps '
                    cmd += '-of GTiff '
                    cmd += '-co \"COMPRESS=LZW\" '
                    cmd += out_name+' '
                    cmd += out_name2+' '
                    print cmd
                    os.system(cmd)

                    print "output image : "+output_image
                    os.rename(out_name2, output_image)
                    os.remove(out_name)



                else:
                    log.warn(' File exist '+output_image)
                return output_image
