from software_list_info import get_software_list_entry
from common_types import MediaType

def add_info_from_software_list(game, software):
	software.add_generic_info(game)
	compatibility = software.get_shared_feature('compatibility')
	if compatibility in ('XL', 'XL/XE'):
		game.metadata.specific_info['Requires-XL'] = True
	if compatibility == "OSb":
		game.metadata.specific_info['Requires-OS-B'] = True

	game.metadata.product_code = software.get_info('serial')

	peripheral = software.get_part_feature('peripheral')
	#TODO Setup input_info I guess:
	#cx77_touch = Touchscreen (tablet)
	#cx75_pen = Light Gun (light pen)
	#koala_pad,koala_pen = Tablet _and_ light pen
	#trackball = Trackball
	#lightgun = Light Gun (XEGS only)

	#trackfld = Track & Field controller but is that just a boneless joystick?
	#Otherwise do we assume joystick and keyboard? Hmm
	game.metadata.specific_info['Peripheral'] = peripheral

	game.metadata.specific_info['Notes'] = software.get_info('usage')
	#To be used with Atari 1400 onboard modem.
	#3 or 4 player gameplay available only on 400/800 systems
	#Keyboard overlay was supplied with cartridge
	#Chalkboard Inc.'s Powerpad Tablet required
	#Plays music only in PAL
	#Requires Lower-Silesian Turbo 2000 hardware modification installed in a tape recorder.
	#Requires a special boot disk, currently unavailable.
	#Expando-Vision hardware device required
	#Kantronics interface II required
	#Needs an Bit-3 80 Column Board or Austin-Franklin 80-Column Board to run.
	#BASIC must be enabled.
	#Pocket Modem required
	#Requires Atari 850 interface and 1200 baud modem to run.
	#2 joysticks required to play.
	#Requires the Atari Super Turbo hardware modification (or compatible ATT, UM) installed in a tape recorder.
	#Personal Peripherals Inc. Super Sketch device required
	#Modem required (and a working Chemical Bank service, obviously inactive for decades)
	#You must type 'X=USR(32768)' from the BASIC prompt to initialize it.

def add_atari_8bit_metadata(game):
	if game.metadata.media_type == MediaType.Cartridge:
		header = game.rom.read(amount=16)
		magic = header[:4]
		if magic == b'CART':
			headered = True
			cart_type = int.from_bytes(header[4:8], 'big')
			#TODO: Have nice table of cart types like with Game Boy mappers
			game.metadata.specific_info['Cart-Type'] = cart_type
			game.metadata.specific_info['Slot'] = 'Right' if cart_type in [21, 59] else 'Left'
		else:
			headered = False

	game.metadata.specific_info['Headered'] = headered

	software = get_software_list_entry(game, skip_header=16 if headered else 0)
	if software:
		add_info_from_software_list(game, software)
