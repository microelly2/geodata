# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import csv
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


from say import *
import Points

import geodat.transversmercator
from  geodat.transversmercator import TransverseMercator

import csv,re


def setNice(flag=True): 
	''' make smooth skins '''
	p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part")
	w=p.GetFloat("MeshDeviation")
	if flag:
		p.SetFloat("MeshDeviation",0.05)
	else:
		p.SetFloat("MeshDeviation",0.5)



'''
datenquelle
http://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/gelaendemodelle/index.html
siehe auch 
http://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/3d_gebaeudemodelle/index.html

http://www.opengeospatial.org/standards/citygml
https://www.youtube.com/watch?v=U0UBNrAr-j0&feature=youtu.be

http://www.cpa-software.de/index.php?do=zei&lang=d
http://www.businesslocationcenter.de/berlin3d-downloadportal/
http://www.3dcitydb.net/3dcitydb/downloads/

'''




'''
example data
32356000.00 5638000.00   50.48
32356000.00 5638001.00   50.47
32356000.00 5638002.00   50.49
32356000.00 5638003.00   50.47
32356000.00 5638004.00   50.46
32356000.00 5638005.00   50.47
32356000.00 5638006.00   50.46
32356000.00 5638007.00   50.46
32356000.00 5638008.00   50.46
'''


def getShape(pts):

	sx=pts[0][0]
	sy=pts[0][1]
	d0=0

	for i,p in enumerate(pts):
		ex=p[0]
		ey=p[1]
		d=abs(sx-ex)+abs(sy-ey)
		if d<d0:
			break
		d0=d

	assert(len(pts)%i == 0)
	return i,len(pts)//i


def reduceGrid(pts,ku=100,kv=50):
	''' simplifiy data '''

	wb, eb, sb, nb = 3, 3, 3, 3
	lu,lv=getShape(pts)

	pts2=[]
	for v in range(lv):
		if v<sb or v>lv-nb-1:
			pass
		else:
			if v%kv <>0: continue
		for u in range(lu):
			if u<wb or u>lu-eb-1:
				pass
			else:
				if u%ku <>0: continue 
			pts2.append(pts[v*lu+u])

#	p=Points.Points(pts2)
#	Points.show(p)
	return pts2


def showFrame(pts,u=0,v=0,d=10,lu=None,lv=None):

	if lu == None or lv == None:
		lu,lv=getShape(pts)

	say((lu,lv,u,v,d))
	assert(u+d<lu)
	assert(v+d<lv)

	try:
		ff=FreeCAD.ActiveDocument.frame
	except:
		ff=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","frame")
		ViewProvider(ff.ViewObject)

	a,b,c,d = pts[u+v*lu], pts[u+v*lu+d],  pts[u+v*lu +d*lu +d],pts[u+v*lu +d*lu],
	sha=Part.makePolygon([a,b,c,d,a])

	ff.Shape=sha
	ff.ViewObject.show()

def removeFrame():
	App.ActiveDocument.removeObject("frame")


def import_xyz(filename="/tmp/test.xyz",ku=20, kv=10):

	say("iport")
	try:
		App.ActiveDocument.Points
		say("use Points")
		return App.ActiveDocument.Points.Points.Points
	except:
		nurbs=App.getDocument("Unnamed").addObject("App::DocumentObjectGroup","nurbs")
		grids=App.getDocument("Unnamed").addObject("App::DocumentObjectGroup","grids")
		points=nurbs=App.getDocument("Unnamed").addObject("App::DocumentObjectGroup","points")

#		filename='/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz'
		f=open(filename)
		lines=f.readlines()
		print len(lines)

		pts=[]
		for a in range(2000):
			for b in range(2000):
				i=a+2000*b
				l=lines[i]

				p=l.split()
				# utm coords 32356000.00 5638000.00
				# height scale factor
				hfac=3

				pts.append(FreeCAD.Vector(float(p[0])-32356000.00,float(p[1])-5638000.00,hfac*float(p[2])))

		if ku>1 and kv>1:
			pts=reduceGrid(pts,ku,kv)

		p=Points.Points(pts)
		Points.show(p)
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.0,1.0,0.0)
		App.ActiveDocument.ActiveObject.ViewObject.PointSize=1.0
		Gui.updateGui()
		Gui.SendMsgToActiveView("ViewFit")
		App.ActiveDocument.ActiveObject.ViewObject.hide()
	print(len(pts))
	return pts


