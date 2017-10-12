
from __future__ import print_function
import ROOT
from array import array
import sys
import math
import os

from ROOT import TCanvas, TGraph, TGraphAsymmErrors, TLegend, TF1
from ROOT import gROOT, gStyle
###############################################################################
###############################################################################
def getSubdetectorGeometry(inXmlFile,detName):
	points = []
	configurations = []
	import xml.etree.ElementTree as ET
	tree = ET.parse(inXmlFile)
	root = tree.getroot()
	if root.findall(detName) is None:
		print ("[WARNING]\tNo detector with name <%s> is found in xml-file" % (detName))
		print ("[WARNING]\tRETURN EMPTY ARRAY")
		return []

	y1 = []
	y2 = []
	x1 = []
	x2 = []

	if len(root.findall(detName)) == 0:
		print ("[ERROR]\tNo detector with name <%s> is found in xml-file <%s>" % (detName, inXmlFile))

	for iDir in root.findall(detName):
         	if iDir.find('nElements') is None:
			print ("[WARNING]\tNo <nElements> variable in detector <%s> is found in xml-file" % (detName))
			print ("[WARNING]\tRETURN EMPTY ARRAY")
			return []
		else:
			nElements = int(iDir.find('nElements').text)
		if (iDir.find('innerRadius') is not None) and (iDir.find('outerRadius') is not None):
			y1 = [float(i) for i in iDir.find('innerRadius').text.split(",")]
			y2 = [float(i) for i in iDir.find('outerRadius').text.split(",")]
			if (len(y1) != len (y2)):
				print ("[ERROR]\tnumber of elements for inner and outer radius for detector <%s> does not match!!!" % (detName))
			elif (len(y1)!=nElements) and (len(y1)!=1):
				print ("[ERROR]\twrong number of elements for inner and outer radius for detector <%s> does not match!!!" % (detName))
			if (len(y1)==1):
				y1 = y1 * nElements
				y2 = y2 * nElements
		elif (iDir.find('radius') is not None) and (iDir.find('rWidth') is not None):
			y = [float(i) for i in iDir.find('radius').text.split(",")]
			rW = [float(i) for i in iDir.find('rWidth').text.split(",")]
			if (len(y)!=nElements) and (len(y)!=1):
				print ("[ERROR]\t<radius>")
			if (len(rW)!=nElements) and (len(rW)!=1):
				print ("[ERROR]\t<rWidth>")
			if (len(y)==1):
				y = y * nElements
			if (len(rW)==1):
				rW = rW * nElements
			for i in range(0,nElements):
				y1.append( y[i]-rW[i]/2.0 )
				y2.append( y[i]+rW[i]/2.0 )
		else:
			print ("[WARNING]\tmissing <innerRadius>/<outerRadius> or <radius>/<rWidth> variable(s) in detector <%s>" % (detName))
			print ("[WARNING]\tRETURN EMPTY ARRAY")
			return []

		if (iDir.find('length') is not None):
			x1 = [-float(i)/2.0 for i in iDir.find('length').text.split(",")]
			x2 = [float(i)/2.0 for i in iDir.find('length').text.split(",")]
			if (len(x1)==1):
				x1 = x1 * nElements
				x2 = x2 * nElements
		elif (iDir.find('halfLength') is not None):
			x1 = [-float(i) for i in iDir.find('halfLength').text.split(",")]
			x2 = [float(i) for i in iDir.find('halfLength').text.split(",")]
			if (len(x1)==1):
				x1 = x1 * nElements
				x2 = x2 * nElements
		elif (iDir.find('zLow') is not None) and (iDir.find('zHigh') is not None):
			x1 = [float(i) for i in iDir.find('zLow').text.split(",")]
			x2 = [float(i) for i in iDir.find('zHigh').text.split(",")]
			if (len(x1) != len (x2)):
				print ("[ERROR]\tnumber of elements for <zLow> and <zHigh> for detector <%s> does not match!!!" % (detName))
			elif (len(x1)!=nElements) and (len(x1)!=1):
				print ("[ERROR]\twrong number of elements for <zLow> and <zHigh> for detector <%s> does not match!!!" % (detName))
			if (len(x1)==1):
				x1 = x1 * nElements
				x2 = x2 * nElements
		elif (iDir.find('z') is not None) and (iDir.find('zWidth') is not None):
			x = [float(i) for i in iDir.find('z').text.split(",")]
			xW = [float(i) for i in iDir.find('zWidth').text.split(",")]
			if (len(x)!=nElements) and (len(x)!=1):
				print ("[ERROR]\t<z>")
			if (len(xW)!=nElements) and (len(xW)!=1):
				print ("[ERROR]\t<zWidth>")
			if (len(x)==1):
				x = x * nElements
			if (len(xW)==1):
				xW = xW * nElements
			for i in range(0,nElements):
				x1.append( x[i]-xW[i]/2.0 )
				x2.append( x[i]+xW[i]/2.0 )
		else:
			print ("[WARNING]\tmissing {z,zWidth}/{zLow,zHigh}/{lenght}/{halfLength} variable(s) in detector <%s>" % (detName))
			print ("[WARNING]\tRETURN EMPTY ARRAY")
			return []

		for i in range(0,nElements):
			points.append( [(x2[i]+x1[i])/2.0, (y2[i]+y1[i])/2.0, (x2[i]-x1[i])/2.0, (x2[i]-x1[i])/2.0,(y2[i]-y1[i])/2.0, (y2[i]-y1[i])/2.0 ])

		if ("endcap" in detName) or ("Endcap" in detName):
			for i in range(0,nElements):
				iPoint = points[i]
				points.append([-iPoint[0],iPoint[1],iPoint[2],iPoint[3],iPoint[4],iPoint[5]])
         	if iDir.find('fillStyle') is not None:
			configurations.append(int(iDir.find('fillStyle').text))

	#  print (y1)
	#  print (y2)
	#  print (x1)
	#  print (x2)
	#  print ("%s:" % (detName))
	#  print (points)
	return [points, configurations]
