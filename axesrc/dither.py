"""
$Revision: 1.7 $ $Date: 2010-06-14 12:53:12 $
Author: Martin Kuemmel
Affiliation: Space Telescope - European Coordinating Facility
"""
from __future__ import absolute_import, print_function

__author__ = "Martin Kuemmel <mkuemmel@eso.org>"
__date__ = "$Date: 2011-04-25 13:46:00 $"
__version__ = "$Revision: 1.8 $"
__credits__ = """This software was developed by the ACS group of the Space Telescope -
European Coordinating Facility (ST-ECF). The ST-ECF is a department jointly
run by the European Space Agency and the European Southern Observatory.
It is located at the ESO headquarters at Garching near Munich. The ST-ECF
staff supports the European astronomical community in exploiting the research
opportunities provided by the earth-orbiting Hubble Space Telescope.

2011-04-22 H. Bushouse: Modified the Drizzle.run method to trap the redirected
Stdout from the drizzle task and print it for the user to see (ticket #700).

2011-04-25 H. Bushouse: Additional updates to Drizzle.run method to raise an
exception if input/output file names are >80 chars long (ticket #700).
"""
from .axeerror import aXeError

class Drizzle(object):
    """
    Class to wrap drizzle command
    """
    def __init__(self):
        """
        Initializes the class
        """
        from pyraf import iraf
        from iraf import stsdas, analysis, dither

        # unlearn the task
        iraf.unlearn('drizzle')

    def run(self, data, in_mask, outdata, outweig, coeffs, wt_scl, drizzle_params, img_nx, img_ny):
        """
        Do the drizzling

        Currently, the basic command is the iraf-version of drizzle,
        but the pydrizzle version may at some point be used instead.
        """
        from pyraf import iraf
        from iraf import stsdas, analysis, dither

        # Check for file names that are too long for the drizzle task
        if len(data) > 80:
           err_msg = 'File name "%s" is too long (>80 chars) for drizzle task' % data
           raise aXeError(err_msg)
        if len(outdata) > 80:
           err_msg = 'File name "%s" is too long (>80 chars) for drizzle task' % outdata
           raise aXeError(err_msg)

        ret = iraf.drizzle(data=data, outdata=outdata, outweig=outweig,
                     in_mask=in_mask, wt_scl=wt_scl, coeffs=coeffs,
                     outnx=img_nx, outny=img_ny,
                     in_un=drizzle_params['IN_UN'], out_un=drizzle_params['OUT_UN'],
                     pixfrac=drizzle_params['PFRAC'],scale=drizzle_params['PSCALE'],
                     kernel=drizzle_params['KERNEL'], Stdout=1)

        for i in range(len(ret)):
            print(ret[i])

