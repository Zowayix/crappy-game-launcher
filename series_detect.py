#!/usr/bin/env python3
import datetime
import os
import re
import time

import launchers
from common import (convert_roman_numeral, convert_roman_numerals_in_title,
                    remove_capital_article)
from config.main_config import main_config
from data.series_detect.series_detect_overrides import series_overrides

probably_not_series_index_threshold = 20
#Assume that a number over this is probably not referring to the nth or higher entry in the series, but is probably just any old number that means something else
probably_not_a_series_index = ('XXX', '007', 'DX', 'XL', 'V3') #V3 shouldn't be detected as some weird mix of Roman and Arabic numerals anyway…
#These generally aren't entries in a series, and are just there at the end
suffixes_not_part_of_series = ('64', 'Advance', '3D', 'DS')
#If these are appended to a series it's just part of that same series and not a new one, if that makes sense, see series_match

series_matcher = re.compile(r'(?P<Series>.+?)\b\s+#?(?P<Number>\d{1,3}|[IVXLCDM]+?)\b(?:\s|$)')
chapter_matcher = re.compile(r'\b(?:Chapter|Vol|Volume|Episode|Part|Version)\b(?:\.)?', flags=re.RegexFlag.IGNORECASE)
#"Phase", "Disk" might also be chapter marker things?
subtitle_splitter = re.compile(r'\s*(?:\s+-\s+|:\s+|\s+\/\s+)')
blah_in_1_matcher = re.compile(r'.+\s+in\s+1')

def get_name_chunks(name):
	name_chunks = subtitle_splitter.split(name)
	name_chunks = [blah_in_1_matcher.sub('', chunk) for chunk in name_chunks]
	name_chunks = [chunk for chunk in name_chunks if chunk]
	return name_chunks

def find_series_from_game_name(name):
	if name in series_overrides:
		return series_overrides[name]
	name_chunks = get_name_chunks(name)
	if not name_chunks:
		return None, None
	name_chunk = name_chunks[0]
	series_match = series_matcher.fullmatch(name_chunk)
	if series_match:
		series_name = series_match['Series']
		series_name.removeprefix('The ')
		series_name = remove_capital_article(series_name)
		number = series_match['Number']
		if number in probably_not_a_series_index:
			return None, None

		try:
			number = int(number)
		except ValueError:
			try:
				number = convert_roman_numeral(number)
			except ValueError:
				#Not actually a roman numeral, chief
				return None, None

		if number > probably_not_series_index_threshold:
			return None, None
		return chapter_matcher.sub('', series_name).rstrip(), number
	return None, None

def does_series_match(name_to_match, existing_series):
	name_to_match = name_to_match.lower()
	existing_series = existing_series.lower()

	name_to_match.removeprefix('the ')

	for suffix in suffixes_not_part_of_series:
		name_to_match = name_to_match.removesuffix(' ' + suffix)

	#Might also want to remove punctuation

	return name_to_match == existing_series

def find_series_name_by_subtitle(name, existing_serieses, force=False):
	name_chunks = get_name_chunks(name)
	if not name_chunks:
		return None, None
	name_chunk = name_chunks[0]

	match = None
	
	if force:
		match = name_chunk
	else:
		for existing_series in existing_serieses:
			if does_series_match(name_chunk, existing_series):
				match = existing_series
				break

	if match:
		series = remove_capital_article(match)
		index = None
		if len(name_chunks) > 1:
			index = name_chunks[1]
		else:
			index = '1'
		return series, index
	return None, None

def get_usable_name(desktop):
	sort_name = launchers.get_field(desktop, 'Sort-Name')
	if sort_name:
		return sort_name
	#Note that this is before disambiguate.py, so we don't need to worry about using Ambiguous-Name from disambiguation section
	#Name _must_ exist in a .desktop file... although this is platform-specific, come to think of it, maybe I should put stuff in launchers.py to abstract getting name/exec/icon/etc
	return launchers.get_field(desktop, 'Name', 'Desktop Entry')

def add_series(desktop, path, series, series_index=None):
	if launchers.metadata_section_name not in desktop:
		desktop.add_section(launchers.metadata_section_name)
	if series is not None:
		desktop[launchers.metadata_section_name]['Series'] = series
	if series_index is not None:
		desktop[launchers.metadata_section_name]['Series-Index'] = str(series_index)
	with open(path, 'wt') as f:
		desktop.write(f)

