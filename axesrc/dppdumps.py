"""
$Revision: 1.7 $ $Date: 2009/09/03 13:33:18 $
Author: Martin Kuemmel (mkuemmel@stecf.org)
Affiliation: Space Telescope - European Coordinating Facility
WWW: http://www.stecf.org/software/slitless_software/axesim/
"""
from __future__ import absolute_import

__author__ = "Martin Kuemmel <mkuemmel@eso.org>"
__date__ = "$Date: 2009/09/03 13:33:18 $"
__version__ = "$Revision: 1.7 $"
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

from . import axeutils
from . import axeinputs
from . import configfile
from .axeerror import aXeError

class DPPdumps(object):
    """
    Class to intitially handle all DPP files
    """
    def __init__(self, inima, confterm, back=False):
        """
        Initializes the class
        """
        self.inima    = inima
        self.confterm = confterm

        # find all ddp file names
        self.dpp_list = self._get_dpp_list(inima, confterm, back)

        # make sure all DPP's exist
        self._check_files(self.dpp_list)



    def _get_dpp_list(self, inima, confterm, back):
        """
        Determine the name of all DPP files
        """
        DPP_list = []

        # generate the input list for aXe
        axe_inputs = axeinputs.aXeInputList(inima, confterm)

        # go over the list of all inputs
        for an_input in axe_inputs:

            # load the configuration file
            conf = configfile.ConfigFile(axeutils.getCONF(an_input['CONFIG']))

            # get the image extensions
            ext_info = axeutils.get_ext_info(axeutils.getIMAGE(an_input['GRISIM']), conf)

            # get the name of all axe files
            axe_names =  axeutils.get_axe_names(an_input['GRISIM'], ext_info)

            # get the root name
            root_name = axe_names['DPP'].split('.DPP.fits')[0]

            # if requested,
            # append the background DPP file
            if back:
                DPP_list.append(axe_names['BCK_DPP'])
            else:
                # append the 'normal' DPP name to the list
                DPP_list.append(axe_names['DPP'])


        # return the DPP list
        return DPP_list

    def _check_files(self, dpp_list):
        """
        check for the existence of all DPP's
        """
        # go over all DPP files
        for one_dpp in dpp_list:
            # make the full path name
            full_path = axeutils.getOUTPUT(one_dpp)

            # check for existence
            if not os.path.isfile(full_path):
                # complain and out
                err_msg = 'Can not find the DPP file: %s!' % full_path
                raise aXeError(err_msg)

    def _get_contam_model(self):
        """
        Get the contamination model from in DPP
        """
        from astropy.io import fits as pyfits

        # make a default return
        contam_model = None

        # open the fits and get the header
        fits_img  = pyfits.open(axeutils.getOUTPUT(self.dpp_list[0]), 'readonly')
        fits_head =  fits_img[0].header

        # transfer value, if possible
        if 'CONTAM' in fits_head:
            contam_model = fits_head['CONTAM']

        # close the fits
        fits_img.close()

        # return the contamination model
        return contam_model

    def is_quant_contam(self):
        """
        Get the flag for quantitative contamination
        """
        # set the default value
        isquantcont = True

        # do nothing if there are not contributors
        if len(self.dpp_list) < 1:
            return isquantcont

        # get the contamination model for the first contributor
        contam_model = self._get_contam_model()

        # check whether the model is quantitative or not
        isquantcont = axeutils.is_quant_contam(contam_model)

        # return the flag
        return (contam_model, isquantcont)

    def filet_dpp(self, opt_extr=False):
        """
        Dump all DPP files
        """
        import os
        import os.path

        from . import axelowlev

        # get the drizzle tmp directory
        drztmp = axeutils.getDRZTMP()

        # go over all DPP files
        for one_dpp in self.dpp_list:

            # get the root-dir name
            root_dir = one_dpp.split('.DPP.fits')[0]
            root_dir_path = os.path.join(drztmp, root_dir)
            os.mkdir(root_dir_path)

            # create a filet objects and run the program
            filet = axelowlev.aXe_FILET(one_dpp, opt_extr=opt_extr, drztmp=root_dir_path)
            filet.runall()
            del filet
