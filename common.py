import re

find_filename_tags = re.compile(r'(\([^)]+?\)+|\[[^]]+?\]+)')
remove_extra_spaces = re.compile(r'\s(?=\s|$)')
def remove_filename_tags(name):
	if name.startswith(('(', '[')) and name.endswith((')', ']')):
		return name	
	else:
		return remove_extra_spaces.sub('', find_filename_tags.sub('', name))

def starts_with_any(s, prefixes):
	#Allows s.startswith() with any iterable, not just tuple
	for prefix in prefixes:
		if s.startswith(prefix):
			return True
	return False
