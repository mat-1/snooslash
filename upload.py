from simple_youtube_api.LocalVideo import LocalVideo
from simple_youtube_api.Channel import Channel
import json

# loggin into the channel
channel = Channel()
channel.login('client_secret.json', 'credentials.storage')

# setting up the video that is going to be uploaded
video = LocalVideo(file_path="video.mp4")

# setting snippet

with open('post.json', 'r') as f:
	post_data = json.loads(f.read())

with open('description.txt', 'r') as f:
	description = f.read()

print('Original Subreddit:', post_data['subreddit_name_prefixed'])
print('Original Reddit title:', post_data['title'])
title = input('Enter YouTube post title: ')
video.set_title(title)
video.set_description(description)
video.set_tags(['snooslash', 'reddit', 'reddit r/'])
video.set_category('gaming')
video.set_default_language('en-US')

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