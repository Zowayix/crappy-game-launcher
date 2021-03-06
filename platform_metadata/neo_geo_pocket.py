import input_metadata

from platform_metadata.minor_systems import add_generic_info


def add_ngp_metadata(game):

	builtin_gamepad = input_metadata.NormalController()
	builtin_gamepad.dpads = 1
	builtin_gamepad.face_buttons = 2 #A B, also Option (Option is just Start really but they have to be special and unique and not like the other girls)
	game.metadata.input_info.add_option(builtin_gamepad)

	header = game.rom.read(amount=64)
	copyright_string = header[:28]
	game.metadata.specific_info['Copyright'] = copyright_string.decode('ascii', errors='backslashreplace')
	if copyright_string == b'COPYRIGHT BY SNK CORPORATION':
		game.metadata.publisher = 'SNK'
	#Otherwise it'd say " LICENSED BY SNK CORPORATION" and that could be any dang third party which isn't terribly useful
	#There's really not much here, so I didn't even bother reading the whole header
	game.metadata.product_code = int.from_bytes(header[32:34], 'little')
	game.metadata.specific_info['Revision'] = header[34]
	game.metadata.specific_info['Is-Colour'] = header[35] == 0x10
	internal_title = header[36:48].decode('ascii', errors='backslashreplace').strip('\0')
	if internal_title:
		game.metadata.specific_info['Internal-Title'] = internal_title

	add_generic_info(game)
