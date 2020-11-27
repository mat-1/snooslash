from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.fx.all import audio_normalize
from moviepy.audio.fx.volumex import volumex
from PIL import Image, ImageDraw
from mutagen.wave import WAVE
from threading import Thread
import thumbnail
import functools
import markdown
import reddit
import random
import numpy
import cv2
import tts
import re
import os

class RedditVideo:
	def __init__(self, filename='video.mp4', video_type='post', reddit_data={}, size=(1280, 720), post_id=None, max_threads=10):
		self.size = size
		self.filename = filename
		self.fps = 24
		self.reddit_data = reddit_data if reddit_data else reddit.fetch_post(post_id=post_id)
		self.max_threads = max_threads

		filename_name_part, filename_ext_part = filename.split('.', 1)
		self.video_silent_filename = filename_name_part + '-silent.' + filename_ext_part
		self.video_audio_filename = filename_name_part + '-audio.mp3'

		fourcc = 0x7634706d  # mp4
		self.v = cv2.VideoWriter(
			'temp/' + self.video_silent_filename,
			fourcc,
			self.fps,
			self.size
		)

		self._create()

	def _write_frame(self, im):
		self._write_frames(im, 1)

	def _write_frames(self, im, times):
		cv2_frame = cv2.cvtColor(numpy.array(im), cv2.COLOR_RGB2BGR)
		for _ in range(times):
			self.v.write(cv2_frame)

	def _get_audio_length(self, filename):
		audio = WAVE(filename)
		return audio.info.length

	def _add_video_section(self, type, image, text=None):
		data = {
			'type': type,
			'image': image,
			'audio': None
		}
		duration = 0
		if text:
			tts_filename = tts.create_tts_file(text)
			duration = self._get_audio_length(tts_filename)
			data['text'] = text
			data['audio'] = tts_filename
		data['duration'] = duration

		self.video_sections.append(data)

	def _create_intro(self):
		thumbnail_im = thumbnail.generate_thumbnail(self.reddit_data)
		self.thumbnail_im = thumbnail_im
		self._add_video_section(
			'image',
			image=thumbnail_im,
			text=self.reddit_data['title']
		)

	def _create_post_part(self, content, new_content, author, page_number):
		im = Image.new('RGBA', self.size, (26, 26, 27))
		text_im = markdown.matdown_to_pillow(content, width=self.size[0]-100)
		d = ImageDraw.Draw(im)
		if page_number == 0:
			current_font = markdown.fonts[16]
			d.text((50, 16), f'Written by u/{author or "???"}', font=current_font, fill='#666666')

		im.paste(text_im, (50, 50), text_im)
		return {
			'image': im,
			'text': markdown.matdown_to_plaintext(new_content)
		}
		

	def _split_sentences(self, content):
		sentences_split = re.findall(r'(.+?)( *[\.\?!\n][\'"\)\]]*[ \n]*)', content)
		sentences = [sentence[0] + sentence[1] for sentence in sentences_split]
		return sentences

	def _gather_threads(self, functions):
		if len(functions) == 1:
			# no need to use threads if it's just one thing :)
			return [functions[0]()]
		results = {}
		threads = []

		for thread_id in range(len(functions)):
			def get_result(thread_id):
				nonlocal results
				function = functions[thread_id]
				result = function()
				results[thread_id] = result

			thread = Thread(None, get_result, args=(thread_id,))
			thread.start()
			threads.append(thread)
		results_list = []
		for thread_id, thread in enumerate(threads):
			thread.join()
			results_list.append(results[thread_id])
		return results_list


	def _create_post_body(self, content, author):
		# print('content', content)
		matdown_content = markdown.markdown_to_matdown(content)
		# print('matdown_content', matdown_content)
		content_pages = markdown.matdown_to_pages(matdown_content, self.size[0]-100, self.size[1]-100)
		# print(content_pages)
		functions = []
		for page_number, page in enumerate(content_pages):
			sentences = self._split_sentences(page)
			displaying_text_list = []

			for sentence in sentences:
				print('.', end='')
				displaying_text_list.append(sentence)
				displaying_text = ''.join(displaying_text_list)
				saying_text = markdown.matdown_to_plaintext(sentence)
				if not re.search('[a-zA-Z]', saying_text): continue
				post_part_function = functools.partial(
					self._create_post_part,
					displaying_text,
					saying_text,
					author=author,
					page_number=page_number
				)
				functions.append(post_part_function)
				if len(functions) >= self.max_threads:
					post_parts = self._gather_threads(functions)
					for post_part in post_parts:
						self._add_video_section(
							'image',
							image=post_part['image'],
							text=post_part['text']
						)
					functions = []
		if functions:
			post_parts = self._gather_threads(functions)
			for post_part in post_parts:
				self._add_video_section(
					'image',
					image=post_part['image'],
					text=post_part['text']
				)

	def _render(self):
		for section in self.video_sections:
			duration_frames = round(section['duration'] * self.fps)
			image = section['image']
			self._write_frames(image, duration_frames)
			print('.', end='', flush=True)
		
		print('pog?')
		self.v.release()

	def _add_audio(self):
		audio_clips = []
		t = 0
		for section in self.video_sections:
			if section['audio']:
				audio_clip = AudioFileClip(section['audio'])
				audio_clip = audio_clip.set_start(t)
				audio_clips.append(audio_clip)
			t += section['duration']

		music_clip = self._make_background_music_clip(t)
		audio_clips.append(music_clip)

		composite_audio_clip = CompositeAudioClip(audio_clips)
		composite_audio_clip.fps = None
		print('Writing complete audio file')
		composite_audio_clip.write_audiofile('temp/' + self.video_audio_filename)

		for audio_clip in audio_clips:
			audio_clip.close()

		composite_audio_clip.close()

	def _combine_video_audio(self):
		video_clip = VideoFileClip('temp/' + self.video_silent_filename)
		video_clip.write_videofile(self.filename, audio='temp/' + self.video_audio_filename)

	def _clear_temp_files(self):
		for f in os.listdir('temp'):
			os.remove(os.path.join('temp', f))

	def _select_song_file(self):
		songs = os.listdir('music')
		song_filename = random.choice(songs)
		print(song_filename)
		return 'music/' + song_filename


	def _make_background_music_clip(self, length):
		music_clips = []
		current_length = 0

		while length > current_length:
			song_filename = self._select_song_file()
			music_clip = AudioFileClip(song_filename)
			music_clips.append(music_clip.fx(audio_normalize).fx(volumex, 0.02))

			current_length = concatenate_audioclips(music_clips).duration

		return concatenate_audioclips(music_clips).set_end(length)

	def _make_description(self):
		lines = []
		title = self.reddit_data['title']
		url = 'https://reddit.com/comments/' + self.reddit_data['id']
		author = self.reddit_data['author']
		lines.append(f'"{title}"')
		lines.append('')
		lines.append(f'Original Reddit post: {url}')
		lines.append(f'Written by u/{author}')
		lines.append('')
		lines.append('')
		lines.append('')
		lines.append('')
		lines.append('SnooSlash source code: https://github.com/mat-1/snooslash/')
		description = '\n'.join(lines)
		with open('description.txt', 'w') as f:
			f.write(description)
		return description


	def _predict_length(self):
		length_in_seconds = 0
		if self.video_sections:
			length = 0
			for section in self.video_sections:
				length += section['duration']
			length_in_seconds = length
		if length_in_seconds > 120:
			return f'{length_in_seconds // 60} minutes'
		else:
			return f'{length_in_seconds // 1} seconds'



	def _create(self):
		print('Starting...')
		self.video_sections = []
		self._create_intro()
		self._create_post_body(
			self.reddit_data['body'],
			author=self.reddit_data['author']
		)

		print('\nPrepared how the video should look, now writing frames using Pillow.')
		print('Predicted output length:', self._predict_length())

		self._render()

		print('\nFinished writing frames! Now adding audio...')
		self._add_audio()
		print('\nFound good audio, adding to video...')
		self._combine_video_audio()
		print('\nClearing temp files...')
		self._clear_temp_files()
		print('\nCreating description...')
		self._make_description()
		print('\nFinished!')
