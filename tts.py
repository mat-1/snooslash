import hashlib
import pyttsx3
import os.path
import re

tts = pyttsx3.init()


def create_tts_file(text, volume=.4):
	if not re.search('[a-zA-Z]', text):
		# Doesn't have anything to say
		return
	hashed_read_text = hashlib.md5(text.encode()).hexdigest()
	audio_filename = f'temp/{hashed_read_text}.wav'
	if os.path.exists(audio_filename): 
		# already cached, no need to create it again!
		return audio_filename

	tts.setProperty('volume', volume)
	tts.save_to_file(text, audio_filename)
	tts.runAndWait()

	return audio_filename
