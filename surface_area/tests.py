# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 08:37:57 2023

@author: Benjamin Dube
"""

import unittest
import numpy as np

from .array_tools import surface_area, generate_edge_array, calc_total_area

r1 = np.array([[190,170,155], [183,165,145], [175,160,122]])

cell_x = 100
cell_y = 100


class Test_Surface_Area(unittest.TestCase):
    def test_surface_area_paper(self):
        
        res = surface_area(r1, cell_y, cell_x)
        from_paper = 10280.48
        self.assertEqual(np.round(from_paper - res[1,1]), 0)
        
    def test_sa_rounded_paper(self):
        edges = np.round(generate_edge_array(r1, cell_y, cell_x), 2)
        areas = np.round(calc_total_area(r1, edges, cell_y, cell_x), 2)
        from_paper = 10280.48
        self.assertEqual(areas[1,1], from_paper)
    
    def test_flat(self):
        r = np.ones((10,10))
        res = surface_area(r, cell_y, cell_x)
        self.assertTrue( np.all(res == 10000))
    
    def test_45(self):
        r = np.repeat(np.arange(0, 10, 1), 10).reshape((10,10))
        res = surface_area(r, 1,1)
        self.assertTrue(np.all(np.round(res,5) == np.round(np.sqrt(2), 5)))
    
class Test_Edge_Array(unittest.TestCase):
    def test_edge_array_paper(self):
        edges =  generate_edge_array(r1, cell_y, cell_x)
        data = dict(
        ab = (50.99, (0,0,0)),
        bc = (50.56, (0,1,0)),
        de = (50.80, (1,0,0)),
        ef = (50.99, (1,1,0)),
        gh = (50.56, (2,0,0)),
        hi = (53.49, (2,1,0)),
        ad = (50.12, (0,0, 2)),
        be = (50.06, (0,1,2)),
        cf = (50.25, (0,2,2)),
        dg = (50.16, (1,0, 2)),
        eh = (50.06, (1,1,2)),
        fi = (51.31, (1,2,2)),
        ae = (71.81, (0,0, 1)),
        ec = (70.89, (1, 1, 3)),
        eg = (70.89, (2,0,3)),
        ei = (73.91, (1,1,1))
        
        
        
        )
        for value, loc in data.values():
            self.assertEqual (np.round(edges[loc], 2), value) 
    
    
if __name__ == '__main__':
    unittest.main()