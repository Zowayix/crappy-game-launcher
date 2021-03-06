import input_metadata
from common_types import SaveType
from config.main_config import main_config
from info.region_info import TVSystem
from software_list_info import get_software_list_entry

from .atari_controllers import xegs_gun

standard_gamepad = input_metadata.NormalController()
standard_gamepad.dpads = 1
standard_gamepad.face_buttons = 2
input_types = {
	1: standard_gamepad,
	#The rest only have one button, for the record
	2: xegs_gun,
	3: input_metadata.Paddle(), #Is this valid? Some games which have this seem to actually use the lightgun
	4: input_metadata.Trackball(), #Is this a valid value?
}

def _add_atari_7800_header_info(rom, metadata, header):
	metadata.input_info.set_inited()

	#Header version: 0
	#Magic: 1-17
	metadata.add_alternate_name(header[17:49].decode('ascii', errors='backslashreplace').rstrip('\0 '), 'Header-Title')
	#ROM size excluding header: Big endian 49-53
	#Special cart type: 53
	#Cart type: 54

	left_input_type = header[55]
	right_input_type = header[56]

	left_controller_option = None
	right_controller_option = None
	if left_input_type != 0:
		left_controller_option = input_metadata.InputOption()
		if left_input_type in input_types:
			left_controller_option.inputs.append(input_types[left_input_type])
		else:
			left_controller_option.inputs.append(input_metadata.Custom('Unknown {0}'.format(left_input_type)))

	if right_input_type != 0:
		right_controller_option = input_metadata.InputOption()
		if right_input_type in input_types:
			right_controller_option.inputs.append(input_types[right_input_type])
		else:
			right_controller_option.inputs.append(input_metadata.Custom('Unknown {0}'.format(right_input_type)))

	if left_controller_option and right_controller_option:
		number_of_players = 2 #I guess?
		metadata.input_info.input_options.append(left_controller_option)
	elif right_controller_option and not left_controller_option:
		number_of_players = 1
		metadata.specific_info['Swap-Ports'] = True
		metadata.input_info.input_options.append(right_controller_option)
	elif left_controller_option and not right_controller_option:
		number_of_players = 1
		metadata.input_info.input_options.append(left_controller_option)
	else:
		number_of_players = 0
	metadata.specific_info['Number-of-Players'] = number_of_players

	tv_type = header[57]

	if tv_type == 1:
		metadata.specific_info['TV-Type'] = TVSystem.PAL
	elif tv_type == 0:
		metadata.specific_info['TV-Type'] = TVSystem.NTSC
	else:
		if main_config.debug:
			print('Something is wrong with', rom.path, ', has TV type byte of', tv_type)
		metadata.specific_info['Invalid-TV-Type'] = True

	save_type = header[58]
	if save_type == 0:
		metadata.save_type = SaveType.Nothing
	elif save_type == 1:
		#High Score Cart, an unreleased device that ends up being supported by some games (apparently). Just saves high scores so don't get too excited.
		#You plug the High Score Cart into the 7800 and then the game into the High Score Cart, so I guess this is the easiest thing to call it.
		metadata.save_type = SaveType.Internal
		metadata.specific_info['Uses-Hiscore-Cart'] = True
	elif save_type == 2:
		#AtariVox/SaveKey. Both are third party products which plug into the controller port, so what else can you call them except memory cards?
		metadata.save_type = SaveType.MemoryCard
	elif main_config.debug:
		print(rom.path, 'has save type byte of ', save_type)
	
	#Reserved: 59-63
	#Expansion module required: 64


def add_atari_7800_metadata(game):
	header = game.rom.read(amount=128)
	if header[1:10] == b'ATARI7800':
		headered = True
		_add_atari_7800_header_info(game.rom, game.metadata, header)
	else:
		headered = False

	game.metadata.specific_info['Headered'] = headered

	software = get_software_list_entry(game, skip_header=128 if headered else 0)
	if software:
		software.add_standard_metadata(game.metadata)
		game.metadata.add_notes(software.get_info('usage'))
		#Don't need sharedfeat > compatibility to get TV type or feature > peripheral, unheadered roms won't work anyway
