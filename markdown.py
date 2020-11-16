from PIL import Image, ImageDraw, ImageFont
import re


matdown_reset = chr(1000000)
matdown_href = chr(1000001)
matdown_monospace = chr(1000002)
matdown_quote = chr(1000003)
matdown_bold = chr(1000004)
matdown_italic = chr(1000005)
matdown_h1 = chr(1000006)
matdown_h2 = chr(1000007)
matdown_h3 = chr(1000008)
matdown_hr = chr(1000009)

matdown_conversions = {
	matdown_href: r'<span foreground="#4fbcff">\1</span>',
	matdown_monospace: r'<code>\1</code>',
	matdown_quote: r'<i>\1</i>',
	matdown_bold: r'<b>\1</b>',
	matdown_italic: r'<i>\1</i>',
	matdown_h1: r'<span size="2048">\1</span>',
	matdown_h2: r'<span size="1536">\1</span>',
	matdown_h3: r'<span size="1198">\1</span>',
	matdown_hr: r'<span size="1198">\1</span>'
}


# matdown: the best markup language:tm:
def markdown_to_matdown(content):
	content = re.sub(
		r'\[(.+?)\]\(([\w\-.\/:?=#;&]+)\)',
		matdown_href + r'\1' + matdown_reset,
		content
	)  # anchors

	# [Hollow.](https://www.reddit.com/r/nosleep/comments/jrkyr8/im_a_dentist_for_monsters_the_baby_and_the_beast/?utm_source=share&amp;utm_medium=ios_app&amp;utm_name=iossmf)
	# content = re.sub(
	# 	r'(?<!["\w])(https?:\/\/[\w\-.]{1,})(?<!["\w])',
	# 	matdown_href + r'\1' + matdown_reset,
	# 	content
	# )  # normal link
	# content = re.sub(
	# 	r'```(\w+|)\n?([\0-\255]+)```',
	# 	matdown_href + r'\2' + matdown_reset,
	# 	content
	# )
	content = re.sub(r'`(.{1,}?)`', matdown_monospace + r'\1' + matdown_reset, content)
	content = re.sub(r'^&gt; (.{1,}?)\n', matdown_quote + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'\*\*(.{1,}?)\*\*', matdown_bold + r'\1' + matdown_reset, content)
	content = re.sub(r'\*(.{1,}?)\*', matdown_italic + r'\1' + matdown_reset, content)
	content = re.sub(r'^# (.+)\n', matdown_h1 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'^## (.+)\n', matdown_h2 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'^### (.+)\n', matdown_h3 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'^#### (.+)\n', matdown_h3 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'^##### (.+)\n', matdown_h3 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'^###### (.+)\n', matdown_h3 + r'\1' + matdown_reset, content, flags=re.MULTILINE)
	content = re.sub(r'\n([-_*])\1{2,}\n', matdown_hr, content)

	return content


def matdown_to_markdown(content):
	current_matdown = None
	output = ''
	content += matdown_reset
	for character in content:
		if (
			(current_matdown and character == matdown_reset)
			or (current_matdown and character in matdown_conversions)
		):
			if not current_matdown: current_matdown = character
			pango_open, pango_close = matdown_conversions[current_matdown].split(r'\1')
			output += pango_close
			current_matdown = None
		elif character in matdown_conversions:
			pango_open, pango_close = matdown_conversions[character].split(r'\1')
			output += pango_open
			current_matdown = character
		elif character != matdown_reset:
			output += character

	return output


def matdown_to_plaintext(content):
	output = ''
	for character in content:
		if character not in matdown_conversions and character != matdown_reset:
			output += character

	output = output\
		.replace('&gt;', '>')\
		.replace('&lt;', '<')
	return output


font_24 = ImageFont.truetype('NotoSans-Regular.ttf', 24)

fonts = {
	24: font_24
}


def wrap_text(text, line_length, font=None):
	output = ''
	current_line_length = 0

	for word in text.split(' '):
		word = word + ' '
		word_length = font.getsize(word)[0]
		new_line_length = current_line_length + word_length
		if '\n' in word:
			current_line_length = 0
		while word_length > line_length:
			output += word[:30] + '\n'
			word = word[30:]
			word_length = font.getsize(word)[0]
		if new_line_length > line_length:
			output = output.strip()
			output += '\n'
			current_line_length = 0
		current_line_length += font.getsize(word)[0]
		output += word.lstrip(' ')
	return output.strip()

def matdown_to_pages(content, width=1280, height=720):
	pages = []
	current_x = 0
	current_y = 0

	current_effect = None

	text_size = 24

	current_page = ''

	for i, char in enumerate(content):
		current_font = fonts[text_size]
		if char == matdown_reset:
			current_effect = None
			current_page += char
		elif char in {
			matdown_href, matdown_monospace, matdown_quote, matdown_bold, matdown_italic, matdown_h1, matdown_h2, matdown_h3,
			matdown_hr
		}:
			current_effect = char
			current_page += char
		elif char == '\n':
			current_x = 0
			current_y += text_size * 1.5
			current_page += char
		elif char == ' ':
			next_word = content[i + 1:].split(' ')[0].strip(' .!?')
			char_width, char_height = current_font.getsize(char)
			word_width, word_height = current_font.getsize(next_word)
			if current_x + word_width >= width:
				current_x = 0
				current_y += text_size * 1.5
			else:
				current_x += char_width
			current_page += ' '
		else:
			char_width, char_height = current_font.getsize(char)
			if current_x + char_width >= width:
				current_x = 0
				current_y += text_size * 1.5
			current_page += char
			current_x += char_width
		if current_y >= height:
			pages.append(current_page)
			current_page = ''
			current_y = 0

	pages.append(current_page)
	return pages


def matdown_to_pillow(content, width=1280, height=720):
	im = Image.new('RGBA', (width, height))

	d = ImageDraw.Draw(im)

	current_x = 0
	current_y = 0

	current_effect = None

	text_size = 24

	for i, char in enumerate(content):
		current_font = fonts[text_size]
		if char == matdown_reset:
			current_effect = None
		elif char in {
			matdown_href, matdown_monospace, matdown_quote, matdown_bold, matdown_italic, matdown_h1, matdown_h2, matdown_h3,
			matdown_hr
		}:
			current_effect = char
		elif char == '\n':
			current_x = 0
			current_y += text_size * 1.5
		elif char == ' ':
			next_word = content[i + 1:].split(' ')[0]
			char_width, char_height = current_font.getsize(char)
			word_width, word_height = current_font.getsize(next_word)
			if current_x + word_width >= width:
				current_x = 0
				current_y += text_size * 1.5
			else:
				current_x += char_width
		else:
			current_color = '#ffffff'

			if current_effect == matdown_href: current_color = '#4fbcff'

			char_width, char_height = current_font.getsize(char)
			if current_x + char_width >= width:
				current_x = 0
				current_y += text_size * 1.5
			d.text((current_x, current_y), char, font=current_font, fill=current_color)
			current_x += char_width

	return im