sdialog='''
#VerticalLayoutTab:
VerticalLayout:
	id:'main'

	QtGui.QLabel:
		setText:"***   I M P O R T    Data from xyz   ***"
	QtGui.QLabel:

	QtGui.QPushButton:
		setText: "Browse for input data filename"
		clicked.connect: app.getfn

	QtGui.QLineEdit:
		setText:"/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz"
		id: 'bl'

	QtGui.QLabel:
		setText:"Reduction Factor  "

	QtGui.QLineEdit:
		setText:"5"
		id: 'ku'

	QtGui.QLineEdit:
		setText:"5"
		id: 'kv'


#	QtGui.QLabel:
#		setText:"Origin (lat,lon) "


	QtGui.QPushButton:
		setText: "initialize values"
		clicked.connect: app.run


	QtGui.QLabel:
		setText:"Frame position"

	QtGui.QDial:
		setValue: 0
		id: 'ud'
		setMinimum: 0
		setMaximum: 200
		setTickInterval: 1
		valueChanged.connect: app.showFrame


	QtGui.QDial:
		setValue: 0
		id: 'vd'
		setMinimum: 0
		setMaximum: 200
		setTickInterval: 1
		valueChanged.connect: app.showFrame

	QtGui.QLabel:
		setText:"Frame size"

	QtGui.QDial:
		setValue: 5
		id: 'dd'
		setMinimum: 1
		setMaximum: 100
		setTickInterval: 1
		valueChanged.connect: app.update2


	QtGui.QPushButton:
		setText: "hide Frame"
		clicked.connect: app.hideFrame

	QtGui.QPushButton:
		setText: "create Nurbs"
		clicked.connect: app.createNurbs

'''

import FreeCAD,FreeCADGui

class MyApp(object):

	def update(self):
		lu,lv = getShape(self.pts)
		dmax = min(lu - self.root.ids['ud'].value(), lv - self.root.ids['vd'].value(),101) -1
		self.root.ids['dd'].setMaximum(dmax)
		if self.root.ids['dd'].value() >dmax:
			self.root.ids['dd'].setValue(dmax)
		self.root.ids['vd'].setMaximum(lv-self.root.ids['dd'].value())
		self.root.ids['ud'].setMaximum(lu-self.root.ids['dd'].value())

	def update2(self):
		self.update()
		self.showFrame()

	def run(self):
		filename=self.root.ids['bl'].text()
		filename='/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz'
		try:
			ts=time.time()
			self.pts=import_xyz(
					filename,
					int(self.root.ids['ku'].text()),
					int(self.root.ids['kv'].text())
			)
			te=time.time()
			say("load points time " + str(round(te-ts,2)))
			say(("points",len(self.pts)))
			self.update()
		except:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		print fileName
		s=self.root.ids['bl']
		s.setText(fileName[0])

	def hideFrame(self):
		removeFrame()

	def showFrame(self):
		u=self.root.ids['ud'].value()
		v=self.root.ids['vd'].value()
		d=self.root.ids['dd'].value()
		showFrame(self.pts,u,v,d)


	def createNurbs(self):
		say("create nurbs")
		u=self.root.ids['ud'].value()
		v=self.root.ids['vd'].value()
		d=self.root.ids['dd'].value()
		lu,lv = getShape(self.pts)
		say((u,v,d,lu,lv))
		suv(self,u,v,d+1,lu,lv)


def mydialog(run=True):
	app=MyApp()

	import geodat
	import geodat.miki as miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki

#	miki.parse2(sdialog)
	miki.run(sdialog)
	return app

import cProfile


# app2=mydialog(False)
# app.run()
# t=app.root.roots()
# t[0][7].hide()




# punkte menge 
# app.pts


# test scheibe und lesen np array file
def run(app):

	#from tempfile import TemporaryFile
	#outfile = TemporaryFile()

	fn="/tmp/npexport"
	outfile=open(fn,"w")
	x = np.array(app.pts).reshape(200,200,3)
	np.save(outfile, x)
	outfile.close()

	outfile=open(fn)
	t=np.load(outfile)
	print t.shape
	return t


def create_grid(pu,du,dv, wb, eb, sb, nb, color=(1.0,0.0,0.0)):
		''' create a grid of BSplineSurface bs with ct lines and rows '''
		ts=time.time()
		sss=[]
