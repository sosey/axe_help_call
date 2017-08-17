"""
$Revision: 1.15 $ $Date: 2010/05/18 07:56:00 $
Author: Martin Kuemmel (mkuemmel@stecf.org)
Affiliation: Space Telescope - European Coordinating Facility
WWW: http://www.stecf.org/software/slitless_software/axesim/
"""
from __future__ import absolute_import
__author__ = "Martin Kuemmel <mkuemmel@eso.org>"
__date__ = "$Date: 2010/05/18 07:56:00 $"
__version__ = "$Revision: 1.15 $"
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
from . import axeutils
from . import configfile
from .axeerror import aXeError

from axe import axe_asciidata

class MEFExtractor(object):
    """
    """
    def __init__(self, drizzle_params, obj_dol, bck_dol=None, opt_extr=None):
        """
        Initializes the class
        """
        # determine and store the file names
        self.ext_names = self._get_ext_names(drizzle_params)

        # store the optimal extraction boolean
        self.opt_extr = opt_extr

        if opt_extr:
            self.opt_names = self._get_opt_names(drizzle_params)

        # save the object lists
        self.obj_dol = obj_dol
        self.bck_dol = bck_dol

        # generate a list with all MEF files;
        # write the list to a file
        self.obj_dol.sort()
        obj_list = MEFList(self.obj_dol.get_mef_files())
        obj_list.writeto(self.ext_names['OLIS'])
        del obj_list
        if bck_dol:
            self.bck_dol.sort()
            bck_list = MEFList(self.bck_dol.get_mef_files())
            bck_list.writeto(self.ext_names['BLIS'])
            del bck_list

            # copy some extensions
            # from the background to
            # the object drizzled frame
            if opt_extr:
                self._copy_optext_images()

            # do the intrinsic background
            # subtraction on the stamp images
            self._subtract_background()

        # create and save the configuration file for the
        # drizzled images
        drzconf = DrizzleConf(drizzle_params)
        drzconf.writeto(self.ext_names['CON_CONF'])
        del drzconf

        # create the dummy image for the extraction
        dummy_fits = DummyImage(self.ext_names['DRZ_FITS'])
        del dummy_fits

    def _get_ext_names(self, drizzle_params):
        """
        Define the file names for extracting the drizzled spectra
        """
        # make an empty dictionary
        ext_names = {}

        # check that a root name is given;
        # message and out if not
        if not 'ROOT' in drizzle_params:
            err_msg = 'Not root name given. Nothing to do!'
            raise aXeError(err_msg)

        # compose the filenames for the input list, the configuration file
        # and the OAF file
        ext_names['OLIS']     = drizzle_params['ROOT'] + '_2.lis'

        ext_names['BLIS']     = drizzle_params['ROOT'] + '_2.BCK.lis'

        ext_names['OAF']      = drizzle_params['ROOT'] + '_2.OAF'
        ext_names['DRZ_OAF']  = axeutils.getDRIZZLE(ext_names['OAF'])

        ext_names['BAF']      = drizzle_params['ROOT'] + '_2.BAF'
        ext_names['DRZ_BAF']  = axeutils.getDRIZZLE(ext_names['BAF'])

        ext_names['FITS']     = drizzle_params['ROOT'] + '.fits'
        ext_names['DRZ_FITS'] = axeutils.getDRIZZLE(ext_names['FITS'])

        ext_names['OPET']     = drizzle_params['ROOT'] + '_2.PET.fits'
        ext_names['DRZ_OPET'] = axeutils.getDRIZZLE(ext_names['OPET'])

        ext_names['BPET']     = drizzle_params['ROOT'] + '_2.BCK.PET.fits'
        ext_names['DRZ_BPET'] = axeutils.getDRIZZLE(ext_names['BPET'])

        ext_names['SPC']      = drizzle_params['ROOT'] + '_2.SPC.fits'
        ext_names['DRZ_SPC']  = axeutils.getDRIZZLE(ext_names['SPC'])

        ext_names['STP']      = drizzle_params['ROOT'] + '_2.STP.fits'
        ext_names['DRZ_STP']  = axeutils.getDRIZZLE(ext_names['STP'])

        ext_names['CONF']     = drizzle_params['ROOT'] + '.conf'
        ext_names['CON_CONF'] = axeutils.getCONF(ext_names['CONF'])

        # return the dictionary
        return ext_names

    def _get_opt_names(self, drizzle_params):
        """
        Define the file names for the optimal extraction
        """
        # make an empty dictionary
        opt_names = {}

        # check that a root name is given;
        # message and out if not
        if not 'ROOT' in drizzle_params:
            err_msg = 'Not root name given. Nothing to do!'
            raise aXeError(err_msg)

        # compose the filenames for the input list, the configuration file
        # and the OAF file
        opt_names['OLIS']     = drizzle_params['ROOT'] + '_2.lis'

        opt_names['BLIS']     = drizzle_params['ROOT'] + '_2.BCK.lis'

        opt_names['OAF']      = drizzle_params['ROOT'] + '_2.OAF'
        opt_names['DRZ_OAF']  = axeutils.getDRIZZLE(opt_names['OAF'])

        opt_names['BAF']      = drizzle_params['ROOT'] + '_2.BAF'
        opt_names['DRZ_BAF']  = axeutils.getDRIZZLE(opt_names['BAF'])

        opt_names['FITS']     = drizzle_params['ROOT'] + '.fits'
        opt_names['DRZ_FITS'] = axeutils.getDRIZZLE(opt_names['FITS'])

        opt_names['OPET']     = drizzle_params['ROOT'] + '_2_opt.PET.fits'
        opt_names['DRZ_OPET'] = axeutils.getDRIZZLE(opt_names['OPET'])

        opt_names['BPET']     = drizzle_params['ROOT'] + '_2_opt.BCK.PET.fits'
        opt_names['DRZ_BPET'] = axeutils.getDRIZZLE(opt_names['BPET'])

        opt_names['SPC']      = drizzle_params['ROOT'] + '_2_opt.SPC.fits'
        opt_names['DRZ_SPC']  = axeutils.getDRIZZLE(opt_names['SPC'])

        opt_names['STP']      = drizzle_params['ROOT'] + '_2_opt.STP.fits'
        opt_names['DRZ_STP']  = axeutils.getDRIZZLE(opt_names['STP'])

        opt_names['CONF']     = drizzle_params['ROOT'] + '.conf'
        opt_names['CON_CONF'] = axeutils.getCONF(opt_names['CONF'])

        # return the dictionary
        return opt_names

    def _copy_optext_images(self):
        from astropy.io import fits as pyfits

        # open the object and background drizzle lists
        obj_list = axe_asciidata.open(self.opt_names['OLIS'])
        bck_list = axe_asciidata.open(self.opt_names['BLIS'])

        # go over one list
        for index in range(obj_list.nrows):

            # take and compose the filenames
            obj_img = axeutils.getDRIZZLE(obj_list[0][index].strip())
            bck_img = axeutils.getDRIZZLE(bck_list[0][index].strip())

            # open the fits file
            obj_fits = pyfits.open(obj_img, 'update')
            bck_fits = pyfits.open(bck_img, 'readonly')

            # replace the VAR- and the MOD- extension
            obj_fits['VAR'].data = bck_fits['VAR'].data
            obj_fits['MOD'].data = bck_fits['MOD'].data

            # close the files
            obj_fits.flush()
            obj_fits.close()
            bck_fits.close()

    def _subtract_background(self):
        """
        Make the background subtraction
        """
        import os
        import os.path

        import numpy
        from astropy.io import fits as pyfits

        # go over the object drizzle list
        for index in range(len(self.obj_dol)):

            # take and compose the filenames
            obj_img = self.obj_dol[index].ext_names['MEF']
            bck_img = self.bck_dol[index].ext_names['MEF']

            # make sure the ID's of object and background match
            if self.obj_dol[index].objID != self.bck_dol[index].objID:
                err_msg = 'The object ID: %s and background ID %s are not identical!' % (self.obj_dol[index].objID, self.bck_dol[index].objID)
                raise aXeError(err_msg)

            # open the fits file
            obj_fits = pyfits.open(obj_img, 'update')
            bck_fits = pyfits.open(bck_img, 'readonly')

            # compose an image HDU for the background
            # and the background error
            bck_sci = pyfits.ImageHDU(data=bck_fits['SCI'].data, header=bck_fits['SCI'].header, name='SCIBCK')
            bck_err = pyfits.ImageHDU(data=bck_fits['ERR'].data, header=bck_fits['ERR'].header, name='ERRBCK')

            # subtract the background;
            # process the error
            obj_fits['SCI'].data = obj_fits['SCI'].data - bck_sci.data
            obj_fits['ERR'].data = numpy.sqrt(obj_fits['ERR'].data * obj_fits['ERR'].data + bck_err.data * bck_err.data)

            # manifest in header
            hist_string1 = 'The extension SCIBCK and ERRBCK were used for '
            hist_string2 = 'background and background error'
            obj_fits['SCI'].header['SCIBCK'] = ( 'DONE', 'subtraction of background stamp')
            obj_fits['SCI'].header['ERRBCK'] = ( 'DONE', 'processing of background stamp error')
            obj_fits['SCI'].header.add_history(hist_string1)
            obj_fits['SCI'].header.add_history(hist_string2)

            # append the new background
            # and the error to the object fits
            obj_fits.append(bck_sci)
            obj_fits.append(bck_err)

            # store the images
            # and delete the objects
            obj_fits.flush()
            obj_fits.close()
            bck_fits.close()
            del bck_sci
            del bck_err

        # delete all background files
        self.bck_dol.delete_files()

    def extract(self, infwhm, outfwhm, adj_sens):
        """
        Extract spectra from the MEF files
        """
        from . import axetasks

        # make the OAF
        self.obj_dol.make_OAF_file(infwhm, outfwhm, self.ext_names['DRZ_OAF'])

        # run DRZ2PET
        axetasks.drz2pet(inlist=self.ext_names['OLIS'], config=self.ext_names['CONF'],
                         opt_extr=False, back=False, in_af=self.ext_names['DRZ_OAF'],
                         out_pet=self.ext_names['DRZ_OPET'])

        # run PET2SPC
        axetasks.pet2spc(grism=self.ext_names['FITS'] , config=self.ext_names['CONF'],
                         use_bpet=False, adj_sens=adj_sens, weights=False, do_flux=True,
                         drzpath=True, in_af=self.ext_names['DRZ_OAF'], opet=self.ext_names['DRZ_OPET'],
                         bpet=None, out_spc=self.ext_names['DRZ_SPC'])

        # run STAMPS
        axetasks.stamps(grism=self.ext_names['FITS'], config=self.ext_names['CONF'],
                        sampling="rectified", drzpath=True, in_af=self.ext_names['DRZ_OAF'],
                        in_pet=self.ext_names['DRZ_OPET'], out_stp=self.ext_names['STP'])

        if self.opt_extr:
            # run DRZ2PET
            axetasks.drz2pet(inlist=self.opt_names['OLIS'], config=self.opt_names['CONF'],
                             opt_extr=self.opt_extr, back=False, in_af=self.opt_names['DRZ_OAF'],
                             out_pet=self.opt_names['DRZ_OPET'])

            # run PET2SPC
            axetasks.pet2spc(grism=self.opt_names['FITS'] , config=self.opt_names['CONF'],
                             use_bpet=False, adj_sens=adj_sens, weights=False, do_flux=True,
                            drzpath=True, in_af=self.opt_names['DRZ_OAF'], opet=self.opt_names['DRZ_OPET'],
                            bpet=None, out_spc=self.opt_names['DRZ_SPC'])

            # run STAMPS
            axetasks.stamps(grism=self.opt_names['FITS'], config=self.opt_names['CONF'],
                            sampling="rectified", drzpath=True, in_af=self.opt_names['DRZ_OAF'],
                            in_pet=self.opt_names['DRZ_OPET'], out_stp=self.opt_names['STP'])

