# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD, FreeCADGui, Draft

import urllib2, json, time
import pivy
from pivy import coin

import geodat.transversmercator
from  geodat.transversmercator import TransverseMercator
import inventortools
		
tm=TransverseMercator()

def getheight(b,l):

	source="https://maps.googleapis.com/maps/api/elevation/json?locations="+str(b)+','+str(l)
	response = urllib2.urlopen(source)
	ans=response.read()
	print ans
	s=json.loads(ans)
	res=s['results']
	for r in res:
		return round(r['elevation']*1000,2)

def run(b0=50.35,l0=11.17,b=50.35,le=11.17,size=40):

	tm.lat=b0
	tm.lon=l0
	baseheight=getheight(tm.lat,tm.lon)
	center=tm.fromGeographic(tm.lat,tm.lon)
	
	print "Base height ", baseheight
	print "center point", center

	source="https://maps.googleapis.com/maps/api/elevation/json?locations="
	
	for i in range(-size,size):
		bb=b+i*0.001
		ss=str(bb)+','+str(le)
		if i < size -1:
			ss += '|'
		source += ss

	response = urllib2.urlopen(source)
	ans=response.read()
	#+# to do: error handling  - wait and try again
	print ans
	s=json.loads(ans)
	res=s['results']
	
	points=[]
	for r in res:
		c=tm.fromGeographic(r['location']['lat'],r['location']['lng'])
		v=FreeCAD.Vector(
					round((c[0]-center[0]),2),
					round((c[1]-center[1]),2), 
					round(r['elevation']*1000,2)-baseheight
				)
		points.append(v)
	
	Draft.makeWire(points,closed=False,face=False,support=None)
	FreeCAD.activeDocument().recompute()
	FreeCADGui.updateGui()
	return FreeCAD.activeDocument().ActiveObject
	

def import_heights(b,le,size):

	size=int(size)
	size=30

	lines=[]
	for ld in range(-size,size): 
		res=run(b,le,b,le +ld*0.001,size)
		lines.append(res)

	ll=FreeCAD.activeDocument().addObject('Part::Loft','Loft')
	ll.Sections=lines
	for li in lines:
		li.ViewObject.Visibility=False

	inventortools.setcolorlights(ll)
	FreeCAD.activeDocument().recompute()