def detect_series(desktop, path):
	name = get_usable_name(desktop)
	series, series_index = find_series_from_game_name(name)
	if series:
		add_series(desktop, path, series, series_index)

def find_existing_serieses():
	serieses = set()
	for name in os.listdir(main_config.output_folder):
		path = os.path.join(main_config.output_folder, name)
		desktop = launchers.get_desktop(path)

		series = launchers.get_field(desktop, 'Series')
		if series:
			serieses.add(series)

	return serieses

def detect_series_by_subtitle(desktop, path, existing):
	name = get_usable_name(desktop)
	series, index = find_series_name_by_subtitle(name, existing)
	if series:
		add_series(desktop, path, series, index)

def force_add_series_with_index(desktop, path, existing):
	name = get_usable_name(desktop)
	series, _ = find_series_name_by_subtitle(name, existing, force=True)
	if series:
		add_series(desktop, path, series)

def get_series_from_whole_thing(series, whole_name):
	rest = whole_name.removeprefix(series).strip()
	rest = chapter_matcher.sub('', rest).strip()

	if rest:
		if rest not in probably_not_a_series_index:
			#Don't convert things that aren't actually roman numerals
			try:
				rest = str(convert_roman_numeral(rest))
			except ValueError:
				pass
			return convert_roman_numerals_in_title(rest)
		return rest
	
	return '1'

def detect_series_index_for_things_with_series():
	for filename in os.listdir(main_config.output_folder):
		path = os.path.join(main_config.output_folder, filename)
		desktop = launchers.get_desktop(path)

		existing_series = launchers.get_field(desktop, 'Series')
		if not existing_series:
			continue

		if launchers.get_field(desktop, 'Series-Index'):
			continue

		name = get_usable_name(desktop)
		name.removeprefix('The ')
		name_chunks = get_name_chunks(name)
		if len(name_chunks) > 1:
			if name_chunks[0] == existing_series:
				series_index = name_chunks[1]
				series_index = chapter_matcher.sub('', series_index).strip()
				series_index = convert_roman_numerals_in_title(series_index)
				add_series(desktop, path, None, series_index)
			elif name_chunks[0].startswith(existing_series):
				series_index = get_series_from_whole_thing(existing_series, name_chunks[0].strip())
				add_series(desktop, path, None, series_index)
			else:
				#This handles the case where it's like "Blah Bloo - Chapter Zabityzoo" but the series in Steam is listed as some abbreviation/alternate spelling of Blah Bloo so it doesn't get picked up otherwise
				chapter_index = None
				try:
					chapter_index = name.index('Ch.') + len('Ch.')
				except ValueError:
					chapter_matcherooni = chapter_matcher.search(name)
					if chapter_matcherooni:
						chapter_index = chapter_matcherooni.end()
				if chapter_index is not None:
					#Could also do just a word match starting from chapter_index I guess
					add_series(desktop, path, None, convert_roman_numerals_in_title(name[chapter_index:].strip()))
		elif len(name_chunks) == 1:
			if name_chunks[0].startswith(existing_series):
				add_series(desktop, path, None, get_series_from_whole_thing(existing_series, name_chunks[0].strip()))

def get_existing_seriesless_launchers():
	for name in os.listdir(main_config.output_folder):
		path = os.path.join(main_config.output_folder, name)
		desktop = launchers.get_desktop(path)

		if launchers.get_field(desktop, 'Series'):
			#Don't need to do this if it already exists
			continue

		yield desktop, path

def detect_series_for_all_desktops():
	time_started = time.perf_counter()

	for desktop, path in get_existing_seriesless_launchers():
		detect_series(desktop, path)
	existing = find_existing_serieses()
	for desktop, path in get_existing_seriesless_launchers():
		detect_series_by_subtitle(desktop, path, existing)

	for desktop, path in get_existing_seriesless_launchers():
		if launchers.get_field(desktop, 'Series-Index'):
			force_add_series_with_index(desktop, path, existing)

	detect_series_index_for_things_with_series()

	if main_config.print_times:
		time_ended = time.perf_counter()
		print('Series detection finished in', str(datetime.timedelta(seconds=time_ended - time_started)))

if __name__ == '__main__':
	detect_series_for_all_desktops()
