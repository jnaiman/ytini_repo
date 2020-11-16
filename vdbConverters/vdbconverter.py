# input data 
datafilename = '~/data/IsolatedGalaxy/galaxy0030/galaxy0030'

# output base name
outfilename = '~/data/vdbs/IsolatedGalaxy/threshold' 

# refinement level
level = 5 

# also, what variable to output?
field = 'density'

# what clipping tolerance?
lower_density_limit = 1e-27

# log this variable?  
log_the_variable = True

renorm_box_size = 100.0

# ---------------------------------------------------

import vdbyt

outvdbname = vdbyt.convert_vdb_with_yt(datafilename, outfilename, level, field,
                                       log_the_variable = True,
                                       variable_tol = lower_density_limit,
                                       renorm_box_size=renorm_box_size)

print('... done with writing vdb file to ' + outvdbname)
