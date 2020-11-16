# NOTE: set minimum number of inputs to 0 in the "Basic" section of the SOP

# This code is called when instances of this SOP cook.
node = hou.pwd()
geo = node.geometry()

# must add all these to the "Parameter" section of the SOP
dfile = node.parm("datafile").eval() # data file to read in - Parameter type: File
rlevel = node.parm("refinement_level").eval() # refinement level - Parameter type: int
logVal = node.parm("LogValue").eval() # take log of field or not - Parameter type: Toggle
fieldName = node.parm("field_name").eval() # name of field - Parameter type: string
fieldType = node.parm("field_type").eval() # type of field - Parameter type: string

from yt import load
import numpy as np

# load your selected data file and grab the data
ds = load(dfile)
dd = ds.all_data()

# create covering grid
all_data = ds.covering_grid(level=rlevel, left_edge=[0,0.0,0.0],
                            dims=ds.domain_dimensions*ds.refine_by**rlevel)

# selects fields like "density" or ("Gas", "Density")
if len(fieldType) == 0:
    field = fieldName
else:
    field = (fieldType, fieldName)

# to take the log or to not take the log, that is the question
if logVal == 1:
    pointdata = np.log10(all_data[field].v).flatten()
else:
    pointdata = (all_data[field].v).flatten()

# rescale from 0->1 for plotting
minp = pointdata.min()
maxp = pointdata.max()
pointdata = (pointdata - minp)/(maxp-minp)

# make a new volume of correct size
volume_geo = geo.createVolume(ds.domain_dimensions[0]*ds.refine_by**rlevel,
                              ds.domain_dimensions[1]*ds.refine_by**rlevel,
                              ds.domain_dimensions[2]*ds.refine_by**rlevel)

# set the values of the volume back in Houdini
volume_geo.setAllVoxels( pointdata.flatten() )




