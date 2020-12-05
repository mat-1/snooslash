import requests
import random

user_agent = 'snooslash'

subreddits = [
	'nosleep',
	'entitledparents',
	'tifu',
	'maliciouscompliance',
	'talesfromtechsupport',
	'TalesFromRetail'
]


def read_post_ids():
	with open('reddit_ids.txt', 'r') as f:
		return f.read().splitlines()


post_ids = read_post_ids()


def add_post_id(post_id):
	if post_id in post_ids:
		# already in reddit_ids, no need to add it again
		return
	with open('reddit_ids.txt', 'a') as f:
		f.write(post_id + '\n')


def fetch_post_from_id(post_id):
	r = requests.get(f'https://www.reddit.com/comments/{post_id}.json', headers={
		'user-agent': user_agent
	})
	data = r.json()
	post = data[0]['data']['children'][0]['data']
	return post

def fetch_post_from_subreddit(subreddit, min_length=None):
	r = requests.get(f'https://www.reddit.com/r/{subreddit}/top.json?t=month', headers={
		'user-agent': user_agent
	})
	data = r.json()
	posts_list = data['data']['children']
	post = None
	for post in posts_list:
		post = post['data']
		if post['locked']: continue
		elif post['stickied']: continue
		elif post['id'] in post_ids: continue
		elif post['distinguished'] == 'moderator': continue
		elif min_length is not None and min_length < len(post['selftext']): continue
		return post


def fetch_post(subreddit=None, post_id=None, min_length=None):
	return {
		'id': 'a',
		'title': 'hello world',
		'body': 'pog',
		'score': 69420,
		'subreddit_name_prefixed': 'r/snooslash',
		'author': 'snooslash',
	}
	if post_id:
		post = fetch_post_from_id(post_id)
	else:
		if subreddit is None:
			subreddit = random.choice(subreddits)
		post = fetch_post_from_subreddit(subreddit, min_length=min_length)
	add_post_id(post['id'])
	return {
		'id': post['id'],
		'title': post['title'],
		'body': post['selftext'],
		'score': post['score'],
		'subreddit_name_prefixed': post['subreddit_name_prefixed'],
		'author': post['author'],
	}
