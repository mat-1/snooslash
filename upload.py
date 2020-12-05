from simple_youtube_api.LocalVideo import LocalVideo
from simple_youtube_api.Channel import Channel
from datetime import datetime, timedelta
import json


def get_upload_time():
	epoch = datetime(1970, 1, 1)
	now = datetime.utcnow()
	with open('publish_day.txt', 'r') as f:
		publish_day = f.read()

	if not publish_day:
		publish_day = (now - epoch).days + 1
	else:
		publish_day = int(publish_day)
		if publish_day < (now - epoch).days + 1:
			publish_day = (now - epoch).days + 1
	publish_datetime = datetime.fromtimestamp(publish_day * 86400)
	publish_datetime -= timedelta(hours=6) # upload at midday cst
	strftime = publish_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
	return strftime

def increase_upload_time():
	epoch = datetime(1970, 1, 1)
	now = datetime.utcnow()
	with open('publish_day.txt', 'r') as f:
		publish_day = f.read()

	if not publish_day:
		publish_day = (now - epoch).days + 1
	else:
		publish_day = int(publish_day)
		if publish_day < (now - epoch).days + 1:
			publish_day = (now - epoch).days + 1
	publish_day += 1
	with open('publish_day.txt', 'w') as f:
		f.write(str(publish_day))

	

# loggin into the channel
channel = Channel()
channel.login('client_secret.json', 'credentials.storage')

# setting up the video that is going to be uploaded
video = LocalVideo(file_path='video.mp4')

# setting snippet

tags = ['reddit', 'rslash', 'story', 'storytime', 'nosleep', 'r/', 'snoo/', 'snooslash', 'reddit storytime', 'entitledparents', 'tifu', 'maliciouscompliance', 'reddit funny', 'top posts', 'comedy', 'best of reddit', 'funny', 'top posts of r/', 'reddit stories', 'askreddit', 'toadfilms', 'giofilms', '\\r', '/r', 'sub', 'subreddit', 'stories', 'memes', 'reddit story', 'cowbelly', 'updoot', 'sir reddit']

with open('post.json', 'r') as f:
	post_data = json.loads(f.read())

with open('description.txt', 'r') as f:
	description = f.read()

print('Original Subreddit:', post_data['subreddit_name_prefixed'])
print('Original Reddit title:', post_data['title'])
title = input('Enter YouTube post title: ')
video.set_title(title)
video.set_description(description)
video.set_tags(tags)
video.set_category('people')
video.set_default_language('en-US')

video.set_publish_at(get_upload_time())

# setting status
video.set_embeddable(True)
video.set_privacy_status('unlisted')
video.set_public_stats_viewable(True)

# setting thumbnail
video.set_thumbnail_path('thumbnail.png')

# uploading video and printing the results
video = channel.upload_video(video)
print(video.id)
print(video)

# liking video
video.like()

increase_upload_time()