class MedianCombine(object):
    """
    Class to median-combine individual drizzles
    """
    def __init__(self, contributors, drizzle_params, mult_drizzle_par, ext_names):
        """
        Initialize the class
        """

        # store the parameters
        self.combine_maskpt  = mult_drizzle_par['combine_maskpt']
        self.combine_type    = mult_drizzle_par['combine_type']
        self.combine_nsigma1 = mult_drizzle_par['combine_nsigma1']
        self.combine_nsigma2 = mult_drizzle_par['combine_nsigma2']
        self.combine_nlow    = mult_drizzle_par['combine_nlow']
        self.combine_nhigh   = mult_drizzle_par['combine_nhigh']
        self.combine_lthresh = mult_drizzle_par['combine_lthresh']
        self.combine_hthresh = mult_drizzle_par['combine_hthresh']
        self.combine_grow    = mult_drizzle_par['combine_grow']

        self.ext_names = ext_names

       # store the name of the median image
        self.median_image = ext_names['MED']

        # store the readout noise
        self.rdnoise      = drizzle_params['RDNOISE']

        self.input_data = self._get_inputs(contributors)

    def _get_inputs(self, contributors):
        """
        Extract the inputs for the median combine
        """
        # generate an empty dictionary
        input_data = {}

        # go over all contributing objects
        sci_imgs = []
        wht_imgs = []
        exp_vals = []
        rdn_vals = []
        sky_vals = []
        exp_tot  = 0.0
        for one_contrib in contributors:

            # put the image names to the list
            sci_imgs.append(one_contrib.ext_names['SING_SCI'])
            wht_imgs.append(one_contrib.ext_names['SING_WHT'])

            # put image properties to the list
            exp_vals.append(one_contrib.info['EXPTIME'])
            rdn_vals.append(self.rdnoise)
            if 'SKY_CPS' in one_contrib.info:
                sky_vals.append(one_contrib.info['SKY_CPS'])
            else:
                err_msg = 'Sky value missing for image: %s!' % input_data['sci_imgs']
                raise aXeError(err_msg)

            # compose the total exposure time
            exp_tot += one_contrib.info['EXPTIME']

        # put the images to the dictionary
        input_data['sci_imgs'] = sci_imgs
        input_data['wht_imgs'] = wht_imgs

        # put the values to the dictionary
        input_data['exp_vals'] = exp_vals
        input_data['rdn_vals'] = rdn_vals
        input_data['sky_vals'] = sky_vals


        input_data['exp_tot']  = exp_tot

        # return the dictionary
        return input_data

    def run(self):
        """
        Run the median combine step

        The code was either directly stolen from the corresponding
        pydrizzle version or done after this version. Necessary
        adjustments to the slitless data were applied.
        """
        import os
        import os.path
        from astropy.io import fits as pyfits

        # Import numpy functionality
        import numpy as np

        # Import general tools
        from stsci.imagestats import ImageStats
        from stsci.image import numcombine
        from stsci.image.numcombine import numCombine

        import multidrizzle
        import multidrizzle.minmed
        from multidrizzle.minmed import minmed

        sci_data = []

        for one_image in self.input_data['sci_imgs']:
            if os.access(one_image,os.F_OK):
                in_fits = pyfits.open(one_image, 'readonly')
                sci_data.append(in_fits[0].data)
                in_fits.close()

        wht_data = []
        for one_image in  self.input_data['wht_imgs']:
            if os.access(one_image,os.F_OK):
                in_fits = pyfits.open(one_image, 'readonly')
                wht_data.append(in_fits[0].data)
                in_fits.close()
            else:
                print(one_image,"not found/created by multidrizzle...skipping it.")

        if len(sci_data) != len(wht_data):
            print("The number of single_sci images created by multidrizzle does not match the number of single_wht files created!")
            raise aXeError("Multidrizzle error")

        weight_mask_list = []

        #added the except so that if the image area contains only zeros then the zero value is returned which is better for later processing
        #we dont understand why the original lower=1e-8 value was supplied unless it was for the case of spectral in the normal field of view
        #see #1110
        for wht_arr in wht_data:
            try:
                tmp_mean_value = self.combine_maskpt * ImageStats(wht_arr,lower=1e-8,lsig=None,usig=None,fields="mean",nclip=0).mean
            except (ValueError,AttributeError):
                tmp_mean_value = 0.
                print("tmp_mean_value set to 0 because no good pixels found; %s"%(self.ext_names["MEF"]))
            except:
                tmp_mean_value = 0.
                print("tmp_mean_value set to 0; possible uncaught exception in dither.py; %s"%(self.ext_names["MEF"]))


            weight_mask = np.zeros(wht_arr.shape,dtype=np.uint8)
            np.putmask(weight_mask, np.less(wht_arr, tmp_mean_value), 1)


            weight_mask_list.append(weight_mask)

        if len(sci_data) < 2:
            print('\nNumber of images to flatten: %i!' % len(sci_data))
            print('Set combine type to "minimum"!')
            self.combine_type = 'minimum'

        if (self.combine_type == "minmed"):
            # Create the combined array object using the minmed algorithm
            result = minmed(sci_data,  # list of input data to be combined.
                            wht_data,# list of input data weight images to be combined.
                            self.input_data['rdn_vals'],           # list of readnoise values to use for the input images.
                            self.input_data['exp_vals'],           # list of exposure times to use for the input images.
                            self.input_data['sky_vals'],           # list of image background values to use for the input images
                            weightMaskList = weight_mask_list,     # list of imput data weight masks to use for pixel rejection.
                            combine_grow = self.combine_grow,           # Radius (pixels) for neighbor rejection
                            combine_nsigma1 = self.combine_nsigma1,     # Significance for accepting minimum instead of median
                            combine_nsigma2 = self.combine_nsigma2      # Significance for accepting minimum instead of median
                            )
        else:
            #print 'going to other', combine_type
            # Create the combined array object using the numcombine task
            result = numCombine(sci_data,
                                numarrayMaskList=weight_mask_list,
                                combinationType=self.combine_type,
                                nlow=self.combine_nlow,
                                nhigh=self.combine_nhigh,
                                upper=self.combine_hthresh,
                                lower=self.combine_lthresh
                                )

        #print result.combArrObj
        hdu = pyfits.PrimaryHDU(result.combArrObj)
        hdulist = pyfits.HDUList([hdu])
        hdulist[0].header['EXPTIME'] = ( self.input_data['exp_tot'], 'total exposure time')
        hdulist.writeto(self.median_image)

        # delete the various arrays
        for one_item in sci_data:
            del one_item
        del sci_data
        for one_item in wht_data:
            del one_item
        del wht_data
        for one_item in weight_mask_list:
            del one_item
        del weight_mask_list


