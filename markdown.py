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
	content = content.replace('\r\n', '\n')

	content = re.sub(
		r'\[(.{1,}?)\]\(([\w\-.\/:?=#;&]+)\)',
		matdown_href + r'\1' + matdown_reset,
		content
	)  # anchors
	content = re.sub(
		r'(?<!["\w])(https?:\/\/[\w\-.]{1,})(?<!["\w])',
		matdown_href + r'\1' + matdown_reset,
		content
	)  # normal link
	content = re.sub(
		r'```(\w+|)\n?([\0-\255]+)```',
		matdown_href + r'\2' + matdown_reset,
		content
	)
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


def matdown_to_pango(content):
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
