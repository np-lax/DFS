#!/usr/bin/env python
import re
import sys

class AccessPoint:
	"""
	hold access point data and gps coords
	"""

	def __init__(self, bssid):
		#capture ID and starting info
		self.bssid = bssid
		
		#create arrays to hold lat/long/sig strength
		self.lat_a = []
		self.lon_a = []
		self.strength = []

	def get_bssid(self):
		"""return bssid of access point"""
		if self.bssid:
			return self.bssid
		else:
			return -1

	def update(self, lat_u, lon_u, dbm_u):
		"""update access point's lat/long/signal strength
			:param lat_u: latitude update
			:param lon_u: longitude update
			:param dbm_u: signal strength update
		"""
		self.lat_a.append(lat_u)
		self.lon_a.append(lon_u)
		self.strength.append(dbm_u)

	def get_current_lat(self):
		""":returns: last recorded latitude of access point"""
		if self.lat_a[-1]:
			return self.lat_a[-1]
		else:
			return -1

	def get_current_lon(self):
		""":returns: last recorded longitude of access point"""
		if self.lon_a[-1]:
			return self.lon_a[-1]
		else:
			return -1

	def get_current_strength(self):
		""":returns: last recorded signal strength of access point"""
		if self.strength[-1]:
			return self.strength[-1]
		else:
			return -1

def ap_exists(bssid, ap_list):
	"""check if ap object is in master list of AccessPoints
		:param bssid: access point BSSID from .gpsxml FILE
		:param ap_list: master list of APs to check against
		:returns: boolean value - False if AP is not in list/True if Ap is in list
	"""
	size = len(ap_list)

	if size > 0:
		for x in range(size):
			if bssid == ap_list[x].get_bssid():
				return True
	else:
		return False

	return False

def inflate_ap(ap, line):
	"""pull data from gpsxml file and add to new AccessPoint object
		:param ap: AccessPoint object
		:param line: next line in gpsxml file to pull data from
		:returns: AccessPoint object with initial location/signal data
	"""
	lat = re.search(lat_re,line)
	lat = lat.group(0)[5:-1]

	lon = re.search(lon_re, line)
	lon= lon.group(0)[5:-1]

	sig = re.search(sig_re, line)
	sig = sig.group(0)[12:-1]

	ap.update(lat, lon, sig)

	return ap



#build out regular expressions for each piece of data in the gpsxml file
bssid_re = '(bssid="([0-9A-F]{2}[:]){5}([0-9A-F]{2})")'
lat_re = '(lat="([0-9]{2})[.]([0-9]{6})")'
lon_re = '(lon="[-?]([0-9]{2}[0-9]?)[.]([0-9]{6})")'
sig_re = '(signal_dbm="[-]([0-9]{2})")'

#open gpsxml file (how to do this dynamically?) - could just run through periodically
try:
	f = open('gpstest', 'r')
except IOError:
	print("DEBUG: ERROR - COULD NOT READ FILE")
	sys.exit()

#initalize global list of access point objects
ap_list = []

#should this be a function? will it be run often? how to pull updates from file continuiously? 
for line in f:
	bssid = re.search(bssid_re, line)
	if bssid:
		bssid = bssid.group(0)[7:-1]
		#filter out probe packets
		if not bssid == '00:00:00:00:00:00':
			if not ap_exists(bssid, ap_list):
				#create new access point
				pt = AccessPoint(bssid)
				#add to global AccessPoint object list
				ap_list.append(inflate_ap(pt, line))

for x in range(len(ap_list)):
	print(ap_list[x].get_bssid())
	print(ap_list[x].get_current_strength())



#for line in f:


#ap = AccessPoint(match)

#print(ap.get_bssid())




