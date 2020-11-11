from moviepy.config import change_settings
import moviepy.editor as mpy
from io import BytesIO
import markdown
import textwrap
import requests
import pyttsx3
import hashlib
import re

change_settings({'IMAGEMAGICK_BINARY': r'C:\\Program Files\\ImageMagick-7.0.10-Q16-HDRI\\magick.exe'})

tts = pyttsx3.init()

clips = []

width = 1280
height = 720


def generate_text_clip(text, read_text=None):
	read_text = read_text or text
	background_clip = mpy.ColorClip((width, height), color=(26, 26, 27))

	hashed_read_text = hashlib.md5(read_text.encode()).hexdigest()
	audio_filename = f'cache/{hashed_read_text}.mp3'

	tts.save_to_file(read_text, audio_filename)
	tts.runAndWait()
	print('saved to file :)', read_text)

	# text_wrapped = textwrap.fill(text, width // 16 - 2, replace_whitespace=False, drop_whitespace=False)

	text_clip = mpy.TextClip(
		markdown.matdown_to_pango(text),
		fontsize=24,
		font='NotoSans-Regular',
		color='white',
		align='east',
		method='pango',
		size=(width - 64 * 2, height)
	).set_position((64, 64))

	audio_clip = mpy.AudioFileClip(audio_filename)

	composite_text = mpy.CompositeVideoClip([background_clip, text_clip])
	composite_text = composite_text.set_audio(audio_clip)
	composite_text = composite_text.set_duration(audio_clip.duration)
	# composite_text = composite_text.set_duration(.1)

	return composite_text


def generate_large_text_clip(text):
	text = markdown.markdown_to_matdown(text)
	sentences_split = re.findall(r'(.+?)(?:( *[\.\?!][\'"\)\]]*[ \n]*)|$)', text)
	sentences = [sentence[0] + sentence[1] for sentence in sentences_split]
	displaying_text = ''
	clips = []
	for sentence in sentences[:10]:
		displaying_text += sentence
		clips.append(generate_text_clip(displaying_text, sentence))
	return mpy.concatenate_videoclips(clips)


def fetch_post(subreddit=None):
	if subreddit is None:
		subreddit = 'nosleep'
	r = requests.get(f'https://reddit.com/r/{subreddit}.json', headers={
		'user-agent': 'snooslash'
	})
	data = r.json()
	posts_list = data['data']['children']
	for post in posts_list:
		post = post['data']
		if post['locked']: continue
		elif post['stickied']: continue
		elif post['distinguished'] == 'moderator': continue
		return {
			'id': post['id'],
			'title': post['title'],
			'body': post['selftext']
		}


# md = markdown.markdown_to_matdown('[hello](https://world.com)')
# print(markdown.matdown_to_pango(md))

# exit()


post = fetch_post()
clips.append(generate_large_text_clip(post['body']))

final_clip = mpy.concatenate_videoclips(clips)

# final_clip = mpy.TextClip(
# 	'a<b>a</b>',
# 	fontsize=32,
# 	font='NotoSans-Regular',
# 	color='white',
# 	align='west',
# 	method='pango'
# ).set_position((64, 64)).set_duration(1)


final_clip.write_videofile('video.avi', fps=30, codec='mpeg4')
