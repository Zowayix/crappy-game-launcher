import re
import os
import configparser
import pathlib

import common
from config import main_config, name_replacement, add_the, subtitle_removal, app_name
from io_utils import ensure_exist

def convert_desktop(path):
	parser = configparser.ConfigParser(interpolation=None)
	parser.optionxform = str #Can you actually fuck off?
	parser.read(path)
	return {section: {k: v for k, v in parser.items(section)} for section in parser.sections()}

def get_field(desktop, name):
	entry = desktop['Desktop Entry']
	if name in entry:
		return entry[name]

	return None

def get_array(desktop, name):
	field = get_field(desktop, name)
	if field is None:
		return []

	return field.split(';')

remove_brackety_things_for_filename = re.compile(r'[]([)]')
clean_for_filename = re.compile(r'[^A-Za-z0-9_]')
def make_filename(name):
	name = name.lower()
	name = remove_brackety_things_for_filename.sub('', name)
	name = clean_for_filename.sub('-', name)
	while name.startswith('-'):
		name = name[1:]
	if not name:
		name = 'blank'
	return name

used_filenames = []
def base_make_desktop(command, display_name, fields=None, icon=None):
	base_filename = make_filename(display_name)
	filename = base_filename + '.desktop'

	i = 0
	while filename in used_filenames:
		filename = base_filename + str(i) + '.desktop'
		i += 1

	path = os.path.join(main_config.output_folder, filename)
	used_filenames.append(filename)

	configwriter = configparser.ConfigParser(interpolation=None)
	configwriter.optionxform = str

	configwriter.add_section('Desktop Entry')
	desktop_entry = configwriter['Desktop Entry']

	#Necessary for this thing to even be recognized
	desktop_entry['Type'] = 'Application'
	desktop_entry['Encoding'] = 'UTF-8'

	desktop_entry['Name'] = display_name
	desktop_entry['Exec'] = command

	if icon:
		if isinstance(icon, str):
			desktop_entry['Icon'] = icon
		else: #assume PIL/Pillow image
			if main_config.icon_folder:
				pathlib.Path(main_config.icon_folder).mkdir(exist_ok=True, parents=True)
				icon_path = os.path.join(main_config.icon_folder, filename + '.png')
				icon.save(icon_path, 'png')
				desktop_entry['Icon'] = icon_path

	metadata_section_name = 'X-%s Metadata' % app_name
	configwriter.add_section(metadata_section_name)
	metadata_section = configwriter[metadata_section_name]

	if fields:
		for k, v in fields.items():
			if v is None:
				continue

			if isinstance(v, list):
				if not v:
					continue
				value_as_string = ';'.join(['None' if item is None else item for item in v])
			else:
				value_as_string = str(v)

			metadata_section[k.replace('_', '-')] = value_as_string

	ensure_exist(path)
	with open(path, 'wt') as f:
		configwriter.write(f)

	#Set executable, but also set everything else because whatever
	os.chmod(path, 0o7777)

def make_display_name(name):
	display_name = common.remove_filename_tags(name)

	for replacement in name_replacement:
		display_name = re.sub(r'(?<!\w)' + re.escape(replacement[0]) + r'(?!\w)', replacement[1], display_name, flags=re.I)
	for replacement in add_the:
		display_name = re.sub(r'(?<!The )' + re.escape(replacement), 'The ' + replacement, display_name, flags=re.I)
	for replacement in subtitle_removal:
		display_name = re.sub(r'^' + re.escape(replacement[0]) + r'(?!\w)', replacement[1], display_name, flags=re.I)

	return display_name

def make_launcher(command, name, metadata, other_fields=None, icon=None):
	display_name = make_display_name(name)
	filename_tags = common.find_filename_tags.findall(name)
	fields = metadata.to_launcher_fields()
	fields['Filename-Tags'] = [tag for tag in filename_tags if tag not in metadata.ignored_filename_tags]
	fields['Original-Name'] = name
	if other_fields:
		fields.update(other_fields)
	#For very future use, this is where the underlying host platform is abstracted away. make_launcher is for everything, base_make_desktop is for Linux .desktop files specifically. Perhaps there are other things that could be output as well.
	base_make_desktop(command, display_name, fields, icon)

def _get_existing_launchers():
	a = []

	output_folder = main_config.output_folder
	if not os.path.isdir(output_folder):
		return []
	for name in os.listdir(output_folder):
		path = os.path.join(output_folder, name)

		existing_launcher = convert_desktop(path)
		existing_type = get_field(existing_launcher, 'X-Type')
		existing_id = get_field(existing_launcher, 'X-Unique-ID')
		a.append((existing_type, existing_id))

	return a
_existing_launchers = None

def has_been_done(game_type, game_id):
	global _existing_launchers #Of course it's global you dicktwat. I swear to fuck this fucking language sometimes, I just wanted to lazy initialize a variable why do you have to make this difficult by making me put spooky keywords in there or forcing me to write some boilerplate shit involving classes and decorators instead, if I wanted to write verbose bullshit I'd program in fucking Java, fuck off
	if _existing_launchers is None:
		_existing_launchers = _get_existing_launchers()

	for existing_type, existing_id in _existing_launchers:
		if existing_type == game_type and existing_id == game_id:
			return True

	return False
