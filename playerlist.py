import time
import logging

from _remote import ffi, lib
from manager import PluginBase
import util

SHELL_ABBREV = {
	'soldier': 'W',
	'assassin': 'D',
	'heavy': 'I',
	'fabricator': 'F',
	'toaster': 'T',
	'spark': ''
}

SHELL_MIN_HP = {
	'soldier': 80,
	'assassin': 50,
	'heavy': 100,
	'fabricator': 60
}

COLUMNS = 'shell name faction hpPercent'.split()

class Plugin(PluginBase):
	def onInit(self):
		self.config.option('visible', False, 'bool')
		self.config.option('size', 14, 'int')
		self.columns = {}
		for cname in COLUMNS:
			self.columns[cname] = util.MultilineText(
				size=self.config.size, spacing=self.config.size)

		self.seen = {}
		self.ct = 0

	def afterUpdate(self):
		cw = self.refs.ClientWorld
		if cw == ffi.NULL:
			return

		self.ct = time.perf_counter()

		allies = util.vec2list(cw.allies, 'struct WorldObject *')
		for obj in allies:
			p = obj.props
			if p.playerdata == ffi.NULL:
				continue
			acc = util.getstr(p.playerdata.accountid)
			name = util.getstr(p.displayname) or '#' + acc[:6]
			faction = util.getstr(p.playerdata.factionname)

			vid = util.getstr(p.vid)
			if vid != 'spark':
				try:
					shell = SHELL_ABBREV[vid]
				except KeyError:
					shell = '?'
				if vid in SHELL_MIN_HP and p.maxhitpoints > 0:
					mk = 1 + (p.maxhitpoints - SHELL_MIN_HP[vid]) // 10

					if mk >= 6:
						if p.maxhitpoints % 5 == 0:
							if mk == 10: # mk6 with salites
								shell += 'S'
								sort = 7
							elif mk == 9: # mk5 with salites
								shell += '5'
								sort = 5
							elif mk == 8: # mk6 with ults/inf salites, mk4 with salites
								shell += 'U'
								sort = 8
							elif mk == 7: # mk6 with inf ults, mk5 with ults/inf salites, mk3 with salites
								shell += '5+'
								sort = 5.5
							elif mk == 6: # mk6, mk5 with inf ults, mk4 with ults/inf salites, mk2 with salites
								shell += '6'
								sort = 6
						else:
							if mk == 9: # mk5 with salites
								shell += '5'
								sort = 5
							elif mk == 8: # mk4 with salites
								shell += '4'
								sort = 4
							elif mk == 7: # mk5 with ults/inf salites, mk3 with salites
								shell += '5'
								sort = 5
							elif mk == 6: # mk5 with inf ults, mk4 with ults/inf salites, mk2 with salites
								shell += '4+'
								sort = 4.5
					else:
						shell += str(mk)
						sort = mk
											
				wasSpark = False
				hpPercent = str(round(100 * p.hitpoints/p.maxhitpoints))
			else:
				if acc not in self.seen:
					shell = ''
					sort = 0
				else:
					shell = self.seen[acc][3]
					sort = self.seen[acc][7]
				wasSpark = True
				hpPercent = ''
			
			cProps = cw.asWorld.props
			if util.getstr(cProps.zone) or util.getstr(cProps.music) == 'hulk':
				boss = False
			else:
				boss = True
				
			self.seen[acc] = (self.ct, name, faction, shell, hpPercent, wasSpark, boss, sort)

	def onPresent(self):
		plst = list(self.seen.values())

		cw = self.refs.ClientWorld
		if cw != ffi.NULL and cw.asWorld.props.safe:
			# wipe old records in safe zones
			self.seen = {}

		if not self.config.visible:
			return

		plst.sort(key = lambda x: x[7], reverse = True)

		ntxt = stxt = ftxt = htxt = ''

		def addList(name, lst):
			nonlocal ntxt, ftxt, stxt, htxt
			lst = list(lst)
			if len(lst) == 0:
				return
			stxt += '{} {}\n'.format(len(lst), name)
			ntxt += '\n'
			ftxt += '\n'
			htxt += '\n'
			for x in lst:
				ntxt += x[1] + '\n'
				ftxt += x[2] + '\n'
				stxt += x[3] + '\n'
				htxt += x[4] + '\n'
		
		addList('shells', filter(lambda x: x[0] == self.ct and not x[5], plst))
		addList('sparks', filter(lambda x: x[0] == self.ct and x[5], plst))
		addList('seen before (boss)', filter(lambda x: x[0] != self.ct and not x[5] and x[6], plst))
		addList('died (boss)', filter(lambda x: x[0] != self.ct and x[5] and x[6], plst))
		addList('seen before', filter(lambda x: x[0] != self.ct and not x[5] and not x[6], plst))
		addList('died', filter(lambda x: x[0] != self.ct and x[5] and not x[6], plst))

		self.columns['shell'].text = stxt
		self.columns['hpPercent'].text = htxt
		self.columns['name'].text = ntxt
		self.columns['faction'].text = ftxt

		x = self.refs.windowW // 2
		y = 10

		self.columns['shell'].draw(x-30, y, anchorX = 1)
		self.columns['hpPercent'].draw(x - 5, y, anchorX=1)
		self.columns['name'].draw(x, y)
		self.columns['faction'].draw(x + 100, y)
