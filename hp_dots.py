import math
import logging

from _remote import ffi, lib
from manager import PluginBase
import util

ELEMS = 'hp hpmax ammo ammomax currency'.split()


class Plugin(PluginBase):
	def onInit(self):
		self.config.options('int', {
			'dot_size': 4,
			'dot_y': 10
		})
		self.config.options('color', {
			'dot_outline': 0x000000,
			'dot_color': 0x00ffff,
		})

		for name in ELEMS:
			setattr(self, 'txt_' + name, util.PlainText(font='HemiHeadBold'))

		self.draw = False

	def afterUpdate(self):
		self.draw = False
		wc = self.refs.WorldClient
		cw = self.refs.ClientWorld
		if wc == ffi.NULL or cw == ffi.NULL or cw.player == ffi.NULL:
			return

		if wc.hud != ffi.NULL and wc.hud.hudStatus != ffi.NULL:
			ffi.cast('struct UIElement *', wc.hud.hudStatus).show = False

		ptype = util.getClassName(cw.player)
		if ptype not in self.refs.CASTABLE['PlayerCharacter']:
			return

		self.draw = True

	def onPresent(self):
		colorAlpha = self.config.dot_color >> 24
		dot_color = self.config.dot_color - (colorAlpha << 24)
		#logging.info(hex(colorAlpha))
		outlineAlpha = self.config.dot_outline >> 24
		dot_outline = self.config.dot_outline - (outlineAlpha << 24)

		if not self.draw:
			return
		
		# hp dots
		wv = self.refs.WorldView
		cw = self.refs.ClientWorld
		player = ffi.cast('struct WorldObject *', cw.player)
		props = player.props
		hp = props.hitpoints
		maxhp = props.maxhitpoints

		ds = self.config.dot_size

		if hp == maxhp:
			return

		x = props.xmp // 256 + props.wmp // 512 - wv.offset.x
		y = props.ymp // 256 - wv.offset.y

		# window space coords
		x = round(x / self.refs.scaleX)
		y = round(y / self.refs.scaleY)
		dy = y - ds - self.config.dot_y
		cw = self.refs.canvasW_[0]
		ch = self.refs.canvasH_[0]
		self.refs.canvasW_[0] = self.refs.windowW
		self.refs.canvasH_[0] = self.refs.windowH

		dotsNum = math.ceil((maxhp - hp) / 25)
		for dot in range(dotsNum):
			xOffset = (ds * 2 * dot) - (ds * (2 * (dotsNum - 1) + 1)) // 2
			colorMod = colorAlpha
			outlineMod = outlineAlpha
			if dot == dotsNum - 1:
				colorMod = round(colorMod * (((maxhp - hp - 1) % 25) + 1) / 25)
				outlineMod = round(outlineMod * (((maxhp - hp - 1) % 25) + 1) / 25)
				
			colorMod = colorMod << 24
			outlineMod = outlineMod << 24
			
			self.refs.XDL_FillRect(
				x + xOffset, dy, ds, ds, colorMod + dot_color, lib.BLENDMODE_BLEND)
			self.refs.XDL_FillRect(
					x + xOffset - 1, dy - 1, 1, ds + 2, outlineMod + dot_outline, lib.BLENDMODE_BLEND)
			self.refs.XDL_FillRect(
					x + xOffset + ds, dy - 1, 1, ds + 2, outlineMod + dot_outline, lib.BLENDMODE_BLEND)
			self.refs.XDL_FillRect(
					x + xOffset, dy - 1, ds, 1, outlineMod + dot_outline, lib.BLENDMODE_BLEND)
			self.refs.XDL_FillRect(
					x + xOffset, dy + ds, ds, 1, outlineMod + dot_outline, lib.BLENDMODE_BLEND)

		# restore coords
		self.refs.canvasW_[0] = cw
		self.refs.canvasH_[0] = ch


	def __del__(self):
		wc = self.refs.WorldClient
		if wc != ffi.NULL and wc.hud != ffi.NULL:
			if wc.hud.hudStatus != ffi.NULL:
				ffi.cast('struct UIElement *', wc.hud.hudStatus).show = True