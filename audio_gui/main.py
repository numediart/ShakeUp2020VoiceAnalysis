# ShakeUp2020VoiceAnalysis
# License
#© - 2020 – UMONS - CLICK' Living Lab
# ShakeUp 2020 Voice Analysis of University of MONS – ISIA Lab (Kevin El Haddad) and CLICK' Living Lab (Thierry Ravet) is free software: 
# you can redistribute it and/or modify it under the terms of the 3-Clause BSD licence. 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the 3-Clause BSD licence License for more details.
 
# You should have received a copy of the 3-Clause BSD licence along with this program.  
 
# Each use of this software must be attributed to University of MONS – CLICK' Living Lab and ISIA Lab.
# ## Legal Notices
# This work was produced as part of the FEDER Digistorm project, co-financed by the European Union and the Wallonia Region.
# ![Logo FEDER-FSE](https://www.enmieux.be/sites/default/files/assets/media-files/signatures/vignette_FEDER%2Bwallonie.png)


# WARNING: This is a development server. Do not use it in a production deployment.

import random, threading, webbrowser
import winreg, os, shlex, time

from views import app

def try_find_chrome_path():
    result = None
    if winreg:
        for subkey in ['ChromeHTML\\shell\\open\\command', 'Applications\\chrome.exe\\shell\\open\\command']:
            try: result = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, subkey)
            except WindowsError: pass
            if result is not None:
                result_split = shlex.split(result, False, True)
                result = result_split[0] if result_split else None
                if os.path.isfile(result):
                    break
                result = None
    else:
        expected = "google-chrome" + (".exe" if os.name == 'nt' else "")
        for parent in os.environ.get('PATH', '').split(os.pathsep):
            path = os.path.join(parent, expected)
            if os.path.isfile(path):
                result = path
                break
    return result


port = 5000 #+ random.randint(0, 999)
url = "http://127.0.0.1:{0}".format(port)
browser_name='chromeTest2'


def locOpennbrowser():
    print('locOpennbrowser')
    try:
        testcontroller= webbrowser.get(browser_name)
        print(testcontroller)
    except:
        chromePath=try_find_chrome_path()
        webbrowser.register(browser_name,
	        None,
	        webbrowser.BackgroundBrowser(chromePath))#"C://Program Files//Google//Chrome//Application//chrome.exe"))
    webbrowser.get(browser_name).open(url, 0)
    return


if __name__ == "__main__":
    #app.logger = logging
    #app.logger = logging.getLogger('audio-gui')
    #app.run(host='0.0.0.0',debug=False,ssl_context='adhoc')
    #threading.Timer(1, lambda:locOpennbrowser() ).start()
    app.run(debug=True)
