# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- osm map importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

# http://api.openstreetmap.org/api/0.6/map?bbox=11.74182,50.16413,11.74586,50.16561
#http://api.openstreetmap.org/api/0.6/way/384013089
#http://api.openstreetmap.org/api/0.6/node/3873106739


'''
xmltodict parser to dict by Martin Blech
https://github.com/martinblech/xmltodict

Copyright (C) 2012 Martin Blech and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

TransverseMercator by Vladimir Elistratov 
https://github.com/vvoovv/blender-geo/wiki/Import-OpenStreetMap-(.osm)

'''

import FreeCAD,FreeCADGui

import json

from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

try:
    from cStringIO import StringIO
except ImportError:  # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

try:
    from collections import OrderedDict
except ImportError:  # pragma no cover
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = dict

try: 
    _basestring = basestring
except NameError:  # pragma no cover
    _basestring = str

try: 
    _unicode = unicode
except NameError:  # pragma no cover
    _unicode = str

__author__ = 'Martin Blech'
__version__ = '0.9.2'
__license__ = 'MIT'


class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler(object):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True,
                 namespace_separator=':',
                 namespaces=None,
                 force_list=()):
        self.path = []
        self.stack = []
        self.data = []
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.force_list = force_list

    def _build_name(self, full_name):
        if not self.namespaces:
            return full_name
        i = full_name.rfind(self.namespace_separator)
        if i == -1:
            return full_name
        namespace, name = full_name[:i], full_name[i+1:]
        short_namespace = self.namespaces.get(namespace, namespace)
        if not short_namespace:
            return name
        else:
            return self.namespace_separator.join((short_namespace, name))

    def _attrs_to_dict(self, attrs):
        if isinstance(attrs, dict):
            return attrs
        return self.dict_constructor(zip(attrs[0::2], attrs[1::2]))

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        attrs = self._attrs_to_dict(attrs)
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(
                    (self.attr_prefix+self._build_name(key), value)
                    for (key, value) in attrs.items())
            else:
                attrs = None
            self.item = attrs or None
            self.data = []

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = (None if not self.data
                        else self.cdata_separator.join(self.data))

            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            data = (None if not self.data
                    else self.cdata_separator.join(self.data))
            item = self.item
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = None
            self.data = []
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = [data]
        else:
            self.data.append(data)

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            if key in self.force_list:
                item[key] = [data]
            else:
                item[key] = data
        return item


def parse(xml_input, encoding=None, expat=expat, process_namespaces=False,
          namespace_separator=':', **kwargs):
    """Parse the given XML input and convert it into a dictionary.

    `xml_input` can either be a `string` or a file-like object.

    If `xml_attribs` is `True`, element attributes are put in the dictionary
    among regular child elements, using `@` as a prefix to avoid collisions. If
    set to `False`, they are just ignored.

    Simple example::

        >>> import xmltodict
        >>> doc = xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>
        ... \"\"\")
        >>> doc['a']['@prop']
        u'x'
        >>> doc['a']['b']
        [u'1', u'2']

    If `item_depth` is `0`, the function returns a dictionary for the root
    element (default behavior). Otherwise, it calls `item_callback` every time
    an item at the specified depth is found and returns `None` in the end
    (streaming mode).

    The callback function receives two parameters: the `path` from the document
    root to the item (name-attribs pairs), and the `item` (dict). If the
    callback's return value is false-ish, parsing will be stopped with the
    :class:`ParsingInterrupted` exception.

    Streaming example::

        >>> def handle(path, item):
        ...     print 'path:%s item:%s' % (path, item)
        ...     return True
        ...
        >>> xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>\"\"\", item_depth=2, item_callback=handle)
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2

    The optional argument `postprocessor` is a function that takes `path`,
    `key` and `value` as positional arguments and returns a new `(key, value)`
    pair where both `key` and `value` may have changed. Usage example::

        >>> def postprocessor(path, key, value):
        ...     try:
        ...         return key + ':int', int(value)
        ...     except (ValueError, TypeError):
        ...         return key, value
        >>> xmltodict.parse('<a><b>1</b><b>2</b><b>x</b></a>',
        ...                 postprocessor=postprocessor)
        OrderedDict([(u'a', OrderedDict([(u'b:int', [1, 2]), (u'b', u'x')]))])

    You can pass an alternate version of `expat` (such as `defusedexpat`) by
    using the `expat` parameter. E.g:

        >>> import defusedexpat
        >>> xmltodict.parse('<a>hello</a>', expat=defusedexpat.pyexpat)
        OrderedDict([(u'a', u'hello')])

    You can use the force_list argument to force lists to be created even
    when there is only a single child of a given level of hierarchy. The
    force_list argument is a tuple of keys. If the key for a given level
    of hierarchy is in the force_list argument, that level of hierarchy
    will have a list as a child (even if there is only one sub-element).
    The index_keys operation takes precendence over this. This is applied
    after any user-supplied postprocessor has already run.

        For example, given this input:
        <servers>
          <server>
            <name>host1</name>
            <os>Linux</os>
            <interfaces>
              <interface>
                <name>em0</name>
                <ip_address>10.0.0.1</ip_address>
              </interface>
            </interfaces>
          </server>
        </servers>

        If called with force_list=('interface',), it will produce
        this dictionary:
        {'servers':
          {'server':
            {'name': 'host1',
             'os': 'Linux'},
             'interfaces':
              {'interface':
                [ {'name': 'em0', 'ip_address': '10.0.0.1' } ] } } }
    """
    handler = _DictSAXHandler(namespace_separator=namespace_separator,
                              **kwargs)
    if isinstance(xml_input, _unicode):
        if not encoding:
            encoding = 'utf-8'
        xml_input = xml_input.encode(encoding)
 
    if not process_namespaces:
        namespace_separator = None
    parser = expat.ParserCreate(
        encoding,
        namespace_separator
    )
    try:
        parser.ordered_attributes = True
    except AttributeError:
        # Jython's expat does not support ordered_attributes
        pass
    
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    
    try:
        parser.ParseFile(xml_input)
    except (TypeError, AttributeError):
        parser.Parse(xml_input, True)
    
    return handler.item


