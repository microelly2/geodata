#------------
import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui
import Part, Draft

import numpy as np
import numpy.linalg as npl
import time

print "projection tools v0.1"

def mittelpunkt(A,B,C,D):
	''' schnitt der Diagonalen AC und BD '''
	M=np.array([A-C,D-B])
	R=D-C
	x=npl.solve(M.T,R)
	(np.dot(M,x)-R)
	S=x[0]*A+(1-x[0])*C
	return S

def schnittpunkt(A,B,C,D):
	''' schnittpunkt von AB und CD'''
	return mittelpunkt(A,C,B,D)


def vec(A,h=0):
	''' 2D Vektor in FreeCASD Vector '''
	return FreeCAD.Vector(A[0],A[1],h)  

def lotfuss(A,B,C):
	''' fusspunkt des lotes von C auf AB'''
	return A + float(np.dot(C-A,B-A))/np.dot(A-B,A-B) *(B-A)


def mittelpunkt(A,B,C,D):
	''' schnitt der Diagonalen AC und BD '''
	M=np.array([A-C,D-B])
	R=D-C
	x=npl.solve(M.T,R)
	(np.dot(M,x)-R)
	S=x[0]*A+(1-x[0])*C
	return S

def schnittpunkt(A,B,C,D):
	''' schnittpunkt von AB und CD'''
	return mittelpunkt(A,C,B,D)

def zpik(A,C,H,G):
	''' schneide die Verlaengerung von HC mit der Parallelen zu HG durch A  ''' 
	BB=A+G-H
	return schnittpunkt(A,BB,H,C)

def edgesplit(A,B,n):
	''' strecke AB in n teile zerlegen '''
	rc=[]
	s=(B-A)/n
	for i in range(n):
		rc.append(A+s*i)
	rc.append(B)
	return rc

def projectionsplit(A,G,H,Splitter):
	''' projektion einer Zerlegung Splitter von H aus auf AG '''
	rc=[]
	for p in Splitter:
		s=schnittpunkt(A,G,H,p)
		rc.append(s)
	return rc  

def vec(A,h=0):
	''' 2D Vektor in FreeCASD Vector '''
	return FreeCAD.Vector(A[0],A[1],h)  

def refresh():
	return
	FreeCAD.ActiveDocument.recompute()
	FreeCADGui.updateGui() 
	time.sleep(0.1)

def drawline(A,B,Name=''):
	''' AB as FreeCAD Linie '''
	pp=App.ActiveDocument.addObject("Part::Line","Line")
	pp.X1=A[0]
	pp.Y1=A[1]
	pp.Z1=0
	pp.X2=B[0]
	pp.Y2=B[1]
	pp.Z2=0
	if Name:
		p=FreeCAD.Vector((pp.X1+pp.X2)/2,(pp.Y1+pp.Y2)/2,0.0)
		t=Draft.makeText([Name],point=p.add(FreeCAD.Vector(0.3,0.3,0.3)))
		t.Label="Label "+Name
		tv=t.ViewObject
		tv.DisplayMode = "Screen"
		tv.FontSize = 16
		tv.TextColor = (1.00,1.00,0.00)
		pp.Label=Name
		group.addObject(t)
	refresh()
	return pp

def pointat(A,G,Length):
	''' Punkt auf der Strecke AG mit Abstand Length '''
	base=np.sqrt((G[0]-A[0])**2+(G[1]-A[1])**2)
	rc=A+(G-A)*Length/base
	return rc

def pointrelat(A,G,Length):
	''' Punkt auf der Strecke AG mit relativem Abstand Length '''
	return A+(G-A)*Length





#------------

def flucht(a,b):
	A=np.array([a.X1.Value,a.Y1.Value])
	B=np.array([a.X2.Value,a.Y2.Value])
	C=np.array([b.X1.Value,b.Y1.Value])
	D=np.array([b.X2.Value,b.Y2.Value])
	S=schnittpunkt(A,B,C,D)
	return S


def endpunkte(a):
	A=np.array([a.X1.Value,a.Y1.Value])
	B=np.array([a.X2.Value,a.Y2.Value])
	return [A,B]



def endpunktev2(ed):

	A=np.array([ed.Vertexes[0].Point.x,ed.Vertexes[0].Point.y])
	B=np.array([ed.Vertexes[1].Point.x,ed.Vertexes[1].Point.y])
	return [A,B]


