"""
$Revision: 1.2 $ $Date: 2009/09/16 06:30:57 $
Author: Martin Kuemmel (mkuemmel@stecf.org)
Affiliation: Space Telescope - European Coordinating Facility
WWW: http://www.stecf.org/software/slitless_software/axesim/
"""
from __future__ import absolute_import

__author__ = "Martin Kuemmel <mkuemmel@eso.org>"
__date__ = "$Date: 2009/09/16 06:30:57 $"
__version__ = "$Revision: 1.2 $"
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

class aXeSpcExtr(object):
    def __init__(self, grisim, objcat, dirim, config, dmag, **params):
        """
        Initializes the object
        """
        # store the input
        self.grisim = grisim
        self.objcat = objcat
        self.dirim  = dirim
        self.config = config
        self.dmag   = dmag

        self.params = params

    def _make_bckPET(self):
        """
        Generate the object PET
        """
        from . import axetasks

        # run GOL2AF
        axetasks.gol2af(grism=self.grisim, config=self.config, mfwhm=self.params['backfwhm'], back=True,
                        orient=self.params['orient'], slitless_geom=self.params['slitless_geom'],
                        exclude=self.params['exclude'], lambda_mark=self.params['lambda_mark'],
                        dmag=self.dmag, out_af=None, in_gol=None)

        #  run BACKEST
        axetasks.backest(grism=self.grisim, config=self.config, np=self.params['np'], interp=self.params['interp'],
                         niter_med=self.params['niter_med'], niter_fit=self.params['niter_fit'],
                         kappa=self.params['kappa'], smooth_length=self.params['smooth_length'],
                         smooth_fwhm=self.params['smooth_fwhm'], old_bck=False, mask=False, in_af=None,
                         out_bck=None)

        # run AF2PET
        axetasks.af2pet(grism=self.grisim, config=self.config, back=True, out_pet=None)

        # run PETFF
        axetasks.petff(grism=self.grisim, config=self.config, back=True, ffname=None)

    def _make_objPET(self):
        """
        Generate the object PET
        """
        from . import pysex2gol
        from . import axetasks

        # set the use_direct flag
        # NOTE: the flag is only usefull
        #       for the C-version, the python
        #       version does not need it!
        if self.dirim != None:
            use_direct = True
        else:
            use_direct=False

        # run SEX2GOL
        axetasks.sex2gol(grism=self.grisim, config=self.config, in_sex=self.objcat, use_direct=use_direct, direct=self.dirim,
                         dir_hdu=None, spec_hdu=None, out_sex=None)

        # run GOL2AF
        axetasks.gol2af(grism=self.grisim, config=self.config, mfwhm=self.params['extrfwhm'], back=False,
                        orient=self.params['orient'], slitless_geom=self.params['slitless_geom'],
                        exclude=self.params['exclude'], lambda_mark=self.params['lambda_mark'],
                        dmag=self.dmag, out_af=None, in_gol=None)

        # run AF2PET
        axetasks.af2pet(grism=self.grisim, config=self.config, back=False, out_pet=None)

        # run PETCONT
        axetasks.petcont(grism=self.grisim, config=self.config, cont_model=self.params['cont_model'],
                         model_scale=self.params['model_scale'], spec_models=None, object_models=None,
                         inter_type=self.params['inter_type'], lambda_psf=self.params['lambda_psf'],
                         cont_map=True, in_af=None)

        # run PETFF
        axetasks.petff(grism=self.grisim, config=self.config, back=False, ffname=None)

    def _make_spectra(self):
        """
        Extract the spectra
        """
        from . import axetasks

        # set the switch for using
        # a background PET
        if 'back' in self.params and self.params['back']:
            use_bpet = True
        else:
            use_bpet=False

        # run PET2SPC
        axetasks.pet2spc(grism=self.grisim, config=self.config, use_bpet=use_bpet, adj_sens=self.params['adj_sens'],
                         weights=self.params['weights'], do_flux=True, drzpath=False, in_af=None, opet=None,
                         bpet=None, out_spc=None)

        # run STAMPS
        axetasks.stamps(grism=self.grisim, config=self.config, sampling=self.params['sampling'], drzpath=False,
                        in_af=None, in_pet=None, out_stp=None)

    def _make_drzgeocont(self, ext_info):
        """
        """
        from . import axetasks

        # get the aXe names
        axe_names = axeutils.get_axe_names(self.grisim, ext_info)

        # for the name of a special contamination OAF
        cont_oaf = axeutils.getOUTPUT(axe_names['OAF'].replace('.OAF', '_%s.OAF' % int(self.params['drzfwhm']*10.0)))

        # run GOL2AF,
        # getting the special OAF as output
        axetasks.gol2af(grism=self.grisim, config=self.config, mfwhm=self.params['drzfwhm'], back=False,
                        orient=self.params['orient'], slitless_geom=self.params['slitless_geom'],
                        exclude=self.params['exclude'], lambda_mark=self.params['lambda_mark'],
                        dmag=self.dmag, out_af=cont_oaf, in_gol=None)

        # run PETCONT,
        # using the special OAF as input
        axetasks.petcont(grism=self.grisim, config=self.config, cont_model=self.params['cont_model'],
                       model_scale=self.params['model_scale'], spec_models=None, object_models=None,
                       inter_type=self.params['inter_type'], lambda_psf=self.params['lambda_psf'],
                       cont_map=True, in_af=cont_oaf)


    def run(self):
        """
        """
        from . import configfile
        from . import nlincoeffs

        # load the configuration files;
        # get the extension info
        conf = configfile.ConfigFile(axeutils.getCONF(self.config))
        ext_info = axeutils.get_ext_info(axeutils.getIMAGE(self.grisim), conf)
        del conf

        if ('drzfwhm' in self.params and self.params['drzfwhm']) or \
            ('cont_model' in self.params and axeutils.is_quant_contam(self.params['cont_model'])):

            # generate the non-linear distortions from the IDCTAB;
            # store them in the fits-file header
            nlins = nlincoeffs.NonLinCoeffs(axeutils.getIMAGE(self.grisim), ext_info)
            nlins.make()
            nlins.store_coeffs()
            del nlins

        # make the object PET's
        self._make_objPET()

        # make a background PET if necessary
        if 'back' in self.params and self.params['back']:
            self._make_bckPET()

        # extract the spectra
        if 'spectr' in self.params and self.params['spectr']:
            self._make_spectra()

        # make the proper non-quantitative contamination
        if ('drzfwhm' in self.params and self.params['drzfwhm']) and \
            ('cont_model' in self.params and not axeutils.is_quant_contam(self.params['cont_model'])):
            self._make_drzgeocont(ext_info)