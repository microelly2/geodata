from say import *

import geodat
import re
from geodat.say import say

class node():

	def __init__(self,typ):
#		print("erzuegen node,type ",typ)
		self.typ=typ
		self.params={}
		self.content=[]

	def getParam(self,param):
		return self.params[param]

	def getNodes(self,typ):
		ns=[]
		for c in self.content:
			if c.typ==typ:
				ns += [c]
		return ns
	
	def addContent(self,c):
		self.content += [c]

	def __str__(self):
		return self.typ


	def getiterator(self,typ):
		rc=[]
		for obj in self.content:
			if obj.typ==typ:
				rc += [obj]
			rc += obj.getiterator(typ)
		return rc


def parseParams(string):
	params={}
	s=string
	while s!="":
		res = re.search(r"(\S+)=\"([^\"]*)\"\s+(\S.*)", s)
		if res != None:
			assert len(res.groups())==3
			k,v,s=res.group(1),res.group(2),res.group(3)
			params[k]=v
			continue

		res = re.search(r"(\S+)=\"(.*)\"", s)
		if res != None:
			assert len(res.groups())==2
			k,v,s=res.group(1),res.group(2),""
			params[k]=v
			continue

		else:
			raise Exception("parse Params Fehler:"+ s)
			s=""
	return params

def getData(fn):
	stack=[0,0]*4
	stackpointer=-1

	objs=[]

	say("Read data from cache file ...")
	say(fn)
	f=open(fn,"r")
	content=f.readlines()
	# say(content)
	for line in content:
	#	print(line)

		if re.search(r"^\s*$",line):
			continue

		# ein satz
		res = re.search(r"^\s*<(\S+)\s+([^<]*)/>\s*$", line)
		if res != None:
	#		print "complete! ",res.groups()
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			print stack[stackpointer]
	#			for c in stack[stackpointer].content:
	#				print c,",",
	#			print 
			continue

		res = re.search(r"^\s*<(\S+)\s+([^<]*)>\s*$", line)
		if res != None:
	#		print "!start! ",res.groups()
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			for c in stack[stackpointer].content:
	#				print c,
			stackpointer += 1
			stack[stackpointer]=obj
			continue


		res = re.search(r"^\s*</([^<]*)>\s*$", line)
		if res != None:
	#		print "!ende! ",res.groups()
			assert len(res.groups())==1
			stackpointer -= 1
			continue

		res = re.search(r"^\s*<([^<\s]*)>\s*$", line)
		if res != None:
	#		print "!simple start! ",res.groups()
			assert len(res.groups())==1
			typ=res.group(1)
			obj=node(typ)

			continue


		#auf und zu
		res = re.search(r"^\s*<(\S+)\s+([^<]*)>(.*)</([^<]+)>\s*$", line)
		if res != None:
	#		print "!alles! ",res.groups()
			assert len(res.groups())==4
			continue


		raise Exception("unerwartet :" +line +":")
	#	x = re.findall('<([^<]*)>', line)
	#	for xl in x: 
	#		print(xl)

	return stack[0]