def len2(A,B):
	return ((A[0]-B[0])**2+(A[1]-B[1])**2)


def abweichung(F,A,B):
	cosw=(len2(F,A)+len2(F,B)-len2(A,B))/(2*np.sqrt(len2(F,A)*len2(F,B)))
	return round(1-cosw,3)


#----------------------

'''
a=App.ActiveDocument.Line252
b=App.ActiveDocument.Line185

F1=flucht(a,b)

c=App.ActiveDocument.Line3139
d=App.ActiveDocument.Line292
F2=flucht(c,d)

print (F1,F2)

'''


#
# nicht waagerechte und nicht senkrechte linien ausblenden
#


if False:
	n=0
	for c in App.ActiveDocument.Objects:
		n += 1
		#if n>4000: break
		if n<4000: continue
		if n%20 == 0: Gui.updateGui()
		try:
			b=c
			[A,B]=endpunktev2(a)
			
			M=schnittpunkt(F1,F2,A,E)
			w=abweichung(A,F1,M)
			w2=abweichung(A,F2,M)
	#		FreeCAD.Console.PrintMessage(str([n,M,w,w2]) +"\n")
			if w >0 and w2>0:
				b.ViewObject.hide()
				FreeCAD.Console.PrintMessage("-")
			else:
				FreeCAD.Console.PrintMessage("+")
				b.ViewObject.show()
		except:
			pass


#
# Kantenauswahl
#


def _selectBox(box,base):
	sel=[]
	for c in base.Shape.Edges:
		try:
			[E,F]=endpunktev2(c)
		except:
			continue
		ok=True
		for p in [E,F]:
			if  p[0]<box.Shape.BoundBox.XMin: ok=False
			if  p[0]>box.Shape.BoundBox.XMax: ok=False
			if  p[1]<box.Shape.BoundBox.YMin: ok=False
			if  p[1]>box.Shape.BoundBox.YMax: ok=False
		if ok:
			sel.append(c)
	comp=Part.makeCompound(sel)
	Part.show(comp)
	vo=App.ActiveDocument.ActiveObject.ViewObject
	vo.LineColor=(1.0,0.0,0.0)
	vo.LineWidth=10
	return vo

'''
box=App.ActiveDocument.Sketch
sel=_selectBox(box)
'''

def selectionBox():
	return _selectBox(Gui.Selection.getSelection()[0],Gui.Selection.getSelection()[1])


#
# haeufung von geraden
#


def referencepoints(A,F2,sel):
	SP={}
	for c in sel:
		if c.ViewObject.Visibility:
			[E,F]=endpunkte(c)
			try:
				M=schnittpunkt(A,F2,E,F)
				print(round(M[0]),round(M[1]))
				try:
					SP[(round(M[0]/10),round(M[1]/10))] += 1
				except:
					SP[(round(M[0]/10),round(M[1]/10))] = 1
			except:
				pass

	for s in SP:
		print (s,SP[s])
		if SP[s]>0:
			p=App.ActiveDocument.addObject("Part::Vertex","Vertex")
			p.X=s[0]*10
			p.Y=s[1]*10
			p.ViewObject.PointColor=(1.0,0.5,0.)
			if SP[s]>1:
				p.ViewObject.PointSize= 6
				p.ViewObject.PointColor=(1.0,0.5,0.5)





'''
a=App.ActiveDocument.Line252
b=App.ActiveDocument.Line185
F1=flucht(a,b)
[A,B]=endpunkte(a)
[C,D]=endpunkte(b)

c=App.ActiveDocument.Line3139
d=App.ActiveDocument.Line292
F2=flucht(c,d)

referencepoints(A,F2,sel)
'''


def _drawquadrangle(rect):
	# reihenfolge empfildlich

#	for l in rect:
#		l.ViewObject.LineColor=(0.7,.0,.0)

	[a1,a2]=endpunktev2(rect[0])
	[b1,b2]=endpunktev2(rect[1])
	[c1,c2]=endpunktev2(rect[2])
	[d1,d2]=endpunktev2(rect[3])

	SA=schnittpunkt(a1,a2,b1,b2)
	SB=schnittpunkt(b1,b2,c1,c2)
	SC=schnittpunkt(c1,c2,d1,d2)
	SD=schnittpunkt(d1,d2,a1,a2)
	points=[vec(SA),vec(SB),vec(SC),vec(SD)]
	w=Draft.makeWire(points,closed=True,face=True,support=None)
	return w

