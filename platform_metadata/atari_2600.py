import re
import subprocess

import input_metadata
from common_types import SaveType
from info.region_info import TVSystem
from software_list_info import get_software_list_entry

def get_stella_database():
	proc = subprocess.run(['stella', '-listrominfo'], stdout=subprocess.PIPE, universal_newlines=True)
	proc.check_returncode()

	lines = proc.stdout.splitlines()
	first_line = lines[0]
	lines = lines[1:]

	columns = {}
	column_names = first_line.split('|')
	for i, column_name in enumerate(column_names):
		columns[i] = column_name

	games = {}
	for line in lines:
		game_columns = line.split('|')
		game = {}

		md5 = None
		for i, game_column in enumerate(game_columns):
			if i in columns:
				if columns[i] == 'Cartridge_MD5':
					md5 = game_column.lower()
				elif game_column:
					game[columns[i]] = game_column

		if md5:
			games[md5] = game

	return games

stella_display_format_line_regex = re.compile(r'^\s*Display Format:\s*(PAL|NTSC)\*')
stella_cart_md5_line_regex = re.compile(r'^\s*Cart MD5:\s*([a-z0-9]{32})')
def autodetect_from_stella(game):
	proc = subprocess.run(['stella', '-rominfo', game.rom.path], stdout=subprocess.PIPE, universal_newlines=True)
	if proc.returncode != 0:
		return None

	md5 = None
	lines = proc.stdout.splitlines()
	for line in lines:
		cart_md5_match = stella_cart_md5_line_regex.match(line)
		if cart_md5_match:
			md5 = cart_md5_match[1]
			break

		display_format_match = stella_display_format_line_regex.match(line)
		if display_format_match:
			game.tv_type = TVSystem[display_format_match.group(1)]
		#Can also get bankswitch type from here if needed. Controller 0 and Controller 1 too, but then it's probably better to just get that from the database
	return md5

def add_controller_info(game, controller):
	#TODO: Take note of Controller_SwapPaddles
	#TODO: Use some attribute to note if PADDLES_IAXIS or PADDLES_IAXDR, whatever those do exactly that's different from just PADDLES
	#Track & Field controller is just a joystick with no up or down, so Stella doesn't count it as separate from joystick

	#TODO: Hella refactor this too I guess

	if not controller:
		return

	if controller in ('PADDLES', 'PADDLES_IAXIS', 'PADDLES_IAXDR'):
		game.metadata.input_info.add_option(input_metadata.Paddle())
		#Paddles come in pairs and hence have 2 players per port
	elif controller == 'JOYSTICK':
		joystick = input_metadata.NormalController()
		joystick.dpads = 1
		joystick.face_buttons = 1
		game.metadata.input_info.add_option(joystick)
	elif controller in ('AMIGAMOUSE', 'ATARIMOUSE'):
		#ATARIMOUSE is an ST mouse, to be precise
		#TODO: Should differentiate between AMIGAMOUSE and ATARIMOUSE? Maybe that's needed for something; anyway they both have 2 buttons
		mouse = input_metadata.Mouse()
		mouse.buttons = 2
		game.metadata.input_info.add_option(mouse)
	elif controller == 'TRAKBALL':
		#Reminder to not do .buttons = 2, while it does have 2 physical buttons, they're just to make it ambidextrous; they function as the same single button
		game.metadata.input_info.add_option(input_metadata.Trackball())
	elif controller == 'KEYBOARD':
		#The Keyboard Controller is actually a keypad, go figure. Actually, it's 2 keypads, go figure twice. BASIC Programming uses both at once and Codebreakers uses them separately for each player, so there's not really anything else we can say here.
		keypad = input_metadata.Keypad()
		keypad.keys = 12
		game.metadata.input_info.add_option(keypad)
	elif controller in 'COMPUMATE':
		#The CompuMate is a whole dang computer, not just a keyboard. But I guess it's the same sorta thing
		keyboard = input_metadata.Keyboard()
		keyboard.keys = 42
		game.metadata.input_info.add_option(keyboard)
	elif controller == 'GENESIS':
		game.metadata.specific_info['Uses-Genesis-Controller'] = True

		genesis_controller = input_metadata.NormalController()
		genesis_controller.dpads = 1
		genesis_controller.face_buttons = 3
		game.metadata.input_info.add_option(genesis_controller)
	elif controller == 'BOOSTERGRIP':
		joystick = input_metadata.NormalController()
		joystick.dpads = 1
		joystick.face_buttons = 3 #There are two on the boostergrip, but it passes through to the 2600 controller which still has a button, or something
		game.metadata.input_info.add_option(joystick)
		game.metadata.specific_info['Uses-Boostergrip'] = True
	elif controller == 'DRIVING':
		#Has 360 degree movement, so not quite like a paddle. MAME actually calls it a trackball
		game.metadata.input_info.add_option(input_metadata.SteeringWheel())
	elif controller == 'MINDLINK':
		game.metadata.input_info.add_option(input_metadata.Biological())
	else:
		game.metadata.input_info.add_option(input_metadata.Custom())

