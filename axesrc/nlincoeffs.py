"""
$Revision: 1.8 $ $Date: 2009/09/11 13:53:56 $
Author: Martin Kuemmel (mkuemmel@stecf.org)
Affiliation: Space Telescope - European Coordinating Facility
WWW: http://www.stecf.org/software/slitless_software/axesim/
"""
from __future__ import absolute_import
__author__ = "Martin Kuemmel <mkuemmel@eso.org>"
__date__ = "$Date: 2009/09/11 13:53:56 $"
__version__ = "$Revision: 1.8 $"
__credits__ = """This software was developed by the ACS group of the Space Telescope -
European Coordinating Facility (ST-ECF). The ST-ECF is a department jointly
run by the European Space Agency and the European Southern Observatory.
It is located at the ESO headquarters at Garching near Munich. The ST-ECF
staff supports the European astronomical community in exploiting the research
opportunities provided by the earth-orbiting Hubble Space Telescope.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import os
import os.path

from .axeerror import aXeError

DEFAULT_COEFF_FILE = 'default_coeffs.dat'

class NonLinCoeffs(object):
    def __init__(self, image, ext_info):
        """
        Initializes the class
        """
        # store the input internally
        self.image    = image
        self.ext_info = ext_info

    def _get_coeff_filename(self):
        """
        Get the missing information about the file name
        """
        from astropy.io import fits as pyfits

        # give a default,
        # which is valid for ACS/HRC and ACS/SBC
        file_info = 1

        # open the fits image
        fits_img = pyfits.open(self.image, 'readonly')

        # check for the chip number
        if 'CCDCHIP' in fits_img[self.ext_info['fits_ext']].header:

            # store the chip number as file info (ACS/WFC)
            file_info = fits_img[self.ext_info['fits_ext']].header['CCDCHIP']

        # check for the camera number
        elif 'CAMERA' in fits_img[0].header:

            # save the camera number as file info (NIMCOS)
            file_info = fits_img[0].header['CAMERA']

        # close the fits
        fits_img.close()

        # compose the name of the coefficients file
        coeff_filename = self.image.replace('.fits','_coeffs'+str(file_info)+'.dat')

        # return the file name
        return coeff_filename, file_info

    def _get_default_coeffs(self, instr_setup, file_info):
        """
        Defines and returns the default coefficients
        """

        # the ACS/WFC branch
        if instr_setup['instrument'] == 'ACS' and instr_setup['detector'] == 'WFC':

            # select the detector
            if str(file_info) == '1':
                default_coeffs = """# ACS WFC/G800L chip 1 polynomial distortion coefficients
# Created for the data set j8qq10ikq_flt.fits using the IDCTAB q2h2010pj_idc.fits
quartic
     29.20952271       0.98463856      0.047121902    8.2405479e-06   -7.1109122e-06
   1.7714826e-06   -4.6293307e-10    -1.243901e-10   -5.3285875e-10    5.1490811e-11
   1.6734254e-14     3.425828e-14    9.5688062e-14   -1.6229259e-14    1.2711148e-13

   1047.90670925      0.040785422       0.97161774   -2.5332551e-06    5.9183197e-06
  -9.4306843e-06    7.3674246e-11   -4.3916951e-10    -5.371583e-11   -3.8747876e-10
  -1.4892746e-14   -3.1028203e-14    -1.024679e-13    2.9690206e-14   -1.4559746e-13
      """
            elif str(file_info) == '2':
                default_coeffs = """# ACS WFC/G800L chip 2 polynomial distortion coefficients
