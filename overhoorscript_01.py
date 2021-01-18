import os


def remove_wrongstarts(rawline):
	if rawline.startswith('-'):
		rawline = rawline[1:len(rawline)]
	for i in range(9):
		if rawline.startswith(str(i+1)):
			rawline = rawline[1:len(rawline)]
	if rawline.startswith('.'):
		rawline = rawline[1:len(rawline)]
	if rawline.startswith(' '):
		rawline = rawline[1:len(rawline)]

	return rawline

def fix_strangecharacters(source):
	source = source.replace('â€™', "'")
	return source

def get_raw_split(line):
	term = ''
	line = remove_wrongstarts(line)
	splitline = line.split(':')
	if len(splitline) > 1:
		if len(splitline) > 2:
			def_seg = ':'.join(splitline[2:len(splitline)])
		else:
			def_seg = splitline[-1]

		def_seg = remove_wrongstarts(def_seg)
		term = splitline[0]
	else:
		def_seg = splitline[0]

	term = fix_strangecharacters(term)
	def_seg = fix_strangecharacters(def_seg)

	return term, def_seg

def unusable_line(line):
	if line.endswith(':'):
		return True

def get_content():
	fpath = r"D:\Dropbox\Documents\marketing_samenvatting_h4.txt"
	f = open(fpath)
	term_dict = {}

	i = 0
	prev_def_seg = None
	for line in f:
		if unusable_line(line):
			continue

		c_term, def_seg = get_raw_split(line)

		if not c_term:
			realterm = None
			if prev_def_seg:
				prev_def_seg += def_seg
			else:
				prev_def_seg = def_seg

			prev_def_seg = ' '.join(prev_def_seg.splitlines())
		else:
			# if no term in this line, that means the previous definition is complete.
			# therefore, enter it into the dict. 
			realterm = c_term
			if prev_def_seg:
				final_def = prev_def_seg
				term_dict[realterm] = final_def

			prev_def_seg = def_seg

		i += 1
		if i > 5:
			break

	print('dict:', term_dict)
	return term_dict

if __name__ == '__main__':
	content = get_content()