class Blot(object):
    """
    Class to wrap the blot command
    """
    def __init__(self):
        """
        Initializes the class
        """
        from pyraf import iraf
        from iraf import stsdas, analysis, dither

        # unlearn the task
        iraf.unlearn('blot')

    def run(self, in_data, out_data, coeffs, out_nx, out_ny, drizzle_params, mult_drizzle_par):
        """
        Do the actual blot

        Currently only the iraf version of blot is invoked.
        """
        from pyraf import iraf
        from iraf import stsdas, analysis, dither

        iraf.blot(data=in_data, outdata=out_data, scale=drizzle_params['PSCALE'], coeffs=coeffs,
                  outnx=out_nx, outny=out_ny, interpol=mult_drizzle_par['blot_interp'],
                  sinscl=mult_drizzle_par['blot_sinscl'], in_un=drizzle_params['IN_UN'],
                  out_un=drizzle_params['OUT_UN'], expkey='exptime', expout = 'input')

class Deriv(object):
    """
    Class for the deriv-command
    """
    def __init__(self):
        """
        Initializes the class
        """
        pass

    def _absoluteSubtract(self, array,tmpArray,outArray):
        """
        Subtract the absolute value of two images
        """
        import numpy
        #subtract shifted image from imput image
        tmpArray = array - tmpArray
        #take the absolute value of tmpArray
        tmpArray = numpy.fabs(tmpArray)
        #save maximum value of outArray or tmpArray and save in outArray
        outArray = numpy.maximum(tmpArray,outArray)
        #zero out tmpArray before reuse
        tmpArray = tmpArray * 0.

        return (tmpArray,outArray)

    def _qderiv(self, array): # TAKE THE ABSOLUTE DERIVATIVE OF A NUMARRY OBJECT
        """
        Take the absolute derivate of an image in memory
        """
        import numpy

        #Create 2 empty arrays in memory of the same dimensions as 'array'
        tmpArray = numpy.zeros(array.shape, dtype=numpy.float64)
        outArray = numpy.zeros(array.shape, dtype=numpy.float64)

        # Get the length of an array side
        (naxis1,naxis2) = array.shape

        #Main derivate loop:
        #Shift images +/- 1 in Y.
        for y in range(-1,2,2):
            if y == -1:
                #shift input image 1 pixel right
                tmpArray[0:(naxis1-1),1:(naxis2-1)] = array[0:(naxis1-1),0:(naxis2-2)]

            else:
                #shift input image 1 pixel left
                tmpArray[0:(naxis1-1),0:(naxis2-2)] = array[0:(naxis1-1),1:(naxis2-1)]

            # subtract the arrays
            (tmpArray,outArray) = self._absoluteSubtract(array,tmpArray,outArray)

        #Shift images +/- 1 in X.
        for x in range(-1,2,2):
            if x == -1:
                #shift input image 1 pixel right
                tmpArray[1:(naxis1-1),0:(naxis2-1)] = array[0:(naxis1-2),0:(naxis2-1)]

            else:
                #shift input image 1 pixel left
                tmpArray[0:(naxis1-2),0:(naxis2-1)] = array[1:(naxis1-1),0:(naxis2-1)]

            # subtract the arrays
            (tmpArray,outArray) = self._absoluteSubtract(array,tmpArray,outArray)

        # delete the tmp-array
        del tmpArray

        # return the result
        return outArray.astype(numpy.float32)

    def run(self, in_name, out_name):
        """
        Code stolen from Multidrizzle.deriv()
        """
        import os
        import os.path

        from astropy.io import fits as pyfits

        import multidrizzle
        import multidrizzle.quickDeriv

        # store the names
        self.in_name  = in_name
        self.out_name = out_name

        # make sure the input image exists
        if not os.path.isfile(self.in_name):

            # complain and out if not
            err_msg = "Image missing: %s!" % self.in_name
            raise aXeError(err_msg)

        # delete output name if existing
        if os.path.isfile(self.out_name):
            os.unlink(self.out_name)

        print("Running quickDeriv on ", self.in_name)
        # OPEN THE INPUT IMAGE IN READ ONLY MODE
        img = pyfits.open(self.in_name,mode='readonly', memmap=0)

        # calling qderiv with the assumption that the
        # input file is a simple FITS file.
        absderiv = multidrizzle.quickDeriv.qderiv(img["PRIMARY"].data)
        #absderiv = self._qderiv(img["PRIMARY"].data)

        # WRITE THE OUTPUT IMAGE TO A FITS FILE
        outfile = pyfits.open(self.out_name,'append')
        outhdu = pyfits.PrimaryHDU(data=absderiv)
        outfile.append(outhdu)

        # CLOSE THE IMAGE FILES
        outfile.close()
        img.close()
        del outfile
        del img

