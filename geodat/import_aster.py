#http://geoinformaticstutorial.blogspot.de/2012/09/reading-raster-data-with-python-and-gdal.html
#http://forum.freecadweb.org/viewtopic.php?f=8&t=17647&start=10#p139201

import FreeCAD
import geodat.transversmercator
from  geodat.transversmercator import TransverseMercator
import numpy as np


# apt-get install python-gdal
import gdal
from gdalconst import * 


def getAST(b=50.26,l=11.39):

	bs=np.floor(b)
	ls=np.floor(l)

	# the ast dataset
	ff="N%02dE%03d" % (int(bs),int(ls))
	fn=FreeCAD.ConfigGet("UserAppData") +'/geodat/AST/ASTGTM2_' + ff +'_dem.tif'
	print fn

	dataset = gdal.Open(fn, GA_ReadOnly) 
	dataset
	if dataset == None:
		FreeCAD.Console.PrintError("\nProblem cannot open " + fn + "\n")
		return

	cols=dataset.RasterXSize
	rows=dataset.RasterYSize

	geotransform = dataset.GetGeoTransform()
	originX = geotransform[0]
	originY = geotransform[3]
	pixelWidth = geotransform[1]
	pixelHeight = geotransform[5]

	originX
	originY
	pixelWidth
	pixelHeight

	band = dataset.GetRasterBand(1)
	data = band.ReadAsArray(0, 0, cols, rows)

	data.shape
	# erfurt 51,11
	data[0,0]
	# zeitz  51,12
	data[3600,0]
	# windischletten(zapfendorf) 50,11
	data[0,3600]
	# troestau fichtelgebirge 50,12
	data[3600,3600]

	px=int(round((bs+1-b)*3600))
	py=int(round((l-ls)*3600))


	print (px,py)
	print  data[px,py]

	pts=[]
	d=140

	tm=TransverseMercator()
	tm.lat=b
	tm.lon=l
	center=tm.fromGeographic(tm.lat,tm.lon)

	z0= data[px,py]

	for x in range(px-d,px+d):
		for y in range(py-d,py+d):
			ll=tm.fromGeographic(bs+1-1.0/3600*x,ls+1.0/3600*y)
			pt=FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1], 1000.0* (data[x,y]-z0))
			pts.append(pt)

	import Points
	p=Points.Points(pts)
	Points.show(p)

# friesener berg - zeyerner wand
#
#	b=50.26
#	l=11.39
#
# 50 15 36.0 N+11 23 24.0 E /50.2570152,11.3818337

if __name__ == '__main__':
	getAST(50.26,11.39)

