# -*- coding: utf-8 -*-
import sys,os

# mission = 'PROBA-V'
# mission = 'S3'


class project_variables :
    def __init__(self,mission):

        system = sys.platform
        if (system == 'win32') :
            self.DATA = os.path.join('C:\DATA',mission)

        if (system == 'linux2'):
            self.DATA = '/home/ideas/script/matcher'

        self.WD = os.path.join(self.DATA,'WD')
        self.WD_RES = os.path.join(self.WD,'RES')

        if not os.path.exists(self.WD_RES):
            os.mkdir(self.WD_RES)

        self.WKT_LIST = os.path.join(self.DATA,'WKT')


        self.SNAP_COMMAND = 'pconvert' #batch execution
        self.GDAL_DIR = 'C:\OSGeo4W64\\bin'
        self.gdal_translate_bin = os.path.join(self.GDAL_DIR, 'gdal_translate')
        self.gdalwarp_bin = os.path.join(self.GDAL_DIR, 'gdalwarp')


        print 'Main working directory :'+self.DATA
        print 'Medicis Parameter      :'+self.WKT_LIST