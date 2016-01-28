import time

start=time.time()

bs=0

# height points
hpoints=[]
for k in App.ActiveDocument.Objects:
	if k.Label.startswith("DWire"):
		if bs==3:
			p1=k.Points[0]
			p2=k.Points[1]
		if bs==4:
			p3=k.Points[0]
			p4=k.Points[1]
		bs += 1
		hpoints += k.Points
		

print bs
print len(hpoints)


bs=0
for k in App.ActiveDocument.Objects:
	if k.Label.startswith("building"):
		bs += 1
		k.Placement.Base.z=0
		[x,y,z]=k.Base.Shape.Vertexes[0].Point
		for p in hpoints:
			if int(abs(p.x-x)/1000)<36 and int(abs(p.y-y)/1000)<56:
					print [int(abs(p.x-x)/1000), int(abs(p.y-y)/1000)]
					print (k.Label, int(x),int(y),p)
					if p.z+5000>k.Placement.Base.z:
						k.Placement.Base.z=p.z+1000
					#break

print "buildings ", bs
print (start - time.time())



print p1
print p2
print p3
print p4

print int((p1.y-p2.y)/1000)
print int((p1.x-p3.x)/1000)


print int((p3.y-p4.y)/1000)
print int((p2.x-p4.x)/1000)