# Created for the data set j8qq10ikq_flt.fits using the IDCTAB q2h2010pj_idc.fits
quartic
    -60.03089477       0.99670914      0.041081449    8.4488359e-06   -4.9053436e-06
   1.8548877e-06   -4.6793614e-10   -6.5382805e-11   -5.2464617e-10   -7.2436454e-12
   2.2345506e-14    2.4896891e-16    3.6249087e-14   -2.3305606e-14    1.2703869e-14

  -1029.88229222      0.027935398        1.0054611   -1.5024368e-06    6.0757868e-06
  -7.2000302e-06    7.5714168e-11   -5.1072041e-10   -8.2177665e-11   -4.0937009e-10
  -1.8200403e-14   -3.1767736e-15   -3.6857861e-14    1.2036951e-14   -9.5179518e-15
      """

        # the ACS/HRC plus G800L branch
        elif instr_setup['instrument'] == 'ACS' and instr_setup['detector'] == 'HRC' and instr_setup['disperser'] == 'G800L':

            default_coeffs = """# ACS HRC/G800L polynomial distortion coefficients
# created for the image j8m820leq_flt.fits using IDCTAB n7o1634cj_idc.fits
quartic
      1.99990688        1.1312952    -0.0013998074   -3.7547287e-06    1.0207302e-05
  -8.1810015e-07    1.0776155e-10   -3.5401801e-11    4.6434155e-10    -2.226957e-11
   3.6592701e-13   -2.5148205e-12   -1.5241192e-12   -2.0761802e-13    4.1691635e-14

     -2.82194592       0.11656498       0.99377446    1.6018684e-06   -1.6023185e-06
   1.1354663e-05    4.5674659e-10    2.9705672e-10   -5.8000163e-10    7.2709968e-10
   3.0293949e-13   -1.5578453e-12    8.3043208e-13   -5.5750209e-13   -1.2661919e-12
       """

        # the ACS/HRC plus PR200L  branch
        elif instr_setup['instrument'] == 'ACS' and instr_setup['detector'] == 'HRC' and instr_setup['disperser'] == 'PR200L':
            default_coeffs = """# ACS HRC/PR200L polynomial distortion coefficients
# Created for the data set j97b06sdq_flt.fits using the IDCTAB p5b1731aj_idc.fits
quartic
      2.08138254        1.1315262    -0.0015648471   -3.7322242e-06    1.0109418e-05
  -8.1409948e-07    1.3075234e-10    2.3539512e-11    4.3735033e-10   -1.0632533e-11
   2.7818193e-13   -2.0905397e-12   -1.6363199e-12    1.4459954e-13    4.6694459e-14

     -2.81487211       0.11637744       0.99369911    1.5666096e-06   -1.5948952e-06
   1.1298673e-05    4.5586465e-10     3.300937e-10   -6.4272644e-10    4.9637125e-10
   4.1921892e-13   -1.6327524e-12    8.2560585e-13   -5.5250041e-13   -1.0909078e-12
   """


        # the ACS/SBC plus PR110L  branch
        elif instr_setup['instrument'] == 'ACS' and instr_setup['detector'] == 'SBC' and instr_setup['disperser'] == 'PR110L':
            default_coeffs = """# ACS SBC/PR110L polynomial distortion coefficients
# Created for the data set j97b11slq_flt.fits using IDCTAB o8u11395j_idc.fits
quartic
      1.04924098        1.3453513      0.020481231    -1.844869e-05    1.6256479e-05
   5.8220551e-06    4.0145121e-09    2.3509428e-09   -5.7698408e-09   -7.6725898e-09
   1.4285034e-11    1.6199441e-12    2.1826236e-12   -7.9748938e-12   -3.9227931e-11

     -4.29830391       0.10788573        1.2035841   -1.4603854e-06     2.437245e-06
   1.2681371e-05    1.5990346e-09   -8.8217959e-09   -1.0642736e-09    1.6438327e-09
   3.5539949e-12   -9.4676107e-13    1.8894413e-12    8.9042909e-12   -2.9544276e-12
       """

        # the ACS/SBC plus PR130L  branch
        elif instr_setup['instrument'] == 'ACS' and instr_setup['detector'] == 'SBC' and instr_setup['disperser'] == 'PR130L':
            default_coeffs = """# ACS SBC/PR130L polynomial distortion coefficients