###############################################################################
###############################################################################
def getGraph(inArr):
	points = inArr[0]
	gr = TGraphAsymmErrors(
		len(points),
		array("d", [ x[0] for x in points ]),
		array("d", [ x[1] for x in points ]),
		array("d", [ x[2] for x in points ]),
		array("d", [ x[3] for x in points ]),
		array("d", [ x[4] for x in points ]),
		array("d", [ x[5] for x in points ]))
	configurations = inArr[1]
	if len(configurations)!=0:
		gr.SetFillStyle(configurations[0])
	return gr

###############################################################################
###############################################################################

def getDetector(inXmlFile, subDetectorsToDraw):
	graphs = []
	
	for iSubDet in subDetectorsToDraw:
		tmpArr = getSubdetectorGeometry(inXmlFile,iSubDet)
		graphs.append(getGraph(tmpArr))

	return graphs
###############################################################################
###############################################################################

def main(argv):

	tracker = ["VXD_barrel", "VXD_endcaps", "IT_barrel", "IT_endcaps", "OT_barrel", "OT_endcaps"]
	calorimeter = ["ECAL_barrel", "ECAL_endcaps", "HCAL_barrel", "HCAL_endcaps_part1", "HCAL_endcaps_part2"]
	afterCalo = ["Vactank", "Coil", "Yoke_barrel", "Yoke_endcaps"]

	FCCee_tracker = getDetector("xmlFiles/FCCeeTracker_increasedWidth_v2.xml",tracker)
	CLIC_tracker = getDetector("xmlFiles/CLICTracker_increasedWidth_v2.xml",tracker)
	#  FCCee_tracker = getDetector("xmlFiles/FCCeeTracker.xml",tracker)
	#  CLIC_tracker = getDetector("xmlFiles/CLICTracker.xml",tracker)
	CLIC_calorimeter = getDetector("xmlFiles/CLICCalorimeter.xml",calorimeter)
	FCCee_calorimeter = getDetector("xmlFiles/FCCeeCalorimeter.xml",calorimeter)
	CLIC_afterCalo = getDetector("xmlFiles/CLIC_afterCalo.xml",afterCalo)
	FCCee_afterCalo = getDetector("xmlFiles/FCCee_afterCalo.xml",afterCalo)

	c1 = TCanvas( 'c1', 'A Simple Graph Example', 0, 0, 1130, 1130 )
	#  myFrame = c1.DrawFrame(-2250,-50,2250,2200)
	#  myFrame = c1.DrawFrame(-10,-10,2500,2500)
	myFrame = c1.DrawFrame(-10,-10,3620,3620)
	#  myFrame = c1.DrawFrame(-2420,-10,4220,3620)
	myFrame.GetXaxis().SetLabelSize(0.03)
	myFrame.GetXaxis().SetTitle("Z [mm]")
	myFrame.GetYaxis().SetTitle("R [mm]")
	myFrame.GetYaxis().SetTitleOffset(1.5)

	CLIC_detector = []
	FCCee_detector = [FCCee_tracker]

	if "CLIC" in argv:
		CLIC_detector = [CLIC_tracker, CLIC_calorimeter, CLIC_afterCalo]
	if ("FCCee" in argv) or ("FCC" in argv):
		FCCee_detector = [FCCee_tracker, FCCee_calorimeter, FCCee_afterCalo]

	if CLIC_detector != []:
		for iSubDet in CLIC_detector:
			for i in range(0,len(iSubDet)):
				iSubDet[i].SetFillColor(15)
				#  iSubDet[i].SetFillColorAlpha(2, 0.35)
				iSubDet[i].Draw("P2 same")
	if FCCee_detector != []:
		for iSubDet in FCCee_detector:
			for i in range(0,len(iSubDet)):
				iSubDet[i].SetFillColor(2)
				iSubDet[i].Draw("P2 same")
	
	myFile = ROOT.TFile.Open("/afs/cern.ch/work/v/viazlo/analysis/PFAAnalysis/build/PhotonECAL/FCCee_singleParticle_performace/kaon0L/nominalEfficiency/test/particleGun_E50_Theta0_Phi0.root","read")
	ROOT.SetOwnership(myFile,False)
	hist = myFile.Get("PandoraPFOs_22/test_clusterPositionZR");
	gStyle.SetPalette(1);
	hist.Draw("sameCOL");

	if (CLIC_detector==[] and FCCee_detector==[]):
		print ("[WARNING]\tSpecify detector type!")
		print ("[INFO]\t\tSupported models: CLIC, FCCee, FCC")
	else:
		c1.SaveAs("geometryComparison.eps")
		c1.SaveAs("geometryComparison.png")

###############################################################################
###############################################################################
if __name__ == "__main__":
	   main(sys.argv[1:])