class MEFList(axe_asciidata.asciidata.AsciiData):
    """
    Class for the list of drizzled MEF files
    """
    def __init__(self, mef_files):
        """
        Initializes the class
        """
        # create an empty list
        super(MEFList, self).__init__(ncols=1, nrows=len(mef_files))

        # go over all MEF files
        for index in range(len(mef_files)):
            # insert the file name
            self[0][index] = mef_files[index]

class DrizzleConf(configfile.ConfigList):
    """
    Class for the drizzle configuration file
    """
    def __init__(self, drizzle_params, modvar=0):
        """
        Initializes the class
        """
        # get the name of the input configuration file;
        # load the configuration file
        config_file = drizzle_params['CONF']
        config = configfile.ConfigFile(axeutils.getCONF(config_file))

        # get the header
        header = self._get_header()

        # generate the list of keywords
        keylist = self._make_keylist(config, drizzle_params, modvar)

        # generate the configuration file via the super class
        super(DrizzleConf, self).__init__(keylist, header)

    def _get_header(self):
        """
        Define and return the header
        """
        # define the header
        header = """
    #---------------------------------------------------
    #
    # Configuraton file to extract 1D spectra from
    # 2D drizzled images. The configuration file was
    # automatically created to be further used in tasks
    # as "aXe_DRZ2PET" and "aXe_PET2SPC". Please change
    # this file ONLY if you know what you are doing!
    #
    #---------------------------------------------------
"""
        # return the header
        return header

    def _make_keylist(self, config, drizzle_params, modvar):
        """
        Creates a list of configuration keywords
        """
        # initialize the list
        keylist = []

        keylist.append(configfile.ConfKey('INSTRUMENT', config.get_gvalue('INSTRUMENT')))
        keylist.append(configfile.ConfKey('CAMERA', config.get_gvalue('CAMERA')))
        keylist.append(configfile.ConfKey('SCIENCE_EXT', 'SCI'))
        keylist.append(configfile.ConfKey('DQ_EXT', 'DQ'))
        keylist.append(configfile.ConfKey('ERRORS_EXT', 'ERR'))
        keylist.append(configfile.ConfKey('WEIGHT_EXT', 'WHT'))
        keylist.append(configfile.ConfKey('FFNAME', 'None'))
        keylist.append(configfile.ConfKey('DRZRESOLA', config.get_gvalue('DRZRESOLA')))
        keylist.append(configfile.ConfKey('DRZSCALE', config.get_gvalue('DRZSCALE')))
        keylist.append(configfile.ConfKey('DRZLAMB0', config.get_gvalue('DRZLAMB0')))
        keylist.append(configfile.ConfKey('DRZXINI', config.get_gvalue('DRZXINI')))

        keylist.append(configfile.ConfKey('DRZPFRAC', drizzle_params['PFRAC']))
        keylist.append(configfile.ConfKey('DRZPSCALE', drizzle_params['PSCALE']))
        keylist.append(configfile.ConfKey('DRZKERNEL', drizzle_params['KERNEL']))

        keylist.append(configfile.ConfKey('DRZROOT', drizzle_params['ROOT']))
        if config.get_gvalue('POBJSIZE') != None:
            keylist.append(configfile.ConfKey('POBJSIZE', config.get_gvalue('POBJSIZE')))
        if config.get_gvalue('SMFACTOR') != None:
            keylist.append(configfile.ConfKey('SMFACTOR', config.get_gvalue('SMFACTOR')))
        keylist.append(configfile.ConfKey('BEAMA', config.beams['A'].get_bvalue('BEAMA')))
        keylist.append(configfile.ConfKey('MMAG_EXTRACT_A', config.beams['A'].get_bvalue('MMAG_EXTRACT_A')))
        keylist.append(configfile.ConfKey('MMAG_MARK_A', config.beams['A'].get_bvalue('MMAG_MARK_A')))

        keylist.append(configfile.ConfKey('DYDX_ORDER_A', '1'))
        keylist.append(configfile.ConfKey('DYDX_A_0', '0.0'))
        keylist.append(configfile.ConfKey('DYDX_A_1', '0.0'))
        keylist.append(configfile.ConfKey('XOFF_A', '0.0'))
        keylist.append(configfile.ConfKey('YOFF_A', '0.0'))
        keylist.append(configfile.ConfKey('DISP_ORDER_A', '1'))
        keylist.append(configfile.ConfKey('DLDP_A_0', config.get_gvalue('DRZLAMB0')))
        keylist.append(configfile.ConfKey('DLDP_A_1', config.get_gvalue('DRZRESOLA')))
        keylist.append(configfile.ConfKey('SENSITIVITY_A', config.beams['A'].get_bvalue('SENSITIVITY_A')))
        if modvar:
            keylist.append(configfile.ConfKey('MODEL_EXT', 'MOD'))
            keylist.append(configfile.ConfKey('VARIANCE_EXT', 'VAR'))

        # return the keyword list
        return keylist

