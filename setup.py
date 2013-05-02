import os
from distutils.core import setup
import py2exe

Mydata_files = []
for files in os.listdir('C:/Users/jeanmarc/Documents/GitHub/Software/images/'):
    f1 = 'C:/Users/jeanmarc/Documents/GitHub/Software/images/' + files
    if os.path.isfile(f1): # skip directories
        f2 = 'images', [f1]
        Mydata_files.append(f2)

setup(
    console=['pronterface.py'],
    data_files = Mydata_files,
    options={
                "py2exe":{
                        "unbuffered": True,
                        "optimize": 2,
                        "excludes": ["email"]
                }
        }
)

