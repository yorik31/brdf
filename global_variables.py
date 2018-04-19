# -*- coding: utf-8 -*-
import sys,os

# mission = 'PROBA-V'
# mission = 'S3'


class project_variables :
    def __init__(self,mission,sites):

        system = sys.platform
        if (system == 'win32') :
            self.DATA = os.path.join('C:\DATA',mission)
            self.WD = os.path.join(self.DATA, 'WD')
            self.WD_RES = os.path.join(self.WD, 'RES')
            if not os.path.exists(self.WD_RES):
                os.mkdir(self.WD_RES)
            self.SNAP_COMMAND = 'pconvert'  # batch execution
            self.GDAL_DIR = 'C:\OSGeo4W64\\bin'
            self.gdal_translate_bin = os.path.join(self.GDAL_DIR, 'gdal_translate')
            self.gdalwarp_bin = os.path.join(self.GDAL_DIR, 'gdalwarp')
#            self.WKT_LIST = os.path.join(self.DATA,'WKT')


        if (system == 'linux2'):
            self.ROOTDIR = os.path.join('/media/lcheyne/DATADRIVE0/DATA', mission, sites)
            self.DATA = os.path.join(self.ROOTDIR ,'INPUT_DATA')
            self.DIMAP = os.path.join(self.ROOTDIR ,'DIMAP')      #Import au format dimap des produits S3
            self.WD = os.path.join(self.ROOTDIR ,'WD')            #Import du format dimap (image full resolution)
            self.WD_RES = os.path.join(self.ROOTDIR,'RES')
            self.ROI = os.path.join(self.ROOTDIR,'ROI')           #Resultat du clipping
            self.STAT = os.path.join(self.ROOTDIR,'STAT')          #Resultat des statistics sur ROI (txt file)
            self.SNAP_COMMAND = '/home/lcheyne/Plugin/snap/bin/pconvert'  # batch execution
            self.GDAL_DIR = '/usr/bin'
            self.gdal_translate_bin = os.path.join(self.GDAL_DIR, 'gdal_translate')
            self.gdalwarp_bin = os.path.join(self.GDAL_DIR, 'gdalwarp')
 #           self.WKT_LIST = os.path.join(self.DATA,'WKT')

        if not os.path.exists(self.WD):
            os.mkdir(self.WD)
        if not os.path.exists(self.WD_RES):
            os.mkdir(self.WD_RES)
        if not os.path.exists(self.DIMAP):
            os.mkdir(self.DIMAP)
        if not os.path.exists(self.ROI):
            os.mkdir(self.ROI)
        if not os.path.exists(self.STAT):
            os.mkdir(self.STAT)

        print 'Main working directory :'+self.DATA
       # print 'Medicis Parameter      :'+self.WKT_LIST