class DummyImage(object):
    """
    Class for the dummy image
    """
    def __init__(self, filename):
        """
        Initializes the class
        """
        import os
        import os.path

        from astropy.io import fits as pyfits

        # delete an existing file
        if os.path.isfile(filename):
            os.unlink(filename)

        # generate a HDU list;
        # append the primary HDU
        mex_hdu = pyfits.HDUList()
        mex_hdu.append(pyfits.PrimaryHDU())

        # add the various extensions to the list
        mex_hdu.append(self._make_dummy_ext('SCI'))
        mex_hdu.append(self._make_dummy_ext('ERR'))
        mex_hdu.append(self._make_dummy_ext('DQ'))

        # write the HDU list to a file
        mex_hdu.writeto(filename)
        mex_hdu.close()

    def _make_dummy_ext(self, extname):
        """
        Creates an empty image extension
        """
        from astropy.io import fits as pyfits
        import numpy

        # create an empty image HDU
        imglayer = pyfits.PrimaryHDU()

        # write the extension version
        imglayer.header['EXTVER'] = 1

        # add some data
        imglayer.data = numpy.zeros((10,10))

        # create the image HDU
        imgext = pyfits.ImageHDU(imglayer.data, header=imglayer.header, name=extname)

        # return the image HDU
        return imgext
