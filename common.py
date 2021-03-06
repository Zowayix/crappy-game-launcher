import importlib.resources
import json
import math
import re

find_brackets = re.compile(r'(?:\([^)]+?\)+|\[[^]]+?\]+)')
find_brackets_at_end = re.compile(r'(?:\([^)]+?\)+|\[[^]]+?\]+)$')

def _find_tags(name):
	#Where did I come up with the word "tags" anyway
	result = name
	tags = []
	while True:
		search = find_brackets_at_end.search(result)
		if not search:
			break
		tags.append(search[0])
		start = search.span()[0]
		result = result[:start]
		if not result:
			#Handle the whole name being (all in parentheses)
			return name, []
		if result[-1] == ' ':
			result = result[:-1]
	return result, tags[::-1]

def find_filename_tags_at_end(name):
	return _find_tags(name)[1]

def remove_filename_tags(name):
	return _find_tags(name)[0]

words_regex = re.compile(r'[\w()]+')
apostrophes_at_word_boundary_regex = re.compile(r"\B'|'\B")
def normalize_name(name, care_about_spaces=True, normalize_words=True, care_about_numerals=False):
	if care_about_numerals:
		name = convert_roman_numerals_in_title(name)
	name = name.lower()
	name = name.replace('3-d', '3d')
	name = name.replace('&', 'and')
	name = name.replace('é', 'e')
	name = name.replace(': ', ' - ')
	name = apostrophes_at_word_boundary_regex.sub('', name)

	if normalize_words:
		return ('-' if care_about_spaces else '').join(words_regex.findall(name))
	return name
	
def starts_with_any(s, prefixes):
	#Allows s.startswith() with any iterable, not just tuple
	for prefix in prefixes:
		if s.startswith(prefix):
			return True
	return False

class NotAlphanumericException(Exception):
	pass

def convert_alphanumeric(byte_array):
	string = ''
	for byte in byte_array:
		char = chr(byte)
		if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
			raise NotAlphanumericException(char)
		string += char
	return string

junk_suffixes = re.compile(r'((?:(?:,)? (?:Inc|LLC|Kft)|(?:Co\.)?(?:,)? Ltd|Corp|GmbH)(?:\.)?|Co\.)$')

def pluralize(n, singular, plural=None):
	if not plural:
		plural = singular + 's'
	if n == 1:
		return singular
	return '%d %s' % (n, plural)

def convert_roman_numeral(s):
	s = s.upper()

	units = {
		'M': (1000, 4),
		'D': (500, 3.5),
		'C': (100, 3),
		'L': (50, 2.5),
		'X': (10, 2),
		'V': (5, 1.5),
		'I': (1, 1),
	}
	value = 0
	i = 0
	while i < len(s):
		c = s[i]
		if c not in units:
			raise ValueError('Invalid char: ' + c)
		char_value, unit_index = units[c]

		if i + 1 < len(s):
			next_char = s[i + 1]
			if next_char not in units:
				raise ValueError('Invalid char: ' + next_char)
			next_char_value, next_unit_index = units[next_char]
			if next_unit_index == unit_index + 1 or (int(next_unit_index) == unit_index and next_unit_index != unit_index):
				#Subtractive notation thingo
				#IV and IX are valid, but VX is not valid, probably
				value += (next_char_value - char_value)
				i += 2
				continue
			if unit_index < next_unit_index:
				raise ValueError('Numerals out of order: ' + c + ', ' + next_char)
		value += char_value
		i += 1
	return value

def is_roman_numeral(s):
	try:
		convert_roman_numeral(s)
		return True
	except ValueError:
		return False

def convert_roman_numerals_in_title(s):
	words = s.split(' ')
	converted_words = []
	for word in words:
		actual_word_match = re.match('[A-Za-z]+', word)
		if not actual_word_match:
			converted_words.append(word)
			continue
		span_start, span_end = actual_word_match.span()
		prefix_punctuation = word[:span_start]
		suffix_punctuation = word[span_end:]
		actual_word = actual_word_match[0]

		try:
			converted_words.append(prefix_punctuation + str(convert_roman_numeral(actual_word)) + suffix_punctuation)
		except ValueError:
			converted_words.append(word)
	return ' '.join(converted_words)