# Created for the data set j97b11smq_flt.fits using IDCTAB o8u11395j_idc.fits
quartic
      1.04923371        1.3453499      0.020481207   -1.8448652e-05    1.6256445e-05
    5.822046e-06    4.0144937e-09    2.3509343e-09   -5.7698199e-09   -7.6725457e-09
   1.4284973e-11    1.6199372e-12    2.1826142e-12   -7.9748596e-12   -3.9227763e-11

     -4.29829370       0.10788562        1.2035828   -1.4603816e-06    2.4372417e-06
   1.2681344e-05    1.5990282e-09   -8.8217677e-09   -1.0642737e-09     1.643828e-09
   3.5539797e-12   -9.4675702e-13    1.8894332e-12    8.9042528e-12    -2.954415e-12
       """

        # the NICMOS plus G141 branch
        elif instr_setup['instrument'] == 'NICMOS' and instr_setup['disperser'] == 'G141':
            default_coeffs = """# ACS polynomial distortion coefficients
# taken from the stored STSDAS coefficients
cubic
      0.00000000        1.0018288                0      8.03467e-06      1.32241e-05
     5.83064e-06                0                0                0                0

      0.00000000     -0.000893359       0.99816635     -1.80668e-05        5.989e-07
    -1.15787e-05                0                0                0                0
            """

        # the WFC3 IR branch
        elif instr_setup['instrument'] == 'WFC3' and instr_setup['detector'] == 'IR':
            default_coeffs = """# Polynomial distortion coefficients
# Extracted from "t991000i_ir_idc.fits" for image:  ibbu01a3q_flt.fits
refpix 507.000000 507.000000
quartic
      0.14763942        1.0560001   -0.00016301818   -1.9466206e-07    2.5865694e-05
   7.3464039e-08   -1.7498839e-10    1.1485823e-10    8.1925668e-11    3.7606885e-11
  -5.1018929e-13    7.4936782e-13    3.9890904e-14    6.9875665e-13   -3.4250334e-13

     -9.00142431     0.0033880965       0.94300664    6.6289689e-06   -1.2124036e-07
   2.8370317e-05    1.7339207e-11   -2.2162965e-10    9.7184953e-12   -1.3682258e-10
  -5.4319899e-13    2.3592402e-13    1.4153352e-13   -2.4528943e-14    7.3598547e-13
            """

        # the WFC3 UVIS branch
        elif instr_setup['instrument'] == 'WFC3' and instr_setup['detector'] == 'UVIS':
            default_coeffs = """# Polynomial distortion coefficients
# Extracted from "t982101i_uv_idc.fits" for ibbr02bzq_flt.fits
refpix 2048.000000 384.000000
quartic
    -11.42143024        1.0037689     0.0018717218    2.8830796e-06   -2.9770541e-06
   8.5112658e-08    2.0556244e-11    -1.088005e-11    1.4832995e-11    2.2900636e-11
   1.6923456e-15     7.120595e-16   -1.7063885e-14   -4.3558507e-15   -1.5479474e-14

     -2.23386146      0.061529103        1.0054915    1.3810195e-07    2.6551435e-06
  -3.0875627e-06    3.6994702e-12      1.62375e-11   -1.0216096e-11    1.0595473e-11
   6.5447373e-16    1.2674826e-15    1.1562322e-14   -8.6793139e-15   -1.3467473e-15
            """


        # the default, which gives the identity matrix
        else:
            default_coeffs = """# Dummy polynomial distortion coefficients
