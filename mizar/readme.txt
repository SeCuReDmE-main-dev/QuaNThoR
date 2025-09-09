Mizar - Version 8.1.15
MML - Version 5.94.1493
May 30, 2025

Copyright (C) 1990-2025 Association of Mizar Users

Mizar System Installation Package:

  README.TXT - this file
  INSTALL.BAT - simple installation script
  MIZDB1.ZIP - auxiliary files needed by the checker
  MIZSYS.ZIP - Mizar verifier and core programs
  MIZDOC.ZIP - Mizar documents
  MIZUTIL.ZIP - auxiliary Mizar utilities
  PREL.ZIP - core database for the Mizar system
  ABSTR.ZIP - abstracts of Mizar articles
  MIZBIB.ZIP - Mizar bibliography
  MIZXML.ZIP - files providing partial XML-ization of Mizar auxiliary files
  UNZIP.EXE - Info-Zip Extraction Tool
  LICENSE - license file for Info-Zip UNZIP

Mizar Mathematical Library Package:

  MMLFULL.ZIP - full Mizar articles

-----------------------------------------------------------------

   This version of the Mizar system has been precompiled with Free Pascal
Compiler (ver. 2.6.4) for i386 compatible machines running Microsoft Windows
9x/2000/NT/XP/Vista/7/8 operating system. The package contains the Mizar
processor, the Mizar database, a set of utility programs, and GNU Emacs
Lisp mode for convenient work with the system. All Mizar articles
constituting the Mizar Mathematical Library (MML) and their abstracts
are also included in this release.

                   1. Hardware requirements

   This version of the Mizar system has been tested under MS Windows 11
operating system but it should also work with its other variants
(9x/XP/2000/NT/7/8/...). The installation requires about 260 MB of free disk
space.

                   2. Installing the system

   You can use batch command INSTALL to set up the Mizar system and the
data base (MML) on a hard disk.

   To install the Mizar system from current directory (assuming that
all the distribution files are currently in it) type:

     INSTALL c:\mizar

   You can replace path c:\mizar with the name of a different directory
and different hard disk drive letter.   c:\mizar is the path to the Mizar
directory.

   You may want to add to the path command in your AUTOEXEC.BAT the path
to the Mizar executable files, for example:

   path c:\mizar;

   If the Mizar system is installed on the different directory than
c:\mizar you have to insert the following command into your
AUTOEXEC.BAT file:

   set MIZFILES=<path>

where <path> is a path to the Mizar directory.

   The distribution of the Mizar System is supported by the Mizar Users
Group. The Group does not take the responsibility for any losses that may
result from using the Mizar system.
   All distributed materials are free of charge only for
non commercial purposes.

   Note that a new version always replaces an old one completely
if the same directories are specified during both installations.

For more information on the Mizar system look at the Mizar home page:

http://mizar.org/

With any questions or comments please contact Mizar User Service:

mus@mizar.uwb.edu.pl