def title_word(s):
	#Like str.title or str.capitalize but actually bloody works how I expect for compound-words and contract'ns
	actual_word_parts = re.split(r"([\w']+)", s)
	return ''.join([part.capitalize() for part in actual_word_parts])

dont_capitalize_these = ['the', 'a', 'an', 'and', 'or', 'at', 'with', 'to', 'of', 'is']
def title_case_sentence_part(s, words_to_ignore_case=None):
	words = re.split(' ', s)
	if not words_to_ignore_case:
		words_to_ignore_case = []

	titled_words = []
	titled_words.append(words[0] if words[0] in words_to_ignore_case else title_word(words[0]))
	words = words[1:]
	for word in words:
		if word in words_to_ignore_case or is_roman_numeral(word):
			titled_words.append(word)
		elif word.lower() in dont_capitalize_these:
			titled_words.append(word.lower())
		else:
			titled_words.append(title_word(word))
	return ' '.join(titled_words)

def title_case(s, words_to_ignore_case=None):
	sentence_parts = re.split(r'(\s+-\s+|:\s+)', s)
	titled_parts = [title_case_sentence_part(part, words_to_ignore_case) for part in sentence_parts]
	return ''.join(titled_parts)

def remove_capital_article(s):
	if not s:
		return ''

	words = s.split(' ')
	new_words = [words[0]]
	for word in words[1:]:
		if word.lower() in ('the', 'a'):
			new_words.append(word.lower())
		else:
			new_words.append(word)
	return ' '.join(new_words)

def clean_string(s):
	return ''.join([c for c in s if c.isprintable()])

def byteswap(b):
	if len(b) % 2 == 0:
		bb = b
	else:
		bb = b[:-1]
	last_byte = b[-1]
	byte_array = bytearray(bb)
	byte_array[0::2] = bb[1::2]
	byte_array[1::2] = bb[0::2]
	if len(b) % 2 != 0:
		byte_array.append(last_byte)
	return bytes(byte_array)

dict_line_regex = re.compile(r'(?P<kquote>\'|\"|)(?P<key>.+?)(?P=kquote):\s*(?P<vquote>\'|\")(?P<value>.+?)(?P=vquote),?(?:\s*#.+)?$')
def load_dict(subpackage, resource):
	d = {}
	package = 'data'
	if subpackage:
		package += '.' + subpackage
	for line in importlib.resources.read_text(package, resource + '.dict').splitlines():
		if line.startswith('#'):
			continue
		match = dict_line_regex.match(line)
		if match:
			key = match['key']
			if not match['kquote']:
				key = int(key)
			d[key] = match['value']
	return d

def load_list(subpackage, resource):
	package = 'data'
	if subpackage:
		package += '.' + subpackage
	return [line for line in [line.split('#', 1)[0] for line in importlib.resources.read_text(package, resource + '.list').splitlines()] if line]

def load_json(subpackage, resource):
	package = 'data'
	if subpackage:
		package += '.' + subpackage
	with importlib.resources.open_binary(package, resource) as f: #It would be text, but I don't know if I wanna accidentally fuck around with encodings
		return json.load(f)

def _format_unit(n, suffix, base_unit=1000, singular_suffix=None):
	try:
		if n < base_unit:
			return '{0} {1}'.format(n, singular_suffix if singular_suffix else suffix)
	except TypeError:
		return n
	
	exp = int(math.log(n, base_unit))
	unit_suffix = 'KMGTPE'[exp - 1]
	d = round(n / math.pow(base_unit, exp), 2)
	return '{0} {1}{2}'.format(d, unit_suffix, suffix)

def format_byte_size(b, metric=True):
	return _format_unit(b, 'B' if metric else 'iB', 1000 if metric else 1024, 'bytes')