def _emit(key, value, content_handler,
          attr_prefix='@',
          cdata_key='#text',
          depth=0,
          preprocessor=None,
          pretty=False,
          newl='\n',
          indent='\t',
          full_document=True):
    if preprocessor is not None:
        result = preprocessor(key, value)
        if result is None:
            return
        key, value = result
    if (not hasattr(value, '__iter__')
            or isinstance(value, _basestring)
            or isinstance(value, dict)):
        value = [value]
    for index, v in enumerate(value):
        if full_document and depth == 0 and index > 0:
            raise ValueError('document with multiple roots')
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        attrs = OrderedDict()
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))
        if pretty:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.startElement(key, AttributesImpl(attrs))
        if pretty and children:
            content_handler.ignorableWhitespace(newl)
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler,
                  attr_prefix, cdata_key, depth+1, preprocessor,
                  pretty, newl, indent)
        if cdata is not None:
            content_handler.characters(cdata)
        if pretty and children:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.endElement(key)
        if pretty and depth:
            content_handler.ignorableWhitespace(newl)


def unparse(input_dict, output=None, encoding='utf-8', full_document=True,
            **kwargs):
    """Emit an XML document for the given `input_dict` (reverse of `parse`).

    The resulting XML document is returned as a string, but if `output` (a
    file-like object) is specified, it is written there instead.

    Dictionary keys prefixed with `attr_prefix` (default=`'@'`) are interpreted
    as XML node attributes, whereas keys equal to `cdata_key`
    (default=`'#text'`) are treated as character data.

    The `pretty` parameter (default=`False`) enables pretty-printing. In this
    mode, lines are terminated with `'\n'` and indented with `'\t'`, but this
    can be customized with the `newl` and `indent` parameters.

    """
    if full_document and len(input_dict) != 1:
        raise ValueError('Document must have exactly one root.')
    must_return = False
    if output is None:
        output = StringIO()
        must_return = True
    content_handler = XMLGenerator(output, encoding)
    if full_document:
        content_handler.startDocument()
    for key, value in input_dict.items():
        _emit(key, value, content_handler, full_document=full_document,
              **kwargs)
    if full_document:
        content_handler.endDocument()
    if must_return:
        value = output.getvalue()
        try:  # pragma no cover
            value = value.decode(encoding)
        except AttributeError:  # pragma no cover
            pass
        return value





''' 
    TransverseMercator:
    "author": "Vladimir Elistratov <vladimir.elistratov@gmail.com> and gtoonstra",
    "wiki_url": "https://github.com/vvoovv/blender-geo/wiki/Import-OpenStreetMap-(.osm)",
    "tracker_url": "https://github.com/vvoovv/blender-geo/issues",
'''

import os
import math

