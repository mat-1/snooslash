import video

def extract_id(url):
	url_parts = url.strip('/').split('/')
	comments_index = url_parts.index('comments')
	if comments_index:
		return url_parts[comments_index + 1]
	else:
		# the input was probably an id anyway
		return url_parts[-1]


post_id = extract_id('https://www.reddit.com/comments/k211no')

v = video.RedditVideo(post_id=post_id)
