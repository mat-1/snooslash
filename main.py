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

subreddits = [
	'nosleep',
	'entitledparents',
	'tifu',
	'maliciouscompliance',
	'talesfromtechsupport',
	'TalesFromRetail'
]


print('Recommended subreddits to look at: ')
for subreddit in subreddits:
	print(f'- r/{subreddit}')
post_id = extract_id(
	input('Enter Reddit post url or id > ')
)

v = video.RedditVideo(post_id=post_id)

print('Saved at', os.path.dirname(__file__))
input()