# see conversion formulas at
# http://en.wikipedia.org/wiki/Transverse_Mercator_projection
# and
# http://mathworld.wolfram.com/MercatorProjection.html
class TransverseMercator:
    radius = 6378137
    radius = 6378137000
    
    def __init__(self, **kwargs):
        # setting default values
        self.lat = 0 # in degrees
        self.lon = 0 # in degrees
        self.k = 1 # scale factor
        
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
        self.latInRadians = math.radians(self.lat)

    def fromGeographic(self, lat, lon):
        lat = math.radians(lat)
        lon = math.radians(lon-self.lon)
        B = math.sin(lon) * math.cos(lat)
        x = 0.5 * self.k * self.radius * math.log((1+B)/(1-B))
        y = self.k * self.radius * ( math.atan(math.tan(lat)/math.cos(lon)) - self.latInRadians )
        return (x,y)

    def toGeographic(self, x, y):
        x = x/(self.k * self.radius)
        y = y/(self.k * self.radius)
        D = y + self.latInRadians
        lon = math.atan(math.sinh(x)/math.cos(D))
        lat = math.asin(math.sin(D)/math.cosh(x))

        lon = self.lon + math.degrees(lon)
        lat = math.degrees(lat)
        return (lat, lon)



#------------------------------
#
# microelly 2016 ..
#
#------------------------------


def import_osm(b,l,bk,progressbar,status):


	dialog=False
	debug=False


	#--------------------
	import FreeCAD,Part
	from PySide import QtGui
	App=FreeCAD
	Gui=FreeCADGui
	#---------------------


	#download data from 
	# http://www.openstreetmap.org/export#map=19/50.16487/11.74431


	# fname, _ = QtGui.QFileDialog.getOpenFileName(None, 'Open file','/home/thomas/Dokumente/freecad_buch/b180_osm/map.osm')



	import urllib2

	if progressbar:
			progressbar.setValue(0)

	if status:
		status.setText("get data from openstreetmap.org ...")
		FreeCADGui.updateGui()
	content=''
	if True:
			#source='http://api.openstreetmap.org/api/0.6/map?bbox=11.74,50.16,11.75,50.17'
			#source='http://api.openstreetmap.org/api/0.6/map?bbox=11.74,50.16,11.742,50.162'
			
			
			#---------------------------------
#			bk=1 # size in km
#			bk=1.3
#			bk=0.22
			bk=0.5*bk

			lk=bk # 
			# scharfe lanke / weinmeisterhornweg 
