#!/bin/python
#####################################################################
# rpy_matrix_conversion.py
# Max Libbrecht
# Updated 7/10
# ---------------------------------------------------------
# This module is responsible for converting between
# different representations of matrices.  
#####################################################################

import sys
sys.path.append('../')

import rpy2.robjects as rpy
r = rpy.r

import numpy as np
from copy import deepcopy



#####################################################################
# python_matrix_to_r
#####################################################################
def python_matrix_to_r(m, dimnames=None):
	vec = rpy.FloatVector(reduce(lambda x,y: x+y, m, []))
	if dimnames is None:
		r_dimnames = r['list'](rpy.StrVector(range(1,len(m)+1)), 
		                       rpy.StrVector(range(1,len(m[0])+1)))
	else:
		r_dimnames = r['list'](rpy.StrVector(dimnames[0]), 
		                       rpy.StrVector(dimnames[1]))
	return r['matrix'](vec, dimnames=r_dimnames, nrow=len(m), byrow=True)


#####################################################################
# list_to_r_matrix
#####################################################################
def list_to_r_matrix(lst, dimnames=None, nrow=1):
	if len(lst) == 0 or nrow == 0:
		return r('NA')
	if dimnames is None:
		r_dimnames = r['list'](rpy.StrVector(range(1,nrow+1)), 
		                       rpy.StrVector(range(1,len(lst)/nrow+1)))
	else:
		assert(len(dimnames[0])==nrow)
		assert(len(dimnames[1])==len(lst)/nrow)
		r_dimnames = r['list'](rpy.StrVector(dimnames[0]), 
		                       rpy.StrVector(dimnames[1]))
	return r['matrix'](rpy.FloatVector(lst), dimnames=r_dimnames, nrow=nrow, byrow=True)


#####################################################################
# r_matrix_to_python
#####################################################################
def r_matrix_to_python(m):
	nrow = r['nrow'](m)[0]
	ncol = r['ncol'](m)[0]
	m_as_list = list(r['t'](m))
	python_matrix = []
	for i in range(nrow):
		python_matrix.append(m_as_list[i*ncol:i*ncol+ncol])
	dimnames = [list(r['labels'](m)[0]), list(r['labels'](m)[1])]
	return python_matrix, dimnames

#####################################################################
# r_matrix_to_np
#####################################################################
def r_matrix_to_np(m):
	nrow = r['nrow'](m)[0]
	ncol = r['ncol'](m)[0]
	dimnames = [list(r['labels'](m)[0]), list(r['labels'](m)[1])]
	m_as_list = list(r['t'](m))
	m_arr = np.array(m_as_list)
	m_arr.shape = (nrow, ncol)
	m_np = np.matrix(m_arr, copy=False)
	return m_np, dimnames
	

#####################################################################
# np_matrix_to_r
#####################################################################
def np_matrix_to_r(m, dimnames=None):
	m_list = deepcopy(map(float, list(m.flat)))
	nrow = m.shape[0]
	return list_to_r_matrix(m_list, nrow=nrow, dimnames=dimnames)

#####################################################################
# np_matrix_to_python
#####################################################################
def np_matrix_to_python(m):
	return m.tolist()


