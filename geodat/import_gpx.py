# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- gpx importer
#--
#-- microelly 2016 v 0.0
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from say import *

# test-data from https://en.wikipedia.org/wiki/GPS_Exchange_Format

trackstring='''
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" creator="Oregon 400t" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
  <metadata>
    <link href="http://www.garmin.com">
      <text>Garmin International</text>
    </link>
    <time>2009-10-17T22:58:43Z</time>
  </metadata>
  <trk>
    <name>Example GPX Document</name>
    <trkseg>
      <trkpt lat="47.644548" lon="-122.326897">
        <ele>4.46</ele>
        <time>2009-10-17T18:37:26Z</time>
      </trkpt>
      <trkpt lat="47.644549" lon="-122.326898">
        <ele>4.94</ele>
        <time>2009-10-17T18:37:31Z</time>
      </trkpt>
      <trkpt lat="47.644550" lon="-122.326898">
        <ele>6.87</ele>
        <time>2009-10-17T18:37:34Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
'''


# https://de.wikipedia.org/wiki/GPS_Exchange_Format
'''
<ele> xsd:decimal </ele>                     <!-- Höhe in m -->
<time> xsd:dateTime </time>                  <!-- Datum und Zeit (UTC/Zulu) in ISO 8601 Format: yyyy-mm-ddThh:mm:ssZ -->
<magvar> degreesType </magvar>               <!-- Deklination / magnetische Missweisung vor Ort in Grad -->
<geoidheight> xsd:decimal </geoidheight>     <!-- Höhe bezogen auf Geoid -->
<name> xsd:string </name>                    <!-- Eigenname des Elements -->
<cmt> xsd:string </cmt>                      <!-- Kommentar -->
<desc> xsd:string </desc>                    <!-- Elementbeschreibung -->
<src> xsd:string </src>                      <!-- Datenquelle/Ursprung -->
<link> linkType </link>                      <!-- Link zu weiterführenden Infos -->
<sym> xsd:string </sym>                      <!-- Darstellungssymbol -->
<type> xsd:string </type>                    <!-- Klassifikation -->
<fix> fixType </fix>                         <!-- Art der Positionsfeststellung: none, 2d, 3d, dgps, pps -->
<sat> xsd:nonNegativeInteger </sat>          <!-- Anzahl der zur Positionsberechnung herangezogenen Satelliten -->
<hdop> xsd:decimal </hdop>                   <!-- HDOP: Horizontale Streuung der Positionsangabe -->
<vdop> xsd:decimal </vdop>                   <!-- VDOP: Vertikale Streuung der Positionsangabe -->
<pdop> xsd:decimal </pdop>                   <!-- PDOP: Streuung der Positionsangabe -->
<ageofdgpsdata> xsd:decimal </ageofdgpsdata> <!-- Sekunden zwischen letztem DGPS-Empfang und Positionsberechnung -->
<dgpsid> dgpsStationType:integer </dgpsid>   <!-- ID der verwendeten DGPS Station -->
<extensions> extensionsType </extensions>    <!-- GPX Erweiterung -->
'''

import time, json, os

import urllib2

import pivy 
from pivy import coin

import FreeCAD,FreeCADGui, Part
App=FreeCAD
Gui=FreeCADGui

import geodat.transversmercator
from  geodat.transversmercator import TransverseMercator

import geodat.inventortools

import geodat.xmltodict
from  geodat.xmltodict import parse

import time
debug=1




global sd

def import_gpx(filename,orig,hi):
	global sd
	# content=trackstring
	
#	'/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/neufang.gpx'
#	fn='/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/im_haus.gpx'
#	fn='/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/neufang.gpx'
	
	f=open(filename,"r")
	c1=f.read()
	import re
	content = re.sub('^\<\?[^\>]+\?\>', '', c1)
	print content
	
	
	tm=TransverseMercator()

	# outdoor inn ...
	tm.lat,tm.lon = 50.3736049,11.191643
	
	yy=orig.split(',')
	origin=(float(yy[0]),float(yy[1]))
	tm.lat=origin[0]
	tm.lon=origin[1]
#	center=tm.fromGeographic(tm.lat,tm.lon)
	
	sd=parse(content)
	if debug: print(json.dumps(sd, indent=4))

	print "huhu"
	
	points=[]
	points2=[]
	px=[]
	py=[]
	
	startx=None
	starty=None
	starth=None
	
	seg=sd['gpx']['trk']['trkseg']
	for s in seg:
		trkpts=s['trkpt']


		n=trkpts[0]
		# tm.lat, tm.lon = float(n['@lat']), float(n['@lon'])
		
		center=tm.fromGeographic(tm.lat,tm.lon)

		print trkpts
		for p in  trkpts:
			print p

		# map all points to xy-plane
		for n in trkpts:
			print n['@lat'],n['@lon']
			ll=tm.fromGeographic(float(n['@lat']),float(n['@lon']))
			h=n['ele']
			print h
			if starth == None:
				starth=float(h)
			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)))
			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],0))
			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)))
			points2.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)+20000))
			px.append(ll[0]-center[0])
			py.append(ll[1]-center[1])
			print ll

	if 1:
		import Draft
		if 0: #close path
			points.append(points[0])
		
		Draft.makeWire(points)

		po=App.ActiveDocument.ActiveObject
		po.ViewObject.LineColor=(1.0,.0,0.0)
		po.MakeFace = False
		say(hi)
		
		po.Placement.Base.z= float(hi) *1000
		po.Label="My Track" 
		

		Draft.makeWire(points2)

		po2=App.ActiveDocument.ActiveObject
		po2.ViewObject.LineColor=(.0,.0,1.0)
		po2.ViewObject.PointSize=5
		po2.ViewObject.PointColor=(.0,1.0,1.0)
		
		po2.Placement.Base.z= float(hi)*1000
		po2.Label="Track + 20m"


		App.activeDocument().recompute()
		Gui.SendMsgToActiveView("ViewFit")
		# break

	return px,py

if 0: 
	px,py=import_gpx()
	count=len(px)
	pp=range(count)
	px2=[]
	py2=[]

	import numpy as np
	xpp=np.array(px)
	np.average(xpp)
	std=np.std(xpp)

	for p in pp:
		if abs(px[p]) <2*std:
			px2.append(px[p])
		else:
			if px[p]>0:
				px2.append(2*std)
			else:
				px2.append(-2*std)

	for p in pp:
		if abs(py[p]) <10000:
			py2.append(py[p])
		else:
			py2.append(10000.0)
			

	import matplotlib.pyplot as plt

	#plt.plot(pp,px,pp,py)
	#plt.show()

	plt.hist(px2)
	# plt.hist(py2)
	#plt.show()


# px,py=import_gpx()



s6='''
VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T    GPX  T R A C K    ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Track input filename"

		QtGui.QLineEdit:
			setText:"/tmp/neufang.gpx"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get GPX File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"Origin (lat,lon) "

		QtGui.QLineEdit:
			setText:"50.3736049,11.191643"
			id: 'orig'

		QtGui.QLabel:
			setText:"relative Height of the Startpoint"

		QtGui.QLineEdit:
			setText:"-197.55"
			id: 'h'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''

import FreeCAD,FreeCADGui

class MyApp(object):

	def run(self):
		filename=self.root.ids['bl'].text()
		try:
			import_gpx(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['h'].text(),
			)
		except:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		print fileName
		s=self.root.ids['bl']
		s.setText(fileName[0])


def mydialog():
	app=MyApp()

	import geodat
	import geodat.miki as miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)


# mydialog()






