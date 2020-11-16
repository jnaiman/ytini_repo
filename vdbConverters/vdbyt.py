import pyopenvdb as vdb
import yt
import numpy as np


def convert_vdb_with_yt(datafilename, outfilename, level, variable_out, log_the_variable=False,
                        variable_tol=None, renorm=True, renorm_box=True, renorm_box_size = 10.0):
    # load your selected data file and grab the data
    ds = yt.load(datafilename)
    dd = ds.all_data()

    all_data = ds.covering_grid(level=level, left_edge=ds.domain_left_edge,
                                dims=ds.domain_dimensions*ds.refine_by**level)

    # to take the log or to not take the log, that is the question
    if log_the_variable is True:
        pointdata = np.log10(all_data[variable_out].v)
        if variable_tol is not None:
            variable_tol = np.log10(variable_tol)
    else:
        pointdata = (all_data[variable_out].v)

    # rescale from 0->1 for plotting
    if renorm:
        minp = pointdata.min()
        maxp = pointdata.max()
        pointdata = (pointdata - minp)/(maxp-minp)
        if variable_tol is not None:
            variable_tol = (variable_tol - minp)/(maxp-minp)

    # take out threshold data -> set to 0
    if variable_tol is not None:
        pointdata[pointdata < variable_tol] = 0.0

    # generate vdb
    domain_box = vdb.FloatGrid()
    domain_box.background = 0.0

    domain_box.copyFromArray(pointdata, ijk=(0,0,0), tolerance = 0)

    # rescale to voxel size
    if renorm_box:
        vsize = renorm_box_size/float(pointdata.shape[0]) # assumes square box/shifting to x-axis units!
        domain_box.transform = vdb.createLinearTransform(voxelSize=vsize) # tolist is for formatting

    #print('Writing vdb file...')
    outvdbname = outfilename + '_' + variable_out + '_one_level_is_' + str(level).zfill(3)  + '.vdb'
    vdb.write(outvdbname, grids=domain_box)
    #print('... done with writing vdb file to ' + outvdbname)

    return outvdbname