'''
# testcase
rect=[ App.ActiveDocument.Line2890,
	App.ActiveDocument.Line2681,
	App.ActiveDocument.Line4835,
	App.ActiveDocument.Line2222	]

_drawquadrangle(rect)

'''
# call
def drawquadrangle():
	s=Gui.Selection.getSelectionEx()[0]
	sels=[]
	for s in Gui.Selection.getSelectionEx():
		subs=s.SubObjects
		print subs
		sels += subs
	print "selection ..."
	print Gui.Selection.getSelectionEx()
	print "!!"
	subs=sels
	for ss in subs:
		print ss
	if len(subs)<>4:
		raise Exception("keine vier kanten")
	for e in s.SubObjects: 
		if e.__class__.__name__ <>'Edge':
			raise Exception ("Non edge in selection" + str(e))
	return _drawquadrangle(subs)


def drawface():
	# auswertuing verbessern:  punkte /kanten in reihenfolge
	sels=Gui.Selection.getSelection()
	points=[]
	for e in sels:
		points.append(e.Shape.Vertexes[0].Point)
		#print e
		#print e.Point

	w=Draft.makeWire(points,closed=True,face=True,support=None)
	return w


def drawboundbox():
	sels=Gui.Selection.getSelection()
	xmin=1e+10
	xmax=-1e+10
	zmin=1e+10
	zmax=-1e+10
	for e in sels:
		xmin=min(xmin,e.Shape.BoundBox.XMin)
		xmax=max(xmax,e.Shape.BoundBox.XMax)
		zmin=min(zmin,e.Shape.BoundBox.ZMin)
		zmax=max(zmax,e.Shape.BoundBox.ZMax)

	points=[FreeCAD.Vector(xmin,0,zmin),FreeCAD.Vector(xmax,0,zmin),
		FreeCAD.Vector(xmax,0,zmax),FreeCAD.Vector(xmin,0,zmax),]
	w=Draft.makeWire(points,closed=True,face=True,support=None)
	return w



def numpo(v):
	''' freecad vector to numpy array '''
	return np.array([v.x,v.y])


#
# testcases
#

# drawquadrangle()





class docs(object):

	def run(self,imgName="HoughLines",modelname="Model"):
		
		ld=App.listDocuments()
		for d in ld:
			print (d)
			if d.startswith('HoughLines'):
				imgName=d
				break
		try:
			App.ActiveDocument=App.getDocument(modelname)
			App.setActiveDocument(modelname)
			self.modeldoc=App.ActiveDocument
			
		except:
			self.modeldoc=App.newDocument(modelname)
			App.setActiveDocument(modelname)

		try:
			App.ActiveDocument=App.getDocument(imgName)
			App.setActiveDocument(imgName)
			self.doc=App.ActiveDocument
			Gui.ActiveDocument=Gui.getDocument("HoughLines")
		except:
			self.doc=App.newDocument(imgName)
			App.setActiveDocument(imgName)
			Gui.ActiveDocument=Gui.getDocument("HoughLines")

	def runm(self,imgName="HoughLines",modelname="Model"):


		ld=App.listDocuments()
		for d in ld:
			print (d)
			if d.startswith('HoughLines'):
				imgName=d
				break
		try:
			App.ActiveDocument=App.getDocument(imgName)
			App.setActiveDocument(imgName)
			self.doc=App.ActiveDocument
			Gui.ActiveDocument=Gui.getDocument("HoughLines")
		except:
			self.doc=App.newDocument(imgName)
			App.setActiveDocument(imgName)
			Gui.ActiveDocument=Gui.getDocument("HoughLines")

		try:
			App.ActiveDocument=App.getDocument(modelname)
			App.setActiveDocument(modelname)
			self.modeldoc=App.ActiveDocument
			
		except:
			self.modeldoc=App.newDocument(modelname)
			App.setActiveDocument(modelname)


	def i(self):
			self.run()
			return self.doc
			
	def m(self):
			self.runm()
			return self.modeldoc
			
	def gi(self):
		self.run()
		return FreeCADGui.getDocument("HoughLines")

	def gm(self):
		self.runm()
		return FreeCADGui.getDocument("Model")