#			b=52.5073
#			l=13.1881
			#----------------------------------


			b1=b-bk/1113*10
			l1=l-lk/713*10


			b2=b+bk/1113*10
			l2=l+lk/713*10

			
			source='http://api.openstreetmap.org/api/0.6/map?bbox='+str(l1)+','+str(b1)+','+str(l2)+','+str(b2)
			
			try:
				fname="/tmp/osm.dat"
				response = urllib2.urlopen(source)
				first=True
				content=''
	#			f=open(fname,"w")
				for line in response:
					print line
	#				f.write(line)
					if first:
						first=False
					else:
						content += line
	#			f.close()
			except:
				print "andere aktion v  kann nicht lesen"

	'''
	if False: #read from file
		first=True
		content=''
		for line in open(fname,'r'):
			if first:
				first=False
			else:
				content += line
	'''


	print "---------------------"
	print content
	print "--------------------"

	if status:
		status.setText("parse data ...")
		FreeCADGui.updateGui()

	sd=parse(content)
	if debug: print(json.dumps(sd, indent=4))

	if status:
		status.setText("transform data ...")
		FreeCADGui.updateGui()



	bounds=sd['osm']['bounds']
	nodes=sd['osm']['node']
	ways=sd['osm']['way']
	relations=sd['osm']['relation']


	# center of the scene
	bounds=sd['osm']['bounds']
	minlat=float(bounds['@minlat'])
	minlon=float(bounds['@minlon'])
	maxlat=float(bounds['@maxlat'])
	maxlon=float(bounds['@maxlon'])

	tm=TransverseMercator()
	tm.lat=0.5*(minlat+maxlat)
	tm.lon=0.5*(minlon+maxlon)
	# tm.size=1000

	center=tm.fromGeographic(tm.lat,tm.lon)
	corner=tm.fromGeographic(minlat,minlon)
	size=[center[0]-corner[0],center[1]-corner[1]]

	print center
	print corner
	print size
	print "-------------------"




	# map all points to xy-plane
	points={}
	for n in nodes:
		ll=tm.fromGeographic(float(n['@lat']),float(n['@lon']))
		points[str(n['@id'])]=FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],0.0)
		print  points[str(n['@id'])]



	# hack to catch deutsche umlaute
	def beaustring(string):
		res=''
		for tk in zz:
			try:
				res += str(tk)
			except:
				print ["error sign",tk,ord(tk)]
				if ord(tk)==223:
					res += 'ß'
				else:
					res +="#"
		return res


	if status:
		status.setText("create visualizations  ...")
		FreeCADGui.updateGui()

	App.newDocument("OSM Map")
	area=App.ActiveDocument.addObject("Part::Plane","area")
	area.Length=size[0]*2
	area.Width=size[1]*2
	area.Placement=FreeCAD.Placement(FreeCAD.Vector(-size[0],-size[1],0.00),FreeCAD.Rotation(0.00,0.00,0.00,1.00))

	wn=-1
	coways=len(ways)
	import time
	starttime=time.time()
	refresh=1000
	for w in ways:
		building=False
		landuse=False
		highway=False
		wn += 1

		#if wn not in [-2,-3]:
		if False:
			continue
		
		nowtime=time.time()
		print
		if wn<>0: print "way -------- # " + str(wn) + "/" + str(coways) + " time per house : " +  str(round((nowtime-starttime)/wn,4))
		if progressbar:
			progressbar.setValue(int(0+100.0*wn/coways))
		
		if debug: print "w=", w
		if debug: print "tags ..."
		st=""
		nr=""
		try:
			w['tag']
		except:
			print "no tags found."
			continue

		for t in w['tag']:
			if t.__class__.__name__ == 'OrderedDict':
				try:
					#list of tags
					if debug: print t
					print t['@k'],' = ', t['@v']
					if str(t['@k'])=='highway':
						highway=True
						st=t['@k']
					if str(t['@k'])=='name':
						zz=t['@v']
						nr=beaustring("!"+zz)
					if str(t['@k'])=='ref':
						zz=t['@v']
						nr=beaustring(zz)+" /"
					if str(t['@k'])=='building':
						building=True
						st='building'
					if str(t['@k'])=='addr:housenumber':
						nr=str(t['@v'])
					if str(t['@k'])=='addr:street':
						zz=w['tag'][1]['@v']
						st=beaustring(zz)
					if str(t['@k'])=='landuse':
						landuse=True
				except:
					print "unexpected error ################################################################"
			else:
				# single tag only 
				if debug: print [w['tag']['@k'],w['tag']['@v']]
				if str(w['tag']['@k'])=='building':
					building=True
					st='building'
				if str(w['tag']['@k'])=='landuse':
					landuse=True
					st=w['tag']['@k']
					nr=w['tag']['@v']
				if str(w['tag']['@k'])=='highway':
					st=w['tag']['@k']
					nr=w['tag']['@v']
					highway=True
			name=str(st) + " " + str(nr)
			if debug: print "name ",name

		#generate pointlist of the way
		polis=[]
		for n in w['nd']:
			polis.append(points[str(n['@ref'])])

		#create 2D map
		pp=Part.makePolygon(polis)
		Part.show(pp)
		z=App.ActiveDocument.ActiveObject
		if name:
			z.Label=name+' outline'
		else:
			z.Label='way '

		if name==' ':
			g=App.ActiveDocument.addObject("Part::Extrusion",name)
			g.Base = z
			g.ViewObject.ShapeColor = (1.00,1.00,0.00)
			g.Dir = (0,0,10)
			g.Solid=True
			g.Label='way ex '

		if building:
			g=App.ActiveDocument.addObject("Part::Extrusion",name)
			g.Base = z
			g.ViewObject.ShapeColor = (1.00,0.00,0.00)
			g.Dir = (0,0,1)
			g.Solid=True
			g.Label=name

		if landuse:
			g=App.ActiveDocument.addObject("Part::Extrusion",name)
			g.Base = z
			if nr == 'residential':
				g.ViewObject.ShapeColor = (1.00,.60,.60)
			elif nr == 'meadow':
				g.ViewObject.ShapeColor = (0.00,1.00,0.00)
			elif nr == 'farmland':
				g.ViewObject.ShapeColor = (.80,.80,.00)
			elif nr == 'forest':
				g.ViewObject.ShapeColor = (1.0,.40,.40)
			g.Dir = (0,0,0.1)
			g.Label=name
			g.Solid=True

		if highway:
			g=App.ActiveDocument.addObject("Part::Extrusion","highway")
			g.Base = z
			g.ViewObject.LineColor = (0.00,.00,1.00)
			g.ViewObject.LineWidth = 10
			g.Dir = (0,0,0.2)
			g.Label=name
		refresh += 1
		if refresh >100:
			FreeCADGui.updateGui()
			FreeCADGui.SendMsgToActiveView("ViewFit")
			refresh=0


	FreeCAD.activeDocument().recompute()
	FreeCADGui.updateGui()

	FreeCADGui.SendMsgToActiveView("ViewFit")

	FreeCAD.activeDocument().recompute()


	print "relations ..."
	for r  in relations:
		print r


	print progressbar

	if status:
		status.setText("import finished.")
	if progressbar:
			progressbar.setValue(100)



# import_osm()
