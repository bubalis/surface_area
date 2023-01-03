# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 19:21:39 2023

@author: Benjamin Dube
"""

from setuptools import setup







with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()




setup(
    name='surface_area',
    version= '1.0.1',

    url='https://github.com/bubalis/surface_area',
    author='Ben Dube',
    description = 'A tool for calculating pixel-by-pixel surface area from a digital elevation model.',
    author_email='benjamintdube@gmail.com',
    long_description_content_type="text/markdown",
    long_description = long_description,
    entry_points = {'console_scripts': 
    [
    'surface_area = surface_area.surface_area:main',
                     ] },

    


   

    
    #packages = [ 'automations.QA_QC', 'automations.anew_utils', 'automations.user_data',  'automations.program_formats'],
    install_requires = [
     'numpy==1.20.3',
     'rasterio==1.2.1',
     ],
    
    include_package_data=False,
    

)