class MPviewprovider:
	def __init__(self, obj):
		obj.Proxy = self

def createMP(doc,v=FreeCAD.Vector(),x=FreeCAD.Vector(10,0,0),y=FreeCAD.Vector(0,10,0),z=FreeCAD.Vector(0,0,10)):
	return createMP2('MP',v,x,y,z)

def createMP2(Name,doc,v=FreeCAD.Vector(),x=FreeCAD.Vector(10,0,0),y=FreeCAD.Vector(0,10,0),z=FreeCAD.Vector(0,0,10)):
	''' create model point '''
	obj=doc.getObject(Name)
	if obj==None:
		obj=doc.addObject('Part::FeaturePython',Name)
		obj.addProperty('App::PropertyLink','refLink',"backlinks")
		obj.addProperty('App::PropertyString','refName',"backlinks")
		
		obj.addProperty('App::PropertyVector','pos',"4 layout")
		obj.addProperty('App::PropertyVector','dirX',"4 layout")
		obj.addProperty('App::PropertyVector','dirY',"4 layout")
		obj.addProperty('App::PropertyVector','dirZ',"4 layout")
		obj.addProperty('App::PropertyFloat','scaleCross',"4 layout").scaleCross=1000
		obj.addProperty('App::PropertyBool','showCross',"4 layout").showCross=True
		
		obj.addProperty('App::PropertyString','type',"1 base")
		obj.addProperty('App::PropertyVector','base',"1 base").base=v
		obj.addProperty('App::PropertyString','basePlane',"2 base") # l,r,z
		obj.addProperty('App::PropertyVector','lunit',"2 base")
		obj.addProperty('App::PropertyVector','runit',"2 base")
		obj.addProperty('App::PropertyVector','zunit',"2 base")
		
		obj.addProperty('App::PropertyVector','clickPoint',"3 img")
		
		
		#type MP IP MBP IBP
		
		
	obj.base=v
	obj.dirX=x
	obj.dirY=y
	obj.dirZ=z
	
	
	lines=[]
	for d in [x,y,z]:
		try:
			d.normalize()
			d=d.multiply(20)
			lines.append(Part.makeLine(d.add(v),d.multiply(-1).add(v)))
		except:pass 
	c=Part.makeCompound(lines)
	obj.Shape=c

	MPviewprovider(obj.ViewObject)
	obj.ViewObject.LineColor=(1.0,1.0,.0)
#	if obj.type=='IBP' or obj.type='IBP':
#		obj.ViewObject.PointColor=(1.0,.0,.0)
#	else:
	obj.ViewObject.PointColor=(1.0,.0,1.0)
	obj.ViewObject.PointSize=10
	#obj.ViewObject.Proxy=object()
	#Gui.SendMsgToActiveView("ViewFit")
	
	return obj



#def getref(obj):
#	if obj.type='MP'
#	docs().i.getObject




def createBaseBox(doc,length=1000,width=400,height=200):
	''' create reference box for perspective '''
	createMP2('A',doc,FreeCAD.Vector(0,0,0))
	createMP2('B',doc,FreeCAD.Vector(-length,0,0))
	createMP2('C',doc,FreeCAD.Vector(0,width,0))
	createMP2('D',doc,FreeCAD.Vector(-length,width,0))
	createMP2('E',doc,FreeCAD.Vector(0,0,height))
	createMP2('F',doc,FreeCAD.Vector(-length,0,height))
	createMP2('G',doc,FreeCAD.Vector(0,width,height))
	createMP2('H',doc,FreeCAD.Vector(-length,width,height))



def perspos(target,nullpos,onepos,pol):
	''' perspective position (target) to ortho position '''
	c=np.sqrt(len2(pol,nullpos))
	a=np.sqrt(len2(onepos,nullpos))
	x=np.sqrt(len2(target,nullpos))
	l=(a-c)*x/a/(x-c)
	return l


def reverseperspos(target,nullpos,onepos,pol):
	''' ortho position (target) to perspective position '''
	print "reverse pos"
	print target
	print "null ",nullpos
	print "one ",onepos
	print "pol ",pol
	
	f=np.sqrt(len2(pol,nullpos))
	e=np.sqrt(len2(onepos,nullpos))
	l=f*target/(target+f/e-1)
	print "f ",f
	print "e ",e
	print "f/e ", f/e
	print l
	
	return l