def parse_stella_db(game, game_info):
	#TODO: Get year out of name
	if 'Cartridge_Manufacturer' in game_info:
		manufacturer = game_info['Cartridge_Manufacturer']
		if ', ' in manufacturer:
			game.metadata.publisher, _, game.metadata.developer = manufacturer.partition(', ')
		else:
			game.metadata.publisher = manufacturer
			#TODO: Clean up manufacturer names (UA Limited > UA)
	if 'Cartridge_ModelNo' in game_info:
		game.metadata.product_code = game_info['Cartridge_ModelNo']
	if 'Cartridge_Note' in game_info:
		#TODO: Ignore things like "Uses the Paddle Controllers" and "Console ports are swapped" that are already specified by other fields
		#TODO: Append to notes that might already exist
		game.metadata.specific_info['Notes'] = game_info['Cartridge_Note']
	if 'Display_Format' in game_info:
		display_format = game_info['Display_Format']
		if display_format == 'NTSC':
			game.metadata.tv_type = TVSystem.NTSC
		elif display_format == 'PAL':
			game.metadata_tv_type = TVSystem.PAL
		#TODO: Can also be SECAM, NTSC50, PAL60, or SECAM60

	left_controller = None
	if 'Controller_Left' in game_info:
		left_controller = game_info['Controller_Left']

	right_controller = None
	no_save = True
	if 'Controller_Right' in game_info:
		right_controller = game_info['Controller_Right']
		if right_controller in ('ATARIVOX', 'SAVEKEY'):
			game.metadata.save_type = SaveType.MemoryCard
			#If these devices are plugged in, they aren't controllers
			right_controller = None
			no_save = False

		if right_controller == 'KIDVID':
			game.metadata.specific_info['Uses-Kid-Vid'] = True
			right_controller = None

	if no_save:
		game.metadata.save_type = SaveType.Nothing

	swap_ports = False
	if 'Controller_SwapPorts' in game_info:
		if game_info['Controller_SwapPorts'] == 'YES':
			swap_ports = True

	if swap_ports:
		add_controller_info(game, right_controller)
		add_controller_info(game, left_controller)
	else:
		add_controller_info(game, left_controller)
		add_controller_info(game, right_controller)

_stella_db = None

def add_atari_2600_metadata(game):
	global _stella_db
	#Python, you're officially a fucking dumbarse. Of course that's a fucking global variable. It is right there. Two lines above here. In the global fucking scope.
	if _stella_db is None:
		try:
			_stella_db = get_stella_database()
		except subprocess.CalledProcessError:
			pass

	software = get_software_list_entry(game)
	if software:
		software.add_generic_info(game)
		game.metadata.product_code = software.get_info('serial')

		if game.metadata.publisher == 'Homebrew':
			#For consistency. There's no company literally called "Homebrew"
			game.metadata.publisher = game.metadata.developer

		game.metadata.specific_info['Uses-Supercharger'] = software.get_shared_feature('requirement') == 'scharger'
		#TODO: Add input info using 'peripheral' feature:
		#"Kid's Controller", "kidscontroller" (both are used)
		#"paddles"
		#"keypad"
	else:
		#TODO: Combine both sources of information
		md5 = autodetect_from_stella(game)
		if md5 in _stella_db:
			game_info = _stella_db[md5]
			parse_stella_db(game, game_info)
