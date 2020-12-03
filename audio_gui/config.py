# # ShakeUp2020VoiceAnalysis
# ## License
# © - 2020 – UMONS - CLICK' Living Lab
# ShakeUp 2020 Voice Analysis of University of MONS – ISIA Lab (Kevin El Haddad) and CLICK' Living Lab (Thierry Ravet) is free software: 
# you can redistribute it and/or modify it under the terms of the GNU General Public License, version 3 or later. 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License, version 3 or later for more details.
 
# You should have received a copy of theGNU General Public License, version 3 or later along with this program.  
 
# Each use of this software must be attributed to University of MONS – CLICK' Living Lab and ISIA Lab.
# ## Legal Notices
# This work was produced as part of the FEDER Digistorm project, co-financed by the European Union and the Wallonia Region.
# ![Logo FEDER-FSE](https://www.enmieux.be/sites/default/files/assets/media-files/signatures/vignette_FEDER%2Bwallonie.png)


import os

SECRET_KEY = b'o)\xaf\x13\xc0\ndt+\xf8\xa0\xba\xef\xef=\x8e\xb9p\xb2Atqv^'


basedir = os.path.abspath(os.path.dirname(__file__))
CLIENT_SOUNDS = basedir+'/tmp/'