#! /usr/bin/env python
import sys
import pyopenvdb as vdb
import yt
import numpy as np

#########################################################################
### Modify these values to point to your own data on your own machine ###
#########################################################################

dataFilePath = "/home/kalina/Downloads/enzo_tiny_cosmology/DD0010/DD0010"
outFileDir   = "/home/kalina/Downloads/"
variable = "Density"
isFlash = False
takeLog = False

#########################################################################
#########################################################################

# Load the dataset
ds = yt.load(dataFilePath)

# More advanced parameters here
minLevel = 0
maxLevel = ds.index.max_level

# Keep track of level 0 voxel size
largestVSize = None

# Error checking: is this variable in the data?
if not [item for item in ds.field_list if item[1] == variable]:
   print >> sys.stderr, "ERROR: Invalid field name: " + variable
   exit()

# This is required to be able to write out ghost zones for FLASH data
if isFlash:
   ds.periodicity = (True, True, True)

# Iterate through all levels
for level in range(minLevel, maxLevel+1):

   # Select specific level of grids set from dataset
   gs = ds.index.select_grids(level)

   # Initiate OpenVDB FloatGrid
   maskCube = vdb.FloatGrid()
   dataCube = vdb.FloatGrid()

   # Go over all grids in current level
   for index in range(len(gs)):

       subGrid = gs[index]

       # Extract grid (without ghost zone) with specific varible
       subGridVar = subGrid[variable]

       # Extract grid (with ghost zone) with specific varible
       subGridVarWithGZ = subGrid.retrieve_ghost_zones(n_zones=1, fields=variable)[variable]

       # Take the log (base 10), if needed
       if takeLog:
           subGridVarWithGZ = np.log10(subGridVarWithGZ)

       # Extract mask grid (eg. {[1 0 0 1],[0 1 0 1]...})
       mask = subGrid.child_mask

       # ijkout is the global x,y,z index in OpenVDB FloatGrid
       ijkout = subGrid.get_global_startindex()

       # Copy data from grid to OpenVDB FloatGrid starting from global x,y,z index in OpenVDB FloatGrid
       maskCube.copyFromArray(mask, ijk=(int(ijkout[0]),int(ijkout[1]),int(ijkout[2])))
       dataCube.copyFromArray(subGridVarWithGZ, ijk=(int(ijkout[0]),int(ijkout[1]),int(ijkout[2])))

   # Calculate a reasonable voxel size
   resolution = ds.domain_dimensions*ds.refine_by**level
   vSize = 1/float(resolution[0])

   # Keep track of level 0 voxel size
   if level==minLevel:
       largestVSize = vSize

   # Scale and translate
   dataMatrix = [[vSize, 0, 0, 0], [0, vSize, 0, 0], [0, 0, vSize, 0], [-vSize/2-largestVSize, -vSize/2-largestVSize, -vSize/2-largestVSize, 1]]
   maskMatrix = [[vSize, 0, 0, 0], [0, vSize, 0, 0], [0, 0, vSize, 0], [ vSize/2-largestVSize,  vSize/2-largestVSize,  vSize/2-largestVSize, 1]]
   dataCube.transform = vdb.createLinearTransform(dataMatrix)
   maskCube.transform = vdb.createLinearTransform(maskMatrix)

   # Write out the generated VDB
   output = []
   dataCube.name = "density"
   maskCube.name = "mask"
   output.append(maskCube)
   output.append(dataCube)
   outFilePath = "%s/%s_level%d.vdb" % (outFileDir, variable, level)
   vdb.write(outFilePath, grids=output)

   # Give feedback to see progress
   print "Finished level " + str(level)
