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



# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


s6='''
MainWindow:
	VerticalLayout:
		id:'main'
		setFixedHeight: 600
		setFixedWidth: 600
		move:  PySide.QtCore.QPoint(3000,100)
		
		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:


		QtGui.QLineEdit:
			setText:"50.3377879,11.2104096"
#			setText:"50.3736049,11.191643"

			id: 'bl'
		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runbl


		QtGui.QRadioButton:
			setText: "0"
			clicked.connect: app.radio_0
		QtGui.QRadioButton:
			setText: "a"
			clicked.connect: app.radio_a

'''

ss='''

		QtGui.QLabel:
			setText:"Latitude"

		QtGui.QLineEdit:
			setText:"50.2631171"
			id: 'b'




		QtGui.QLabel:
			setText:"Longitude"
		QtGui.QLineEdit:
			setText:"10.9483120"
			id: 'l'
		QtGui.QLabel:
			setText:"Length of the Square 0,1 km ... 4 km"
		QtGui.QSlider:
			id:'s'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 1
			setMaximum: 40
			setTickInterval: 1
			setValue: 2
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runValues

		QtGui.QPushButton:
			setText: "Show openstreet map in web browser"
			clicked.connect: app.showMap

		QtGui.QLabel:
		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P R E D E F I N E D   L O C A T I O N S"

		QtGui.QPushButton:
			setText: "Run import spandau"
			clicked.connect: app.run3

		QtGui.QPushButton:
			setText: "Run import coburg university and school "
			clicked.connect: app.run_co2
		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P R O C E S S I N G:"
			id: "status"


		QtGui.QLabel:
			setText:"---"
			id: "status"

		QtGui.QProgressBar:
			id: "progb"
#		QtGui.QSlider:
#			id:'slider'
#			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
#			valueChanged.connect: app.run2

'''

import FreeCAD,FreeCADGui

class App(object):

	def radio_0(self):
		print "clicked"
		print "0"

	def radio_a(self):
		print "clicked"
		print "a"



	def run(self):
		print "run app"
		print self
		s=self.root.ids['otto']
		print s
		s.setText('huhwas')
		pb=self.root.ids['progb']
		print s
		v=pb.value()
		pb.setValue(v+5)


	def run2(self,v=1234):
		print "run2 app"
		print self
		print "value ",v
		s=self.root.ids['otto']
		print s
		pb=self.root.ids['progb']
		print s
		pb.setValue(v)
		
	def run3(self):
		import geodat.import_osm
		geodat.import_osm.import_osm(52.508,13.18,1.3,self.root.ids['progb'],self.root.ids['status'])

	def run_co2(self):
		import geodat.import_osm
		geodat.import_osm.import_osm( 50.2631171, 10.9483,1.2,self.root.ids['progb'],self.root.ids['status'])

	def runbl(self):
		print "Run values"
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		
		
		# s=self.root.ids['s'].value()
		s=15
		print [l,b,s]
		import WebGui
#		WebGui.openBrowser( "http://www.openstreetmap.org/#map=19/"+str(b)+'/'+str(l))
		#import geodat.import_heights
		#reload(geodat.import_heights)
		print "Start"
		import_heights(float(b),float(l),float(s))



	def runValues(self):
		print "Run values"
		b=self.root.ids['b'].text()
		l=self.root.ids['l'].text()
		s=self.root.ids['s'].value()
		print [l,b,s]
		import WebGui
#		WebGui.openBrowser( "http://www.openstreetmap.org/#map=19/"+str(b)+'/'+str(l))
		import geodat.import_osm
		print "Start"
		geodat.import_osm.import_osm(float(b),float(l),float(s)/10,self.root.ids['progb'],self.root.ids['status'])
		

	def showMap(self):
		print "Run values"
		b=self.root.ids['b'].text()
		l=self.root.ids['l'].text()
		s=self.root.ids['s'].value()
		print [l,b,s]
		import WebGui
		WebGui.openBrowser( "http://www.openstreetmap.org/#map=16/"+str(b)+'/'+str(l))
		

# =17/50.26286/10.94804




def mydialog():
	app=App()

	import miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki


	miki.parse2(s6)

	miki.run(s6)
	m=miki.ids['main']


def mytest():
	app=App()

	import geodat.miki as miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki


	miki.parse2(s6)

	miki.run(s6)
	m=miki.ids['main']


# mytest()



