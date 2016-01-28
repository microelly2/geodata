# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui


''' 
    TransverseMercator:
    "author": "Vladimir Elistratov <vladimir.elistratov@gmail.com> and gtoonstra",
    "wiki_url": "https://github.com/vvoovv/blender-geo/wiki/Import-OpenStreetMap-(.osm)",
    "tracker_url": "https://github.com/vvoovv/blender-geo/issues",
'''

import os
import math

# see conversion formulas at
# http://en.wikipedia.org/wiki/Transverse_Mercator_projection
# and
# http://mathworld.wolfram.com/MercatorProjection.html
class TransverseMercator:
    radius = 6378137
    radius = 6378137000
    
    def __init__(self, **kwargs):
        # setting default values
        self.lat = 0 # in degrees
        self.lon = 0 # in degrees
        self.k = 1 # scale factor
        
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
        self.latInRadians = math.radians(self.lat)

    def fromGeographic(self, lat, lon):
        lat = math.radians(lat)
        lon = math.radians(lon-self.lon)
        B = math.sin(lon) * math.cos(lat)
        x = 0.5 * self.k * self.radius * math.log((1+B)/(1-B))
        y = self.k * self.radius * ( math.atan(math.tan(lat)/math.cos(lon)) - self.latInRadians )
        return (x,y)

    def toGeographic(self, x, y):
        x = x/(self.k * self.radius)
        y = y/(self.k * self.radius)
        D = y + self.latInRadians
        lon = math.atan(math.sinh(x)/math.cos(D))
        lat = math.asin(math.sin(D)/math.cosh(x))

        lon = self.lon + math.degrees(lon)
        lat = math.degrees(lat)
        return (lat, lon)



        
tm=TransverseMercator()

import urllib2

source="https://maps.googleapis.com/maps/api/elevation/json?locations="
#Latitude: 50.35° N
#Longitude: 11.17° E
#Elevation: 365 m
source += "50.35,11.17|"
# zugspitze 2962
source += "47.4207504,10.9854391|" 
#Aiguille de Rochefort (4001 m
source += "45.86380,06.96090|" 
# Mont Blanc (4807 m 
source += "45.83270,06.86430|"
source += "52.5073,13.1881|52.7,11.9|52.3,11.8|52.4,11.6"



def getheight(b,l):

	source="https://maps.googleapis.com/maps/api/elevation/json?locations="+str(b)+','+str(l)
	response = urllib2.urlopen(source)
	ans=response.read()
	print ans
	import json
	s=json.loads(ans)
	res=s['results']
	for r in res:
		return round(r['elevation']*1000,2)


def run(b0=50.35,l0=11.17,b=50.35,l=11.17,size=40):

	source="https://maps.googleapis.com/maps/api/elevation/json?locations="
	#b0=50.35
	#l0=11.17
	for i in range(-size,size):
		bb=b+i*0.001
		ll=l+i*0.001
		ll=l
		ss=str(bb)+','+str(ll)+'|'
		source += ss

	i=10
	bb=b+i*0.001

	ll=l+i*0.001
	ll=l
	ss=str(bb)+','+str(ll)
	source += ss

	tm.lat=b0
	tm.lon=l0


	response = urllib2.urlopen(source)
	ans=response.read()
	print ans

	import json
	s=json.loads(ans)
	res=s['results']

	#tm.lat=52.5073
	#tm.lon=13.1881

	baseheight=getheight(tm.lat,tm.lon)


	center=tm.fromGeographic(tm.lat,tm.lon)
	import Draft

	print "Base height ", baseheight
	points=[]
	for r in res:
#		print 
#		print r
#		print tm.lat
#		print tm.lon


		c=tm.fromGeographic(r['location']['lat'],r['location']['lng'])
		print center
		v=FreeCAD.Vector(round((c[0]-center[0]),2),round((c[1]-center[1]),2), round(r['elevation']*1000,2)-baseheight)
		points.append(v)
		print v
	
	
	Draft.makeWire(points,closed=False,face=False,support=None)
	return App.ActiveDocument.ActiveObject
	print points[0]
	print points[-1]
	

def import_heights(b,l,size):
	# altstadt sonneberg/we
	##b=50.3689;l=11.174;size=15
	size=int(size)
	size=15
	# outdoor inn
	##b=50.3736049;l=11.191643
	
	import time
	start=time.time()

	lines=[]
	for ld in range(-size,size): 
		res=run(b,l,b,l +ld*0.001,size)
		lines.append(res)
		res.ViewObject.Visibility=False
		

	ll=App.ActiveDocument.addObject('Part::Loft','Loft')
	ll.Sections=lines
	
	#---------------
	if True:
			import pivy
			from pivy import coin
			obj = ll
			obj.ViewObject.ShapeColor = (1.00,1.00,1.00)
			obj.ViewObject.LineColor = (1.00,1.00,.00)
			obj.ViewObject.LineWidth = 1.00
			
			viewprovider = obj.ViewObject
			root=viewprovider.RootNode
			#myLight = coin.SoDirectionalLight()
			#root.insertChild(myLight, 0)

			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(0,1,0))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)
			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(1,0,0))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)

			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(0,-1,0))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)
			
			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(-1,0,0))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)

			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(0,0,1))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)
			
			l=coin.SoDirectionalLight()
			l.direction.setValue(coin.SbVec3f(0,0,-1))
			l.color.setValue(coin.SbColor(0,1,0))
			root.insertChild(l, 0)


	
	
	
	
	
	
	App.ActiveDocument.recompute()
	ende=time.time()



	# 5 x 5 km   -- 15 sec

	print (ende-start)



def mydialog():
	print "mydialo"
	demo()
	print "done"
