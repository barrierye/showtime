import os
import platform

if platform.system() == 'Darwin':
    # This fix doesn't work on Mojave. It does the trick on High Sierra though.
    # see: https://github.com/darkskyapp/forecast-ruby/issues/13
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
