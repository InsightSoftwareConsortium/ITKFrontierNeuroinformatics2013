#!/usr/bin/env python

"""Download input data images for the example."""

import urllib2
import os

base_url = 'http://midas3.kitware.com/midas/download/bitstream/'
files = ['101860/Sim_094_T2.mha',
         '101652/Sim_074_T2.mha']

print('fetching data')
output_dir = os.path.join('..', 'data')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for ff in files:
    response = urllib2.urlopen(base_url + ff)
    data = response.read()
    filename = os.path.join(output_dir, ff.split('/')[-1])
    print('writing ' + filename)
    with open(filename, 'wb') as fp:
        fp.write(data)
