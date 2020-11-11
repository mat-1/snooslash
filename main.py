from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip, TextClip, ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.fx.volumex import volumex
from moviepy.config import change_settings

import moviepy.editor as mpy
import thumbnail
import markdown
import requests
import pyttsx3
import hashlib
import random
import re
import os


change_settings({'IMAGEMAGICK_BINARY': r'C:\\Program Files\\ImageMagick-7.0.10-Q16-HDRI\\magick.exe'})

tts = pyttsx3.init()

clips = []

width = 1280
height = 720

debugging = False


def generate_audio_tts_clip(text):
	print('saying', text)
	hashed_read_text = hashlib.md5(text.encode()).hexdigest()
	audio_filename = f'cache/{hashed_read_text}.mp3'

	tts.save_to_file(text, audio_filename)
	tts.runAndWait()

	audio_clip = AudioFileClip(audio_filename)

	return audio_clip


def generate_text_clip(text, read_text=None):
	read_text = read_text or text
	background_clip = ColorClip((width, height), color=(26, 26, 27))

	text_clip = TextClip(
		markdown.matdown_to_pango(text),
		fontsize=24,
		font='NotoSans-Regular',
		color='white',
		align='east',
		method='pango',
		size=(width - 64 * 2, height)
	).set_position((64, 64))

	audio_clip = generate_audio_tts_clip(read_text)

	composite_text = CompositeVideoClip([background_clip, text_clip])
	composite_text = composite_text.set_audio(audio_clip)
	composite_text = composite_text.set_duration(audio_clip.duration)

	audio_clip.coreader()

	return composite_text


def generate_large_text_clip(text):
	text = markdown.markdown_to_matdown(text)
	sentences_split = re.findall(r'(.+?)(?:( *[\.\?!][\'"\)\]]*[ \n]*)|$)', text)
	sentences = [sentence[0] + sentence[1] for sentence in sentences_split]
	displaying_text_list = []
	clips = []
	for sentence in sentences[:10] if debugging else sentences:
		displaying_text_list.append(sentence)
		if len(displaying_text_list) >= 50:
			displaying_text_list = [sentence]
		displaying_text = ''.join(displaying_text_list)
		saying_text = markdown.matdown_to_plaintext(sentence)
		if not re.search('[a-zA-Z]', saying_text): continue
		clips.append(generate_text_clip(displaying_text, saying_text))
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
			'body': post['selftext'],
			'score': post['score'],
			'subreddit_name_prefixed': post['subreddit_name_prefixed']
		}


def select_song_file():
	songs = os.listdir('music')
	song_filename = random.choice(songs)
	return 'music/' + song_filename


def make_background_music_clip(length):
	music_clips = []
	current_length = 0

	while length > current_length:
		song_filename = select_song_file()
		music_clip = AudioFileClip(song_filename)
		music_clips.append(music_clip)

		current_length = mpy.concatenate_audioclips(music_clips).duration

	return mpy.concatenate_audioclips(music_clips).fx(volumex, 0.2)


def generate_intro_clip(post):
	thumbnail.generate_thumbnail(post)
	intro_clip = ImageClip('thumbnail.png')
	audio_clip = generate_audio_tts_clip(post['title'])

	intro_clip = intro_clip.set_audio(audio_clip)
	intro_clip = intro_clip.set_duration(audio_clip.duration)

	audio_clip.coreader()

	return intro_clip


def make_reddit_clip(type='post'):
	post = fetch_post()

	clips = []

	clips.append(generate_intro_clip(post))
	clips.append(generate_large_text_clip(post['body']))

	final_clip_nomusic = mpy.concatenate_videoclips(clips)
	music_clip = make_background_music_clip(final_clip_nomusic.duration)

	final_audio = mpy.CompositeAudioClip([final_clip_nomusic.audio, music_clip]).set_end(final_clip_nomusic.duration)
	final_clip = final_clip_nomusic.set_audio(final_audio)
	return final_clip


print('Creating reddit clip :)')

final_clip = make_reddit_clip()

print('Writing video!')

final_clip.write_videofile('video.mp4', fps=1, preset='ultrafast')
