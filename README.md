# axe_help_call
fixing old iraf axe in py27

This is a quickfix for outdated axe files in iraf. To update your install you need access to your conda environment and locations.
Clone this repository, then copy everythingin axesrc/  to the directory in your environment like this:

If your conda env was called axeiraf27, and it lived in /home/users/anaconda3/env/axeiraf27/:

cp axesrc/*  /Users/users/anaconda3/envs/axeiraf27/iraf_extern/stsdas/pkg/analysis/slitless/axe/axesrc/

Then startup pyraf and try it out
