#!/usr/bin/env python3

import sys
from rosie.tools.mapmaker.file_reader import FileReader
from rosie.tools.mapmaker.sim_objects import *

from math import *

def parse_info_file(name, info_filename):
	fin = open(info_filename, 'r')
	reader = FileReader(fin)
	world_info = WorldInfo(reader, name)
	fin.close()
	return world_info

####### ALL INFO ######

class WorldInfo:
	def __init__(self, reader, name):
		self.name = name
		self.robot = None
		self.walls = []
		self.regions = []
		self.edges = []
		self.doors = []
		self.objects = []

		self.scale = 1.0

		# Parse each item
		try:
			word = reader.nextWord()
			while word != None:
				itemtype = word
				if itemtype == "scale":
					self.scale = float(reader.nextWord())
				elif itemtype == "robot":
					self.robot = RobotInfo().read_info(reader, self.scale)
				elif itemtype == "region":
					self.regions.append(RegionInfo().read_info(reader, self.scale))
				elif itemtype == "edge":
					self.edges.append(EdgeInfo().read_info(reader, self.scale))
				elif itemtype == "wall":
					self.walls.append(WallInfo().read_info(reader, self.scale))
				elif itemtype == "wallchain":
					self.walls.extend(parseWallChain(reader, self.scale))
				elif itemtype == "BoxObject":
					self.objects.append(BoxObject().read_info(reader, self.scale))
				elif itemtype == "Surface":
					self.objects.append(Surface().read_info(reader, self.scale))
				word = reader.nextWord()
		except Exception as e:
			raise Exception("Parsing Error on line " + str(reader.lineNum) + ":\n" + str(e))


###### ROBOT ######

class RobotInfo:
	def __init__(self):
		self.x = 0
		self.y = 0

	def read_info(self, reader, scale=1.0):
		self.x = float(reader.nextWord()) * scale
		self.y = float(reader.nextWord()) * scale
		return self

###### REGION ######

class RegionInfo:
	def __init__(self):
		self.tag_num = 0
		self.handle = ""
		self.x = 0
		self.y = 0
		self.rot = 0
		self.width = 0
		self.length = 0
		self.label = None

	def read_info(self, reader, scale=1.0):
		self.tag_num = int(reader.nextWord())
		self.handle = "wp" + ("0" if self.tag_num < 10 else "") + str(self.tag_num)
		self.x = float(reader.nextWord()) * scale
		self.y = float(reader.nextWord()) * scale
		self.rot = float(reader.nextWord())
		self.width = float(reader.nextWord()) * scale
		self.length = float(reader.nextWord()) * scale
		return self

	def contains_point(self, x, y):
		dx = self.x - x
		dy = self.y - y
		dist = sqrt(dx*dx + dy*dy)
		theta = atan2(dy, dx)
		local_theta = theta - self.rot
		xproj = dist * cos(local_theta)
		yproj = dist * sin(local_theta)
		return abs(xproj) < self.width/2 and abs(yproj) < self.length/2

###### EDGES ######

class EdgeInfo:
	def __init__(self):
		self.start_wp = 0
		self.end_wp = 0
		self.has_door = False
	
	def read_info(self, reader, scale=1.0):
		self.start_wp = int(reader.nextWord())
		self.end_wp = int(reader.nextWord())
		label = reader.nextWord()
		if label == "open":
			self.has_door = False
		elif label == "door":
			self.has_door = True
			self.door_x = float(reader.nextWord()) * scale
			self.door_y = float(reader.nextWord()) * scale
			self.door_rot = float(reader.nextWord())
		return self

###### WALLS ######

class WallInfo:
	def __init__(self):
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0

	def read_info(self, reader, scale=1.0):
		self.x1 = float(reader.nextWord()) * scale
		self.y1 = float(reader.nextWord()) * scale
		self.x2 = float(reader.nextWord()) * scale
		self.y2 = float(reader.nextWord()) * scale
		return self

def parseWallChain(reader, scale=1.0):
	walls = []
	n = int(reader.nextWord())
	x1 = float(reader.nextWord()) * scale
	y1 = float(reader.nextWord()) * scale
	for i in range(n):
		x2 = float(reader.nextWord()) * scale
		y2 = float(reader.nextWord()) * scale
		wall = WallInfo()
		wall.x1 = x1
		wall.y1 = y1
		wall.x2 = x2
		wall.y2 = y2
		walls.append(wall)
		x1 = x2
		y1 = y2
	return walls

###### DOORS #####

class DoorInfo:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.yaw = 0
		self.wp1 = 0
		self.wp2 = 0
		self.open = True

	def read_info(self, reader, scale=1.0):
		self.x = float(reader.nextWord()) * scale
		self.y = float(reader.nextWord()) * scale
		self.yaw = float(reader.nextWord())
		self.wp1 = int(reader.nextWord())
		self.wp2 = int(reader.nextWord())
		self.open = (True if reader.nextWord() == "open" else False)
		return self


