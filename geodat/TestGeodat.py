# Unit test for the Nurbs module


import FreeCAD, os, unittest, FreeCADGui, Draft

class NurbsTest(unittest.TestCase):

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != "DraftTest":
                FreeCAD.newDocument("DraftTest")
        else:
            FreeCAD.newDocument("DraftTest")
        FreeCAD.setActiveDocument("DraftTest")

    def testPivy(self):
        FreeCAD.Console.PrintLog ('Checking Pivy...\n')
        from pivy import coin
        c = coin.SoCube()
        FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(c)
        self.failUnless(c,"Pivy is not working properly")



    def tearDown(self):
        FreeCAD.closeDocument("DraftTest")
        pass



