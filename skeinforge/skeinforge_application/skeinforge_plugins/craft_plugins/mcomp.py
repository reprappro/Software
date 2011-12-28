"""
mcomp is a script to compensate for mechanical misalignment.

The mcomp script has been written by Jean-Marc Giacalone.

In order to install the mcomp script within the skeinforge tool chain, put mcomp.py in the skeinforge_application/skeinforge_plugins/craft_plugins/ 
folder. Then edit  skeinforge_application/skeinforge_plugins/profile_plugins/extrusion.py and add the mcomp script to the tool chain sequence by 
inserting 'mcomp' into the tool sequence  in getCraftSequence(). The best place is at the end of the sequence, right before 'export'.

==Operation==
The default 'Activate mcomp' checkbox is off, enable it if using a stepper based extruder.

==Settings==
===some stuff in here===
details here
The following examples mcomp the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and mcomp.py.


> python mcomp.py
This brings up the mcomp dialog.


> python mcomp.py Screw Holder Bottom.stl
The mcomp tool is parsing the file:
Screw Holder Bottom.stl
..
The mcomp tool has created the file:
Screw Holder Bottom_mcomp.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mcomp
>>> mcomp.main()
This brings up the mcomp dialog.


>>> mcomp.writeOutput( 'Screw Holder Bottom.stl' )
Screw Holder Bottom.stl
The mcomp tool is parsing the file:
Screw Holder Bottom.stl
..
The mcomp tool has created the file:
Screw Holder Bottom_mcomp.gcode

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_application.skeinforge_utilities import skeinforge_profile
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import archive
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from fabmetheus_utilities.vector3 import Vector3
import sys
from math import *

__author__ = "Jean-Marc Giacalone (jmgiacalone@hotmail.com)"
__date__ = "$Date: 2011/03/08 $"
__license__ = "GPL 3.0"

X = 0
Y = 1
E = 2

def getCraftedText( fileName, text = '', repository = None ):
	"mcomp the file or text."
	return getCraftedTextFromText( archive.getTextIfEmpty( fileName, text ), repository )

def getCraftedTextFromText( gcodeText, repository = None ):
	"mcomp a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'mcomp' ):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( mcompRepository() )
	if not repository.activatemcomp.value:
		return gcodeText
	return mcompSkein().getCraftedGcode( gcodeText, repository )

def getStringFromCharacterSplitLine( character, splitLine):
	"Get the string after the first occurence of the character in the split line."
	indexOfCharacter = gcodec.getIndexOfStartingWithSecond(character, splitLine)
	if indexOfCharacter < 0:
		return None
	return splitLine[indexOfCharacter][1 :]

def myformat(x, dp = 2):
	if dp == 0:
	    return ('%.0f' % x)
	elif dp == 1:
	    return ('%.1f' % x).rstrip('0').rstrip('.')
	elif dp == 2:
	    return ('%.2f' % x).rstrip('0').rstrip('.')
	elif dp == 3:
	    return ('%.3f' % x).rstrip('0').rstrip('.')
	#endif    

#def getRepositoryConstructor():
#	"Get the repository constructor."
#	return mcompRepository()

def getNewRepository():
	"Get the repository constructor."
	return mcompRepository()

def writeOutput( fileName = ''):
	"mcomp a gcode linear move file."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName == '':
		return
	skeinforge_craft.writeChainTextWithNounMessage( fileName, 'mcomp')

class mcompRepository:
	"A class to handle the mcomp settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.mcomp.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for mcomp', self, '' )
		self.activatemcomp = settings.BooleanSetting().getFromValue( 'Activate mcomp', self, False )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Feedrates -', self )
		#zFeed
		self.xDistance = settings.FloatSpin().getFromValue( 4.0, 'X measurement distance (mm):', self, 34.0, 100 )
		#first layer feed
		self.yError = settings.FloatSpin().getFromValue( 4.0, 'Y error (mm):', self, 34.0, 0.1 )
		#Create the archive, title of the execute button, title of the dialog & settings fileName.
		self.executeTitle = 'mcomp'

	def execute( self ):
		"mcomp button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFilenames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )

class mcompSkein:
	"A class to mcomp a skein of extrusions."
	def __init__( self ):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.lineIndex = 0
		self.lines = None
		self.oldLocation = None
		self.erry = 0

	def getCraftedGcode( self, gcodeText, repository ):
		"Parse gcode text and store the mcomp gcode."
		self.repository = repository
		self.lines = archive.getTextLines( gcodeText )
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			#print line
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def parseInitialization(self):
		'Parse gcode initialization and store the parameters.'
		for self.lineIndex in xrange(len(self.lines)):
			line = self.lines[self.lineIndex]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine(firstWord, splitLine)
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureName> mcomp </procedureName>)')
				return
			self.errY = self.repository.yError.value / self.repository.xDistance.value
			self.distanceFeedRate.addLine(line)
	
	def parseLine( self, line ):
		"Parse a gcode line and add it to the stretch skein."
		#print line
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		if location != self.oldLocation:
			self.oldLocation = location
			#calc new y based on X pos and y error
			newY = myformat(location.y - ( location.x * self.errY ))
			self.distanceFeedRate.addLine(gcodec.getLineWithValueString('Y', line, splitLine, str(newY)))
		else:
			self.distanceFeedRate.addLine(line)
		#endif
		
def main():
	"Display the mcomp dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getRepositoryConstructor() )

if __name__ == "__main__":
	main()
