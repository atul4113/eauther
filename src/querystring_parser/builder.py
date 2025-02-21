# coding: utf-8
'''
Created on 2012-03-28

@author: Tomasz 'Doppler' Najdek

Updated 2012-04-01 Bernard 'berni' Kobos
'''

import urllib.request, urllib.parse, urllib.error
import types

def build(item):
	def recursion(item, base=None):
		pairs = list()
		if(hasattr(item, 'values')):
			for key, value in list(item.items()):
				if(base):
					new_base = "%s[%s]" % (base, urllib.parse.quote(str(key)))
					pairs += recursion(value, new_base)
				else:
					new_base = urllib.parse.quote(str(key))
					pairs += recursion(value, new_base)
		elif(isinstance(item, list)):
			for (index, value) in enumerate(item):
				if(base):
					new_base = "%s" % (base)
					pairs += recursion(value, new_base)
				else:
					pairs += recursion(value)
		else:
			if(base):
				pairs.append("%s=%s" % (base, urllib.parse.quote(str(item))))
			else:
				pairs.append(urllib.parse.quote(str(item)))
		return pairs
	return '&'.join(recursion(item))