# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- miki - my kivy like creation tools
#--
#-- microelly 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------




def creatorFunction(name):
	print "creator Function :", name
#	if name.startswith('Part::'):
#		return "App.activeDocument().addObject(name,'test')"
	if name.startswith('Part.'):
		print "huhu"
		[a,c]=name.split('.')
		return "App.activeDocument().addObject('Part::"+c+"','test')"

	if name.startswith('So'):
		return "coin."+name+'()'
	if name.startswith('QtGui'):
		return name+"()"
# QtGui.QPushButton()

	if name.startswith('Animation'):
		[a,c]=name.split('.')
		return 'Animation.create' +c + '()'


	if name in ['Plugger','Manager']:
		return 'Animation.create'+name+'()'
	return name+'()'
#	print "no creater Function ***************************"
	return None



import FreeCAD,Animation,FreeCADGui
import re
import pivy
from pivy import coin

App=FreeCAD

import PySide
from PySide import QtCore, QtGui, QtSvg

import traceback,sys
def sayexc(mess=''):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=[lls[(l-3)],lls[(l-1)]]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))
	print (mess + "\n" +"-->  ".join(l2))



#***************
YourSpecialCreator=Animation.createManager

def  fv(name="vertical"):
	w=QtGui.QWidget()
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

###	w.setStyleSheet("QWidget { font: bold 18px;color:brown;border-style: outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout = QtGui.QVBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignTop)
	w.setLayout(layout)

#	pB= QtGui.QLabel(name)
#	layout.addWidget(pB)
	w.show()
	w.layout=layout
	return w

def  fh(name="horizontal"):
	w=QtGui.QWidget()
###	w.setStyleSheet("QWidget { font: bold 18px;color:blue;border-style: outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout = QtGui.QHBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
	w.setLayout(layout)
#	pB= QtGui.QLabel(name)
#	pB.setStyleSheet("QWidget { font: bold 18px;color:red;border-style: outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
#	layout.addWidget(pB)
	w.show()
	w.layout=layout
	return w


VerticalLayout=fv
HorzontalLayout=fh

#***************


class Miki():
	def __init__(self):
		self.objects=[]
		self.anchors={}
		self.indents=[]
		self.olistref=[]
		self.indpos=-1
		self.app=None
		self.ids={}
		self.classes={}



	def parse2(self,s):

		ls=s.splitlines()

		app=self.app
		line=0
		depth=0
		d=[0,0,0,0,0,0,0,0,0,0]
		ln=[0,0,0,0,0,0,0,0,0,0]
		refs={}
		rs=[]
		r=None
		r=[-1,0,0,'']
		for l in ls:
			if r: 
				rs.append(r)
				r=[-1,0,0,'']
			line += 1
			print l
			if l.startswith('#:'):
				res=re.search("#:\s*(\S.*)",l)
				r=[l,line,-1,'cmd',res.group(1)]
				continue

			if l.startswith('#'):
				continue
				
			res=re.search("\<(\S.*)\>:",l)
			if res:
					parent=0
					ln[0]=line
					depth=0
					r=[l,line,parent,"local class",res.group(1)]
					self.classes[res.group(1)]=line
					continue

			res=re.search("(\s*)(\S.*)",l)
			if res:
				l=len(res.group(1))
				if l==0:
					depth=0
				if d[depth]<l:
					depth += 1
				elif d[depth]>l:
					depth -= 1
				d[depth]=l
				ln[depth]=line
				parent=ln[depth-1]

				r=[l,line,parent,res.group(2)]
				st=res.group(2)
				
				res=re.search("(\S+):\s*\*(\S+)",st)
				if res:
					r=[l,line,parent,'link',res.group(1),res.group(2),refs[res.group(2)]]
	#				print refs[res.group(2)]
					continue

				res=re.search("(\S+):\s*&(\S+)\s+(\S.*)",st)
				if res:
					r=[l,line,parent,"anchor attr",res.group(1),res.group(2),res.group(3)]
					refs[res.group(2)]=line
					continue

				res=re.search("(\S+):\s*&(\S+)",st)
				if res:
					r=[l,line,parent,"anchor",res.group(1),res.group(2)]
					refs[res.group(2)]=line
					continue

				res=re.search("(\S+[^:]):\s*([^:]\S.*)",st)
				if res:
					print app
					r=[l,line,parent,"att val",res.group(1),eval(res.group(2))]
					if res.group(1) =='Name':
						print "setze Namen von parent"
						print parent
						print rs[parent]
						rs[parent].append(res.group(2))
						print rs[parent]
					continue

				res=re.search("\s*(\S):\s*([^:]\S.*)",st)
				if res:
					print app
					r=[l,line,parent,"att val",res.group(1),eval(res.group(2))]
					if res.group(1) =='Name':
						print "setze Namen von parent"
						print parent
						print rs[parent]
						rs[parent].append(res.group(2))
						print rs[parent]
					continue
				else:
					print "tttt"
					print st
					res=re.search("(\S+):",st)
					if res:    
						r=[l,line,parent,"obj", res.group(1),'no anchor']
		print
		print "lines parsed ..."
		for r in rs:
				print r

		print 
		print "Anchors ...."
		self.anchors=refs
		print self.anchors
		self.lines=rs
		print
		print



	def build(self):
		for l in self.lines:

			if l[3]=='cmd':
				try: 
					exec(l[4])
				except:
					sayexc(str(["Error exec:",l[4]]))
				continue
			if l[3]=='obj' or  l[3]=='anchor' or  l[3]=='local class':
					name=l[4]
					print name
					try: 
						print "class check ..."
						print self.classes
						self.classes[name]
						f=name+"()"
						f2=name
					except:
						f=creatorFunction(l[4])

					if len(l)<7: # no name for object
						l.append('')
					print "**", f



					if l[3]=='local class':
						exec("class "+name+"(object):pass")
						h=eval(f2)
					else:
						h=eval(f)
					print h
					if len(l)<7:
						l.append(None)
					l.append(h)
					self.objects.append(h)
			if  l[2] <> 0:
				if l[4]=='Name': continue
				if l[3]=='obj' or  l[3]=='anchor':
					parent=self.lines[l[2]][7]
					print parent
					print l
					print l[7]
					self.addChild(parent,l[7])
					print l
				if l[3]=='link':
					parent=self.lines[l[2]][7]
					try:
						child=self.lines[l[6]][7]
						self.addChild(parent,child)
					except:
						# link eines attribs
				#----------------------------------
						method=l[4]
						v=self.lines[l[6]][6]
						print "check atts"
						kk=eval("parent."+l[4])
						cnkk=kk.__class__.__name__
						print ["vor function ", cnkk]
						
						if cnkk.startswith('So'):
							print "So ..."
							print v
							print v.__class__
							ex="parent."+method+".setValue(" +str(v) + ")"
							exec(ex)
							continue
						if cnkk =='builtin_function_or_method':
							# qt 2...
							print "mche was"
							print v
							print "parent."+l[4]
							kk(v)
							print "okay"
							continue
						cn=v.__class__.__name__
						print [v,cn]
						if cn=='int' or  cn=='float':
							ex="parent."+l[4]+"="+str(v)
						elif cn=='str':
							ex="parent."+l[4]+"='"+v+"'"
						else:
							print "nicht implementierter typ"
							ex=''
						print "!!! *!!** "+ex
						exec(ex)
						print parent
						
				#-----------------------------------
			if l[3]=='att val' or  l[3]=='anchor attr':
