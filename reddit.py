import requests


def fetch_post(subreddit=None):
	# return {
	# 	'id': 'abc',
	# 	'title': 'title',
	# 	'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce scelerisque urna quis maximus scelerisque. Vivamus convallis semper quam vel vestibulum. Donec in luctus lectus. Nunc tempus scelerisque enim, in porttitor sapien egestas non. Donec id varius enim. Sed nec consectetur nulla. Mauris vel cursus nisi.',
	# 	'score': 69420,
	# 	'subreddit_name_prefixed': 'r/snooslash'
	# }
	if subreddit is None:
		subreddit = 'nosleep'
	r = requests.get(f'https://www.reddit.com/r/{subreddit}.json', headers={
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