#		say([ ("du dv",du,dv)])
#		print "len pu ",len(pu)

		for iu in range(sb,dv-nb):
			pps=[]
			for iv in range(wb,du-eb):
				pps.append(pu[iu*du+iv])
			tt=Part.BSplineCurve()
			tt.interpolate(pps)
			ss=tt.toShape()
			sss.append(ss)
#			if iu > sb+3: break

		if 1:
			for iv in range(wb,du-eb):
				pps=[]
				for iu in range(sb,dv-nb):
					pps.append(pu[iu*du+iv])
				tt=Part.BSplineCurve()
				tt.interpolate(pps)
				ss=tt.toShape()
				sss.append(ss)
		
		comp=Part.Compound(sss)

		Part.show(comp)
		App.ActiveDocument.ActiveObject.ViewObject.LineColor=color
		App.ActiveDocument.grids.addObject(App.ActiveDocument.ActiveObject)
		te=time.time()
		say(["create grid time ",round(te-ts,5) ])
		return App.ActiveDocument.ActiveObject


def create_pcl(pu,color=(1.0,0.0,0.0)):
	p=Points.Points(pu)
	Points.show(p)
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	App.ActiveDocument.points.addObject(App.ActiveDocument.ActiveObject)
	Gui.updateGui()


class ViewProvider:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj
		# obj.hide()


def suv(app,u=3,v=5,d=10,la=100,lb=100):
	'''generate quad on startposition u,v wit size d)'''

	print app
	st=time.time()
	tt=Part.BSplineSurface()
	wb, eb, sb, nb = 0, 0, 0, 0
	if u>=2: wb=2
	if u<la-2-d: eb=2
	if v>=2: sb=2
	if v<la-2-d: nb=2
	uu=[]
	du=d+wb+eb
	dv=d+nb+sb
	u=u-wb
	v=v-sb
	pu=[]
	say([ "(wb,eb,sb,nb,du,dv)", (wb,eb,sb,nb,du,dv)])
	for k in range(dv):
		#print ("zeile",k,u+v*lb+la*k,u+v*lb+du+la*k)
		print ("zeile",k,u+v*la+la*k,u+v*la+du+la*k)
		pu += app.pts[u+v*la+la*k:u+v*la+du+la*k]
		#pu += app.pts[u+v*lb+la*k:u+v*lb+du+la*k]
		# if k%3 <>0 and k>2 and k < dv-4 : continue
		uu.append(app.pts[u+v*la+la*k:u+v*la+du+la*k])

	color=(1-0.5*random.random(),1-0.5*random.random(),1-0.5*random.random())

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	# create point cloud
	create_pcl(pu,color)
	Gui.updateGui()

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	#create bspline grid
	create_grid(pu,du,dv, wb, eb, sb, nb, color)
	Gui.updateGui()

	tt.interpolate(uu)
	uk=tt.getUKnots()
	vk=tt.getVKnots()
	tt.segment(uk[sb],uk[-1-nb],vk[wb],vk[-1-eb])
	sha=tt.toShape()
	se=time.time()
	say(["running time for one shape ", round(se-st,5)])

	# alternative
	# Part.show(sha)

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","mynurbs")
	ViewProvider(a.ViewObject)
	a.Shape=sha


	se=time.time()
	say([ "running time for show the shape ", round(se-st,5)])
	
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	App.ActiveDocument.nurbs.addObject(App.ActiveDocument.ActiveObject)
	Gui.ActiveDocument.update()
	return tt




# generate 100 quads with each 100 interpolation points
'''
st=time.time()
for vx in range(10):
	for ux in range(10):
		tt=suv(2+9*ux,2+18*vx)

se=time.time()

print "running time for 100 quads"
print round(se-st,1)
'''

'''
# range 22,10
st=time.time()
for vx in range(22):
	for ux in range(11):
		tt=suv(0+9*ux,0+9*vx)

se=time.time()
print "running time all"
print round(se-st,1)
'''

# suv(90,0)
#suv(0,0)
#suv(10,0)


'''
Kreuz Koeln Sued
50.8869691,6.9658102


32356_5638

'''


'''
suv(140,40,20,2000,2000)

#mitte kreuzung
suv(1000,1000,80,2000,2000)

#abfahrt
suv(1100,920,50,2000,2000)

# unten
suv(800,40,50,2000,2000)

# see
suv(300,500,60,2000,2000)
'''

'''
# lasttest
for i in range(10,110,10):
	say("\n")
	say(i)
	suv(1000,1000,i,2000,2000)
'''


