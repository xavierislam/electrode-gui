#!/usr/bin/python
''' This script tests interpol.py utility function that interpolates all
        electrode grids in a strip or grid configuration.

It takes as inputs three sample voxel coordinates representing the oriented
    corners of the grid as well as the path to the electrode segmentation file
    to use to map the interpolation.
'''

from os import path
import sys
sys.path.append(path.abspath('../../util'))
import cProfile

import unittest
import time

import numpy as np
import nibabel as nib
import json

from interpol import interpol

__version__ = '0.1'
__author__ = 'Lohith Kini'
__email__ = 'lkini@mail.med.upenn.edu'
__copyright__ = "Copyright 2016, University of Pennsylvania"
__credits__ = ["Xavier Islam","Sandhitsu Das", "Joel Stein",
                "Kathryn Davis"]
__license__ = "MIT"
__status__ = "Development"

DATA_DIR = 'data/'

class TestInterpolation(unittest.TestCase):
    """Unit test for interpolation on grids and strips.

    Tests different strips and grids for 5 different sample patients with both
        strips and grids using the util.interpol module.
    """

    def load_data(self):
        """returns the JSON data as a dictionary

        Takes in coordinates and grid size from 5 sample patients saved in
            interpol_examples.json file located in the same folder as this
            unit test.
        """
        with open('interpol_examples.json') as data_file:
            data = json.load(data_file)
        # Set filepath to data
        global DATA_DIR
        DATA_DIR = str(data['DATA_DIR'])
        return data

    def test_patient(self,patient_id):
        """returns True or False depending on the success of creating a
            synthetic electrode interpolation NIfTI file.

        @param patient_id: Sample patient ID
        @type patient_id: string
        @rtype: bool
        """
        try:
            preprocess_start = time.clock()
            # Load the test coordinates
            data = self.load_data()

            # Load the segmentation file
            seg_filename = '%s/%s_unburied_electrode_seg.nii.gz'%(
                DATA_DIR,
                patient_id
                )
            seg = nib.load(path.expanduser(seg_filename))
            seg_data = seg.get_data()

            # Initialize the result 3d image matrix
            res = np.zeros(seg_data.shape)

            # Set the output file name
            out_filename = seg_filename[:-35] + '%s_interpol.nii.gz'%patient_id

            # Interpolate on the 2-3 corners
            grid = data[patient_id]["1"]["grid_config"]
            M = int(grid.split('x')[0])
            N = int(grid.split('x')[1])
            radius = 0.2 * 10

            print 'Preprocessing took: %s ms'%(
                (time.clock()-preprocess_start)*1000
                )

            interpol_start = time.clock()
            if M == 1 or N == 1:
                pairs = interpol(data[patient_id]["1"]["A"],
                            data[patient_id]["1"]["B"],[],
                            M,N)
            else:
                pairs = interpol(data[patient_id]["1"]["A"],
                                data[patient_id]["1"]["B"],
                                data[patient_id]["1"]["C"],
                                M,N)
            print 'Interpolation took: %s ms'%(
                (time.clock()-interpol_start)*1000
                )

            nib_start = time.clock()
            # Create spheres of radius
            for k,v in pairs.items():
                res[v[0]-radius:v[0]+radius,
                    v[1]-radius:v[1]+radius,
                    v[2]-radius:v[2]+radius] = 1

            # Save res as new output result file
            res_nifti = nib.Nifti1Image(res,seg.get_affine())
            nib.save(res_nifti,path.expanduser(out_filename))
            print 'Postprocessing (which includes creating the final NIfTI \
                file) took: %s ms'%((time.clock()-nib_start)*1000)

            return True
        except Exception, e:
            print str(e)
            return False

    def test_HUP64(self):
        """Unit test for patient HUP64."""
        patient_id = 'HUP64'
        return self.test_patient(patient_id)

    def test_HUP65(self):
        """Unit test for patient HUP65."""
        patient_id = 'HUP65'
        return self.test_patient(patient_id)

    def test_HUP72(self):
            """Unit test for patient HUP65."""
            patient_id = 'HUP72'
            return self.test_patient(patient_id)

    def test_HUP86(self):
            """Unit test for patient HUP65."""
            patient_id = 'HUP86'
            return self.test_patient(patient_id)

    def test_HUP87(self):
            """Unit test for patient HUP65."""
            patient_id = 'HUP87'
            return self.test_patient(patient_id)

    def runTest(self):
        """Required method for running a unit test."""
        return self.test_HUP64()


if __name__ == '__main__':
    ti = TestInterpolation()
    ti.test_HUP64()
