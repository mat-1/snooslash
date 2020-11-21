from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
import colorsys
import random
import io

default_size = (1280, 720)

upvote_im = Image.open('assets/upvote.png')
upvote_im = upvote_im.resize((100, 100))

downvote_im = upvote_im.rotate(180)

gold_im = Image.open('assets/gold.png')
gold_im = gold_im.resize((150, 150))

platinum_im = Image.open('assets/platinum.png')
platinum_im = platinum_im.resize((150, 150))

ibm_plex_sans_url = 'https://github.com/IBM/plex/blob/master/IBM-Plex-Sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf?raw=true'


def random_rainbow():
	h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
	r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
	return (r, g, b)


def load_font(url, size):
	font_data = requests.get(font_url).content
	font_raw = io.BytesIO(font_data)

	font = ImageFont.truetype(font_raw, size)
	return font


fonts = {
	'title': (
		ibm_plex_sans_url,
		100
	),
	'title2': (
		ibm_plex_sans_url,
		70
	),
}

for font_name in dict(fonts):
	font_url, font_size = fonts[font_name]
	font = load_font(font_url, font_size)
	fonts[font_name] = font


def wrap_text(text, line_length, font=None):
	output = ''
	current_line_length = 0

	font = fonts['title']

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


def generate_thumbnail(post):
	title = post['title']
	border_color = random_rainbow()
	im = Image.new('RGB', default_size)

	draw = ImageDraw.Draw(im)

	outline_width = 15
	im_width, im_height = im.size

	draw.rectangle(
		[
			0, 0,
			im_width, im_height
		],
		(0, 0, 0),
		border_color,
		width=outline_width
	)

	# title text
	font = fonts['title']

	title_font = fonts['title'] if len(title) < 100 else fonts['title2']

	lines = wrap_text(title, 850 if len(title) < 100 else 1500, title_font).split('\n')
	total_height = 0
	for line in lines:
		w, h = draw.textsize(line, title_font)
		total_height += h
	text_offset = ((720 - total_height) / 2) + 50

	for line in lines:
		draw.text((250, text_offset), line, fill='white', font=title_font, align='right')
		text_offset += title_font.getsize(line)[1]

	# upvotes
	if post['score'] >= 10000:
		upvote_count = str(int(post['score'] / 1000)) + 'k'
	elif post['score'] >= 1000:
		upvote_count = str(
			int(post['score'] // 100) / 10
		) + 'k'
	else:
		upvote_count = str(post['score'])
	w, h = draw.textsize(upvote_count, font)

	draw.text((125 - w // 2, 300), upvote_count, fill='#FF5700', font=font, align='center')

	# subreddit name
	draw.text((35, 25), post['subreddit_name_prefixed'], fill='#AAAAAA', font=font, align='left')

	# assets
	im.paste(upvote_im, (75, 200))
	im.paste(downvote_im, (75, 425))

	im.paste(platinum_im, (800, 35))
	im.paste(gold_im, (1000, 35))

	im.save('thumbnail.png')

	return im