class CRIdent(object):
    def __init__(self, drizzle_params, mult_drizzle_par):
        """
        Initializes the class
        """
        self.driz_cr_scale   = (float(mult_drizzle_par['driz_cr_scale'].split()[0]), float(mult_drizzle_par['driz_cr_scale'].split()[1]))
        self.driz_cr_snr     = (float(mult_drizzle_par['driz_cr_snr'].split()[0]),   float(mult_drizzle_par['driz_cr_snr'].split()[1]))
        self.driz_cr_grow    = int(mult_drizzle_par['driz_cr_grow'])
        self.driz_cr_ctegrow = 0

        # store the readout noise
        self.rdnoise      = drizzle_params['RDNOISE']

    def _identify_crr(self, in_img, blot_img, blotder_img, exptime, sky_val):
        """
        Identify CRR's and other deviant pixels

        The code was taken from muldidrizzle.DrizCR. Small adjustments and
        re-factoring was done.
        """
        import numpy
        import stsci.convolve as convolve

        # create an empty file
        __crMask = numpy.zeros(in_img.shape,dtype=numpy.uint8)

        # Part 1 of computation:
        # flag the central pixels
        # Create a temp array mask
        __t1 = numpy.absolute(in_img - blot_img)
        __ta = numpy.sqrt(numpy.absolute(blot_img * exptime + sky_val * exptime) + self.rdnoise*self.rdnoise)
        __t2 = self.driz_cr_scale[0] * blotder_img + self.driz_cr_snr[0] * __ta / exptime
        __tmp1 = numpy.logical_not(numpy.greater(__t1, __t2))

        # mop up
        del __ta
        del __t1
        del __t2

        # Create a convolution kernel that is 3 x 3 of 1's
        __kernel = numpy.ones((3,3),dtype=numpy.uint8)
        # Create an output tmp file the same size as the input temp mask array
        __tmp2 = numpy.zeros(__tmp1.shape,dtype=numpy.int16)
        # Convolve the mask with the kernel
        convolve.convolve2d(__tmp1,__kernel,output=__tmp2,fft=0,mode='nearest',cval=0)
        del __kernel
        del __tmp1

        # Part 2 of computation
        # flag the neighboring pixels
        # Create the CR Mask
        __xt1 = numpy.absolute(in_img - blot_img)
        __xta = numpy.sqrt(numpy.absolute(blot_img * exptime + sky_val * exptime) + self.rdnoise*self.rdnoise)
        __xt2 = self.driz_cr_scale[1] * blotder_img + self.driz_cr_snr[1] * __xta / exptime

        # It is necessary to use a bitwise 'and' to create the mask with numarray objects.
        __crMask = numpy.logical_not(numpy.greater(__xt1, __xt2) & numpy.less(__tmp2,9) )

        del __xta
        del __xt1
        del __xt2
        del __tmp2

        # Part 3 of computation - flag additional cte 'radial' and 'tail' pixels surrounding CR pixels as CRs
        # In both the 'radial' and 'length' kernels below, 0->good and 1->bad, so that upon
        # convolving the kernels with __crMask, the convolution output will have low->bad and high->good
        # from which 2 new arrays are created having 0->bad and 1->good. These 2 new arrays are then 'anded'
        # to create a new __crMask.

        # recast __crMask to int for manipulations below; will recast to Bool at end
        __crMask_orig_bool= __crMask.copy()
        __crMask= __crMask_orig_bool.astype( numpy.int8 )

        # make radial convolution kernel and convolve it with original __crMask
        cr_grow_kernel = numpy.ones((self.driz_cr_grow, self.driz_cr_grow))     # kernel for radial masking of CR pixel
        cr_grow_kernel_conv = __crMask.copy()   # for output of convolution
        convolve.convolve2d( __crMask, cr_grow_kernel, output = cr_grow_kernel_conv)

        # make tail convolution kernel and convolve it with original __crMask
        cr_ctegrow_kernel = numpy.zeros((2*self.driz_cr_ctegrow+1,2*self.driz_cr_ctegrow+1))  # kernel for tail masking of CR pixel
        cr_ctegrow_kernel_conv = __crMask.copy()  # for output convolution

        # which pixels are masked by tail kernel depends on sign of ctedir (i.e.,readout direction):
        ctedir=0
        if ( ctedir == 1 ):  # HRC: amp C or D ; WFC: chip = sci,1 ; WFPC2
            cr_ctegrow_kernel[ 0:ctegrow, ctegrow ]=1    #  'positive' direction
        if ( ctedir == -1 ): # HRC: amp A or B ; WFC: chip = sci,2
            cr_ctegrow_kernel[ ctegrow+1:2*ctegrow+1, ctegrow ]=1    #'negative' direction
        if ( ctedir == 0 ):  # NICMOS: no cte tail correction
            pass

        # do the convolution
        convolve.convolve2d( __crMask, cr_ctegrow_kernel, output = cr_ctegrow_kernel_conv)

        # select high pixels from both convolution outputs; then 'and' them to create new __crMask
        where_cr_grow_kernel_conv    = numpy.where( cr_grow_kernel_conv < self.driz_cr_grow*self.driz_cr_grow,0,1 )        # radial
        where_cr_ctegrow_kernel_conv = numpy.where( cr_ctegrow_kernel_conv < self.driz_cr_ctegrow, 0, 1 )     # length
        __crMask = numpy.logical_and( where_cr_ctegrow_kernel_conv, where_cr_grow_kernel_conv) # combine masks

        __crMask = __crMask.astype(numpy.uint8) # cast back to Bool

        del __crMask_orig_bool
        del cr_grow_kernel
        del cr_grow_kernel_conv
        del cr_ctegrow_kernel
        del cr_ctegrow_kernel_conv
        del where_cr_grow_kernel_conv
        del where_cr_ctegrow_kernel_conv

        # get back the result
        return __crMask

    def _createcrmaskfile(self, crName = None, crmask = None, header = None, in_imag=None):
        """
        Create a fits file containing the generated cosmic ray mask.
        """
        import os
        import os.path
        from astropy.io import fits as pyfits
        import numpy

        # migrate the data over
        _cr_file = numpy.zeros(in_imag.shape,numpy.uint8)
        _cr_file = numpy.where(crmask,1,0).astype(numpy.uint8)

        # rmove file if it exists
        if os.path.isfile(crName):
            os.unlink(crName)

        # Create the output file
        fitsobj = pyfits.HDUList()

        if (header != None):
            del(header['NAXIS1'])
            del(header['NAXIS2'])
            if 'XTENSION' in header:
                del(header['XTENSION'])
            if 'EXTNAME' in header:
                del(header['EXTNAME'])
            if 'EXTVER' in header:
                del(header['EXTVER'])
            if 'NEXTEND' in header:
                header['NEXTEND'] = 0

            hdu = pyfits.PrimaryHDU(data=_cr_file,header=header)
            del hdu.header['PCOUNT']
            del hdu.header['GCOUNT']

        else:
            hdu = pyfits.PrimaryHDU(data=_cr_file)

        fitsobj.append(hdu)
        fitsobj.writeto(crName)

        # close the fits image
        fitsobj.close()

        # mop up
        del fitsobj
        del _cr_file

    def run(self, in_image, blot_image, blotder_image, exptime, sky_val, crr_image):
        """
        Do the identification
        """
        from astropy.io import fits as pyfits

        # open the input image
        inImage = pyfits.open(in_image, 'readonly')

        # open the blot image
        blotImage = pyfits.open(blot_image, 'readonly')

        # open the blot image
        blotDerImage = pyfits.open(blotder_image, 'readonly')

        # identify the CR's
        crr_data = self._identify_crr(inImage[0].data, blotImage[0].data, blotDerImage[0].data, exptime, sky_val)

        # save the image
        self._createcrmaskfile(crr_image, crr_data, inImage[0].header, inImage[0].data)

        # delete the array
        del crr_data

        # close the images
        inImage.close()
        blotImage.close()
        blotDerImage.close()