#					print l
#					print self.lines[l[2]]
					

					method=l[4]
					parent=self.lines[l[2]][7]

					if l[3]=='att val':
						v=l[5]
					else:
						print "anchor val"
						v=l[6]
					if method=='id':
						self.ids[v]=parent
						continue
					try:
						kk=eval("parent."+l[4])
					except:
						
						cn=v.__class__.__name__
						print [v,cn]
						if cn=='int' or  cn=='float':
							ex="parent."+l[4]+"="+str(v)
						elif cn=='str':
							ex="parent."+l[4]+"='"+v+"'"
						else:
							print "nicht implementierter typ"
							ex=''
#						ex="parent."+l[4]+"="+str(v)
						print "*** "+ex
						exec(ex)
						continue


					kk=eval("parent."+l[4])
					cnkk=kk.__class__.__name__
					print "vor function ", cnkk
					if cnkk.startswith('So'):
						print "So ..."
						print v
						print v.__class__
						ex="parent."+method+".setValue(" +str(v) + ")"
						exec(ex)
						continue
					
					if cnkk =='builtin_function_or_method':
							# qt 3...
							print "mche was"
							print v
							print "parent."+l[4]
							kk(v)
							print "okay"
							continue

					cn=v.__class__.__name__
					print [v,cn]
					if cn=='int' or  cn=='float':
						ex="parent."+l[4]+"="+str(v)
					elif cn=='str':
						ex="parent."+l[4]+"='"+v+"'"
					else:
						print "nicht implementierter typ"
						ex=''
					print "//*** "+ex
					exec(ex)
					print parent


	def showSo(self):
		for l in self.lines:
			if  l[2] == 0 and l[0] <>-1:
#					print l
					if len(l)<7:
						continue
					r=l[7]
#					print r
					if r.__class__.__name__.startswith('So'):
						print r
						sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
						sg.addChild(r)



	def showSo2(self,dokname):
		for l in self.lines:
			if  l[2] == 0 and l[0] <>-1:
#					print l
					r=l[7]
#					print r
					if r.__class__.__name__.startswith('So'):
						print r
						dok = FreeCADGui.getDocument(dokname)
						sg=dok.ActiveView.getSceneGraph()
						sg.addChild(r)



	def addChild(self,p,c):
		cc=c.__class__.__name__
		print p
		print p.__class__
		print 
		print c
		print c.__class__
		print cc
		

		if str(c.__class__).startswith("<type 'PySide.QtGui."):
			print "pyside"
			print p
			dir(p)
			print p.layout
			p.layout.addWidget(c)
			return
		
		if cc.startswith('So'):
			p.addChild(c)
			return

		if p.__class__.__name__=='object' or str(p.__class__).startswith("<class 'geodat.miki."):
			print "Add children to object"
			try:
				p.children.append(c)
			except:
				p.children=[c]
			return

		if str(p.TypeId)=='Part::MultiFuse':
			z=p.Shapes
			z.append(c)
			p.Shapes=z
		elif str(p.TypeId)=='Part::Compound':
			z=p.Links
			z.append(c)
			p.Links=z
		else:
			try: 
				p.addObject(c)
			except: 
				FreeCAD.Console.PrintError("\naddObject funktioniert nicht")
				FreeCAD.Console.PrintError([p,c])


	def run(self,string):
		print "parse2 ...."
		self.parse2(string)
		print "build ..."
		self.build()
		print "showSo ..."
		self.showSo()
		print "done"


	def roots(self):
		rl=[]
		for l in self.lines:
			if l[0]==0:
				rl.append(l)
		return rl

	def report(results=[]):
		print "Results ..."
		for r in results:
			print r
			if r.__class__.__name__.startswith('So'):
				sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
				sg.addChild(r)

		print "Data ..."
		for ob in self.objects:
			print ob

		print self.anchors

		for r in self.roots():
			print r




