# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

'''
{
   "error_message" : "You have exceeded your daily request quota for this API. We recommend registering for a key at the Google Developers Console: https://console.developers.google.com/",
   "results" : [],
   "status" : "OVER_QUERY_LIMIT"
}

'''




s6='''
VerticalLayout:
		id:'main'
		setFixedHeight: 600
		setFixedWidth: 600
		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:
		QtGui.QLineEdit:
			setText:"50.3736049,11.191643"
			id: 'bl'
		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runbl


		QtGui.QPushButton:
			setText: "Run Alexanderplatz  Haus des Lehrers"
			clicked.connect: app.run_alex


		QtGui.QPushButton:
			setText: "Run Paris Rue de Seine"
			clicked.connect: app.run_paris

		QtGui.QPushButton:
			setText: "Run Tokyo near tower"
			clicked.connect: app.run_tokyo



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
		

	def run_alex(self):
		import geodat.import_osm
		reload(geodat.import_osm)
		s=self.root.ids['s'].value()

		#52.5219184,13.4110207
		
		b=52.52128
		l=13.41646
		print s
		geodat.import_osm.import_osm(b,l,float(s)/10,self.root.ids['progb'],self.root.ids['status'])


	def run_paris(self):
		import geodat.import_osm
		reload(geodat.import_osm)
		s=self.root.ids['s'].value()
		b=48.85167
		l=2.33669
		print s
		geodat.import_osm.import_osm(b,l,float(s)/10,self.root.ids['progb'],self.root.ids['status'])





	def run_tokyo(self):
		import geodat.import_osm
		reload(geodat.import_osm)
		s=self.root.ids['s'].value()
		b=35.65905
		l=139.74991
		print s
		geodat.import_osm.import_osm(b,l,float(s)/10,self.root.ids['progb'],self.root.ids['status'])


	def run3(self):
		import geodat.import_osm
		s=self.root.ids['s'].value()
		geodat.import_osm.import_osm(52.508,13.18,float(s)/10,self.root.ids['progb'],self.root.ids['status'])

	def run_co2(self):
		import geodat.import_osm
		geodat.import_osm.import_osm( 50.2631171, 10.9483,1.2,self.root.ids['progb'],self.root.ids['status'])

	def runbl(self):
		print "Run values"
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		
		
		s=self.root.ids['s'].value()
		print [l,b,s]
		import WebGui
#		WebGui.openBrowser( "http://www.openstreetmap.org/#map=19/"+str(b)+'/'+str(l))
		import geodat.import_osm
		reload(geodat.import_osm)
		print "Start"
		geodat.import_osm.import_osm(float(b),float(l),float(s)/10,self.root.ids['progb'],self.root.ids['status'])



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
