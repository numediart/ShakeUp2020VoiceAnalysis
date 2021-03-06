# # ShakeUp2020VoiceAnalysis
# ## License
# © - 2020 – UMONS - ISIA Lab - CLICK' Living Lab
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

#option

USE_VOICEDETECTION = False#this flag enable/disable the voice detection (based on our test it's not necessary)

SOUND_MAX_SIZE = 5000000 #max memory in Bytes accepted for a wav file
USED_VOWELS = ["O", "A", "E", "I", "OU"]#these number of vowels will be segmented and these labels will be used in the figures

SOUND_MEMORY_DURATION =1*60*60#every unused file is deleted after this duration in second

#USED_VOWELS = ["LA0", "LA1", "LA2", "LA3", "LA4", "LA5"]