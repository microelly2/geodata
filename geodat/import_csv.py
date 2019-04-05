# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import csv
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


from geodat.say import *

import sys
if sys.version_info[0] !=2:
	from importlib import reload

import FreeCAD,FreeCADGui, Part
App=FreeCAD
Gui=FreeCADGui

import geodat.transversmercator
from  geodat.transversmercator import TransverseMercator

import csv,re

'''
example data csv

50.3729107;11.1913920;"l";"b"
50.3731789;11.1919306;"l";"b"
50.3732226;11.1920048;"l";"b"
50.3732894;11.1920829;"l";"b"
50.3734014;11.1900516;"l";"b"
50.3736555;11.1906749;"l";"b"
50.3734900;11.1904810;"l";"b"
50.3734923;11.1905679;"l";"b"


# python data ...

	origin=(50.3729107,11.1913920)
	
	data=[
		[50.3729107, 11.1913920, "l", "b"],
		[50.3731789, 11.1919306, "l", "b"],
		[50.3732226, 11.1920048, "l", "b"],
		[50.3732894, 11.1920829, "l", "b"],
		[50.3734014, 11.1900516, "l", "b"],
		[50.3736555, 11.1906749, "l", "b"],
		[50.3734900, 11.1904810, "l", "b"],
		[50.3734923, 11.1905679, "l", "b"],
	]

'''


def import_csv(fn,orig,datatext=None):
	# lat lon
	yy=orig.split(',')
	origin=(float(yy[0]),float(yy[1]))

	data=[]
	if len(datatext) != 0:
		lines=datatext.split('\n')
		for l in lines:
			pp=re.split("( )+",l)
			if len(pp)==1:
				continue
			if len(pp)<3:
				raise Exception("Syntax error in 'direct Data input'")
			data.append([str(pp[0]),str(pp[2])])
		print(data)
	else:
		with open(fn, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')
			print (reader)
			for row in reader:
				data.append(row)

	tm=TransverseMercator()
	tm.lat=origin[0]
	tm.lon=origin[1]
	center=tm.fromGeographic(tm.lat,tm.lon)

	points=[]
	for p in data:
		lat,lon = p[0],p[1]
		ll=tm.fromGeographic(float(lat),float(lon))
		points.append( FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],0.0))

	import Draft
	points.append(points[0])
	Draft.makeWire(points)

	po=App.ActiveDocument.ActiveObject
	po.ViewObject.LineColor=(1.0,0.0,0.0)
	po.MakeFace = False

	App.activeDocument().recompute()
	Gui.SendMsgToActiveView("ViewFit")


s6='''
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T    CSV   GEODATA   ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Data input filename"

		QtGui.QLineEdit:
			setText:"/home/thomas/.FreeCAD/Mod/geodat/testdata/csv_example.csv"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get CSV File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"direct Data input  "


		QtGui.QTextEdit:
			setText:""
			id: 'data'

		QtGui.QLabel:
			setText:"Origin (lat,lon) "


		QtGui.QLineEdit:
			setText:"50.3729107,11.1913920"
			id: 'orig'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''

import FreeCAD,FreeCADGui

class MyApp(object):

	def run(self):
		filename=self.root.ids['bl'].text()
		try:
			import_csv(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['data'].toPlainText(),
			)
		except:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		s=self.root.ids['bl']
		s.setText(fileName[0])



def importCSV():
	app=MyApp()

	import geodat.miki as miki
	#reload(miki)


	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)
	return miki


# mydialog()



def runtest():
	m=mydialog()
	m.objects[0].hide()