# file, created bz aXe
cubic
  0.0  1.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

  0.0  0.0  1.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
      """

        return default_coeffs

    def _get_spect_setup(self):
        """
        Get the keywords for the spectroscopic setup
        """
        import os
        import os.path

        from astropy.io import fits as pyfits

        # make a dict for the setup; give defaults
        instr_setup = {'instrument': None, 'disperser': None,'detector': None}

        # open the fits image
        fits_img = pyfits.open(os.path.basename(self.image), 'readonly')

        # get the instrument keyword
        if 'INSTRUME' in fits_img[0].header:
            instr_setup['instrument'] = fits_img[0].header['INSTRUME']

        # check for detector and filter info
        if 'DETECTOR' in fits_img[0].header and \
            'FILTER1' in fits_img[0].header and \
            'FILTER2' in fits_img[0].header:

            # store the detector name
            instr_setup['detector']  = fits_img[0].header['DETECTOR']

            # store the filter names
            filter1  = fits_img[0].header['FILTER1']
            filter2  = fits_img[0].header['FILTER2']

            # this is for the HRC/WFC
            if   filter1.find('CLEAR') > -1:
                instr_setup['disperser'] = filter2
            elif filter2.find('CLEAR') > -1:
                instr_setup['disperser'] = filter1

            # this is for the SBC
            elif filter1.find('N/A') > -1:
                instr_setup['disperser'] = filter2
            elif filter2.find('N/A') > -1:
                instr_setup['disperser'] = filter1

        elif 'FILTER' in fits_img[0].header:

            # store the single filter name
            instr_setup['disperser'] = fits_img[0].header['FILTER']

        # close the fits image
        fits_img.close()

        # return the instrument setup
        return instr_setup

    def _create_dummy_coeffs(self, file_info):
        """
        Make the default coefficients
        """
        # get the instrumental setup
        instr_setup = self._get_spect_setup()

        # get the default coefficients
        default_coeffs = self._get_default_coeffs(instr_setup, file_info)

        # get the default coefficient
        # name and destroy any existing
        # file with this name
        coeff_filename = DEFAULT_COEFF_FILE
        if os.path.isfile(coeff_filename):
            os.unlink(coeff_filename)

        # create, fill and close the
        # default coefficients file
        cfile = open(coeff_filename, 'w+')
        cfile.write(default_coeffs)
        cfile.close()

        # return the coefficients name
        return coeff_filename

    def _get_coeffs_numbers(self, coeffs):
        """
        Extract the coefficients from the file content
        """
        import numpy

        from . import axeutils

        # initialize the arrays
        xcoeffs = []
        ycoeffs = []

        # parse through the content
        first = 0
        for line in coeffs:

            # neglect lines starting with a comment
            if line[0] == '#':
                continue

            # switch from x- to y-array
            # when encountering a blank line
            elif len(line.strip()) == 0:
                first = 1

            # neglect also lines starting with a string
            elif axeutils.isstringlike(line.strip().split()[0]) == 1:
                continue

            # here are the data lines
            else:

                # convert the data lines to a list
                scoeffs = line.strip().split()

                # parse through the list
                for number in scoeffs:

                    # append the item to x
                    if first == 0:
                        xcoeffs.append(float(number))

                    # or append it to y
                    else:
                        ycoeffs.append(float(number))

        # return the lists
        return xcoeffs, ycoeffs

    def mopup_pydrizzle(self, coeff_filename):
        """
        Delete al files created by pydrizzle
        """
        # compose the file names
        msk1name   = self.image.replace('.fits','_final_mask1.fits')
        msk2name   = self.image.replace('.fits','_final_mask2.fits')
        sing1name  = self.image.replace('.fits','_single_mask1.fits')
        sing2name  = self.image.replace('.fits','_single_mask2.fits')

        # check if the files exist;
        # delete them if yes
        if os.path.isfile(msk1name):
            os.unlink(msk1name)
        if os.path.isfile(msk2name):
            os.unlink(msk2name)
        if os.path.isfile(sing1name):
            os.unlink(sing1name)
        if os.path.isfile(sing2name):
            os.unlink(sing2name)

        # also delete the coefficients file
        if os.path.isfile(coeff_filename):
            os.unlink(coeff_filename)

    def make(self):
        """
        Generate the non-linear coefficients
        """
        from pyraf import iraf
        import pydrizzle

        # get the name of the coefficients file
        coeff_filename, file_info = self._get_coeff_filename()

        # determine and save the
        # base directory
        homedir = os.getcwd()

        # go into the data directory
        os.chdir(os.path.dirname(self.image))

        # reduce the coefficients file name
        coeff_filename = os.path.basename(coeff_filename)

        try:
            # create a distortion coefficient file
            pydrizzle.PyDrizzle(os.path.basename(self.image), bits_single=None, bits_final=None, updatewcs=False)
        except:
            # if this fails, create a default coefficients file
            coeff_filename = self._create_dummy_coeffs(file_info)

        # check whether the file exists
        if os.path.isfile(coeff_filename):
            # open the normal file
            cfile = file(coeff_filename, 'r')
        else:
            # complain and out
            err_msg = 'The coefficients file: %s does not exist!' % coeff_filename
            raise aXeError(err_msg)

        # read in the coefficients file,
        # close and delete it
        coeffs = cfile.readlines()
        cfile.close()

        # go back to the base directory
        os.chdir(homedir)

        # convert the string into a float array
        self.xcoeffs, self.ycoeffs = self._get_coeffs_numbers(coeffs)

        # delete unnecessary files
        self.mopup_pydrizzle(coeff_filename)

    def store_coeffs(self):
        """
        """
        from astropy.io import fits as pyfits

        # open the fits and go to the first header
        flt_imag = pyfits.open(self.image,'update', memmap=0)
        flt_head = flt_imag[0].header

        # get the instrument keyword
        if 'INSTRUME' in flt_head:
            instrume = flt_head['INSTRUME']
        else:
            instrume = None

        # get the detector or the camera keyword
        if 'DETECTOR' in flt_head:
            detector = flt_head['DETECTOR']
        elif 'CAMERA' in flt_head:
            detector = flt_head['CAMERA']
        else:
            detector = None

        # translate instrument and detector to
        # a linear pixel scale;
        # store this pixel scale
        if instrume == 'ACS' and detector == 'HRC':
            flt_head['DRZSCALE'] = (0.025, 'Scale for drizzling')
        elif instrume == 'ACS' and detector == 'SBC':
            flt_head['DRZSCALE'] = (0.025, 'Scale for drizzling')
        elif instrume == 'ACS' and detector == 'WFC':
            flt_head['DRZSCALE'] = (0.050, 'Scale for drizzling')
        elif instrume == 'NICMOS' and detector == 3:
            flt_head['DRZSCALE'] = (0.20, 'Scale for drizzling')
        elif instrume == 'WFC3' and detector == 'IR':
            flt_head['DRZSCALE'] = (0.128254, 'Scale for drizzling')
        elif instrume == 'WFC3' and detector == 'UVIS':
            flt_head['DRZSCALE'] = (0.039622, 'Scale for drizzling')
        else:
            #report_warning(140,image=putIMAGE(image))
            flt_head['DRZSCALE'] = (1.0, 'Default scale for drizzling')

        # store the number of coefficients
        flt_head['DRZCNUM'] = (len(self.xcoeffs), 'Number of coefficients per coordinate')

        # store the x-coefficients
        for index in range(len(self.xcoeffs)):
            keyname = 'DRZ%01iX%02i' % (int(self.ext_info['axe_ext']), index+1)
            keycomm = 'Drizzle coefficient %02i in X' % (index+1)
            flt_head[keyname] = (self.xcoeffs[index],keycomm)

        # store the y-coefficients
        for index in range(len(self.ycoeffs)):
            keyname = 'DRZ%01iY%02i' % (int(self.ext_info['axe_ext']), index+1)
            keycomm = 'Drizzle coefficient %02i in Y' % (index+1)
            flt_head[keyname] = (self.ycoeffs[index],keycomm)

        # close the fits
        flt_imag.close()
