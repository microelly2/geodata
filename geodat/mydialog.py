# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.4
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
		setFixedWidth: 730
		setFixedWidth: 654
		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:
		QtGui.QLineEdit:
			setText:"50.340722, 11.232647"
#			setText:"50.3736049,11.191643"
#			setText:"50.3377879,11.2104096"
			id: 'bl'

		QtGui.QLabel:
		QtGui.QCheckBox:
			id: 'elevation' 
			setText: 'Process Elevation Data'

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"Length of the Square 0 km ... 4 km, default 0.5 km  "
		QtGui.QLabel:
			setText:"0*2_4_6_8*#*2_4_6_8*1*2_4_6_8*#*2_4_6_8*2*2_4_6_8*#*2_4_6_8*3*2_4_6_8*#*2_4_6_8*4"
		QtGui.QSlider:
			id:'s'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 40
			setTickInterval: 1
			setValue: 2
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runbl

		QtGui.QPushButton:
			setText: "Show openstreet map in web browser"
			clicked.connect: app.showMap

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P R E D E F I N E D   L O C A T I O N S"
		QtGui.QLabel:

		QtGui.QRadioButton:
			setText: "Sonneberg Outdoor Inn"
			clicked.connect: app.run_sternwarte

		QtGui.QRadioButton:
			setText: "Coburg university and school "
			clicked.connect: app.run_co2

		QtGui.QRadioButton:
			setText: "Berlin Alexanderplatz/Haus des Lehrers"
			clicked.connect: app.run_alex

		QtGui.QRadioButton:
			setText: "Berlin Spandau"
			clicked.connect: app.run_spandau

		QtGui.QRadioButton:
			setText: "Paris Rue de Seine"
			clicked.connect: app.run_paris

		QtGui.QRadioButton:
			setText: "Tokyo near tower"
			clicked.connect: app.run_tokyo


		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P R O C E S S I N G:"
			id: "status"

		QtGui.QLabel:
			setText:"---"
			id: "status"

		QtGui.QProgressBar:
			id: "progb"

'''

import FreeCAD,FreeCADGui

class App(object):

	def runXX(self):
		print "run app"
		print self
		s=self.root.ids['otto']
		print s
		s.setText('huhwas')
		pb=self.root.ids['progb']
		print s
		v=pb.value()
		pb.setValue(v+5)

	def run(self,b,l):
		import geodat.import_osm
		reload(geodat.import_osm)
		s=self.root.ids['s'].value()
		key="%0.7f" %(b) + "," + "%0.7f" %(l)
		self.root.ids['bl'].setText(key)
		geodat.import_osm.import_osm(b,l,float(s)/10,self.root.ids['progb'],self.root.ids['status'])

	def run_alex(self):
		self.run(52.52128,l=13.41646)

	def run_paris(self):
		self.run(48.85167,2.33669)

	def run_tokyo(self):
		self.run(35.65905,139.74991)

	def run_spandau(self):
		self.run(52.508,13.18)

	def run_co2(self):
		self.run(50.2631171, 10.9483)

	def run_sternwarte(self):
		self.run(50.3736049,11.191643)
# "50.3736049,11.191643

	def runbl(self):
		print "Run values"
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		s=self.root.ids['s'].value()
		elevation=self.root.ids['elevation'].isChecked()
		print [l,b,s]
		import geodat.import_osm
		reload(geodat.import_osm)
		geodat.import_osm.import_osm2(float(b),float(l),float(s)/10,self.root.ids['progb'],self.root.ids['status'],elevation)

	def showMap(self):
		print "Run values"
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		s=self.root.ids['s'].value()
		print [l,b,s]
		import WebGui
		WebGui.openBrowser( "http://www.openstreetmap.org/#map=16/"+str(b)+'/'+str(l))


def mydialog():
	app=App()

	import miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)
