#!/usr/bin/env python

"""Download input data images for the example."""

import urllib2
import os

url = 'http://packages.bic.mni.mcgill.ca/mni-models/colin27/mni_colin27_1998_minc2.zip'

print('fetching data')
output_dir = os.path.join('..', 'data')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
response = urllib2.urlopen(url)
data = response.read()
filename = os.path.join(output_dir, url.split('/')[-1])
print('writing ' + filename)
with open(filename, 'wb') as fp:
    fp.write(data)