def createGrids(polset,basepoints,refpoint,size=0.2,count=20):

		[p0,p2,p3,p4]=basepoints
		[lp,rp,zp]=polset
		
		count +=1
		
		docs().i()
		rcs=[]
		rc=makePerspectiveGrid(refpoint,lp,p2,p3,zp,"Vertical Left Grid",count,size)
		rc.ViewObject.LineColor=(1.0,.0,.0)
		rcs.append(rc)
		rc=makePerspectiveGrid(refpoint,rp,p4,p3,zp,"Vertical Right Grid",count,size)
		rc.ViewObject.LineColor=(.0,1.,.0)
		rcs.append(rc)
		rc=makePerspectiveGrid(refpoint,zp,p0,p3,lp,"Left Height Grid",count, size)
		rc.ViewObject.LineColor=(.0,.0,1.0)
		rcs.append(rc)
		rc=makePerspectiveGrid(refpoint,zp,p0,p3,rp,"Right Height Grid",count, size)
		rc.ViewObject.LineColor=(.0,.0,1.0)
		rcs.append(rc)
		rc=makePerspectiveGrid(refpoint,rp,p4,p3,lp,"Horizontal Left Grid",count, size)
		rc.ViewObject.LineColor=(.0,1.0,.0)
		rc.ViewObject.hide()
		rcs.append(rc)
		rc=makePerspectiveGrid(refpoint,lp,p2,p3,rp,"Horizontal Right Grid",count, size)
		rc.ViewObject.LineColor=(1.0,.0,0.0)
		rc.ViewObject.hide()
		rcs.append(rc)
		return rcs


def makePerspectiveGrid(refpoint,pol,unitpoint,zeropoint,pol2,name="Pers Grid",count=10,relativ=1):
			lines=[]
			f=np.sqrt(len2(pol,zeropoint))
			e=np.sqrt(len2(unitpoint,zeropoint))
#			print ("f,e",f,e)
			for i in range(count):
				dist=e*f*i*relativ/((i*relativ-1)*e+f)
				p=pointat(zeropoint,pol,dist)
				lval=perspos(p,zeropoint,unitpoint,pol)
#				print (i,dist,lval)
				## lines.append(Part.makeLine(vec(pol2),vec(p).add(refpoint)))
				lines.append(Part.makeLine(vec(pol2),vec(p)))
			comp=Part.makeCompound(lines)
			obs=App.ActiveDocument.getObjectsByLabel(name)
			if len(obs)>0:
				obs[0].Shape=comp
				return obs[0]
			else:
				Part.show(comp)
				App.ActiveDocument.ActiveObject.Label=name
				return App.ActiveDocument.ActiveObject



def makeBase(l,z,lpol,zpol,lone,zone,zero):

	lines=[]
	f=np.sqrt(len2(lpol,zero))
	e=np.sqrt(len2(lone,zero))
	dist=e*f*l/((l-1)*e+f)
	pa=pointat(zero,lpol,dist)
	print (l,z,dist,pa)

#	lines.append(Part.makeLine(vec(zpol),vec(pa)))	
#	lines.append(Part.makeCircle(10000,vec(pa)))

	f=np.sqrt(len2(zpol,zero))
	e=np.sqrt(len2(zone,zero))
	dist=e*f*z/((z-1)*e+f)
	pb=pointat(zero,zpol,dist)
	print (l,z,dist,pb)

#	lines.append(Part.makeLine(vec(lpol),vec(pb)))	
#	lines.append(Part.makeCircle(10000,vec(pb)))
	pc=schnittpunkt(lpol,pb,zpol,pa)
	print (pa,pb,pc)
	lines.append(Part.makeCircle(15000,vec(pc)))
	comp=Part.makeCompound(lines)
#	Part.show(comp)

	return pc




import Draft

def genLabel(name,pt):
	''' label as textobject in FreeCAD3D '''
	p=FreeCAD.Vector(pt[0],pt[1],0)
	t=Draft.makeText([name],point=p.add(FreeCAD.Vector(1000,1000,10)))
	t.Label=name
	tv=t.ViewObject
	tv.DisplayMode = "Screen"
	tv.FontSize = 20
	tv.TextColor = (1.00,0.00,0.00)
	tt=Draft.makePoint(p)
	tt.ViewObject.PointColor=(1.00,0.00,0.00)
	return t




