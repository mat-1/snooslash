import reddit
import video
import os

def extract_id(url):
	url_parts = url.strip('/').split('/')
	if 'comments' in url_parts:
		comments_index = url_parts.index('comments')
		return url_parts[comments_index + 1]
	else:
		# the input was probably an id anyway
		return url_parts[-1]

print('Fetching post...')

post = reddit.fetch_post(min_length=2000)

title = post['title']
subreddit_name = post['subreddit_name_prefixed']

print(f'Generating video titled "{title}" from {subreddit_name}')

v = video.RedditVideo(reddit_data=post)

print('Saved at', os.path.dirname(__file__))
