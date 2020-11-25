
#import scipy.io.wavfile as wav
#import matplotlib.pyplot as plt
#import numpy as np
import random, threading, webbrowser
import winreg, os, shlex, time

from audioapp import app

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
