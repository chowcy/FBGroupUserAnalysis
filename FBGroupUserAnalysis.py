#Program to find data on users in a Facebook group you have privileges for

import json
import requests
import sys

#TODO: fill in the FB_GROUP_ID and your access token
FB_GROUP_ID = ''
# get access token from
# https://developers.facebook.com/tools/explorer"
access_token = None
if access_token == None:
    access_token = raw_input("\nCopy and paste token from https://developers.facebook.com/tools/explorer\n>  ")

FB_BASEURL = "https://graph.facebook.com/v2.10/{}/feed".format(FB_GROUP_ID)
CACHE_FNAME = 'cache.json'

#function that prints json nicely (for debugging only)
def pretty(obj):
    return json.dumps(obj, sort_keys = True, indent = 2)

#open cache file
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

#function gets data from caching or API
def getWithCaching(baseURL, params = {}):
    req = requests.Request(method = 'GET', url = baseURL, params = sorted(params.items()))
    prepped = req.prepare()
    fullURL = prepped.url

    # if we haven't seen this URL before
    if fullURL not in CACHE_DICTION:
        # make the request and store the response
        response = requests.Session().send(prepped)
        CACHE_DICTION[fullURL] = response.text

        # write the updated cache file
        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()

    # if fullURL WAS in the cache, CACHE_DICTION[fullURL] already had a value
    # if fullURL was NOT in the cache, we just set it in the if block above, so it's there now
    return CACHE_DICTION[fullURL]

# Building the Facebook parameters dictionary
url_params = {}
url_params["access_token"] = access_token
#post messages, likes, comments, subcomments, sublikes, submessages
url_params["fields"] = "message,likes{name},from,comments{from,comments{likes,message,from},message,likes}"
url_params['filter'] = 'stream'
url_params["limit"] = 200

#class definition of a comment
class Comment():
    #initialize commenter, comment message, subcomments, sublikes, and likes
    def __init__(self, comment_dict = {}):
        if 'from' in comment_dict:
            self.commenter = comment_dict['from']['name']
        else:
            self.commenter = ''
        if 'message' in comment_dict:
            self.comment = comment_dict['message']
        else:
            self.comment = ''
        if 'comments' in comment_dict:
            #comment class inception. Each subcomment is an instance of Comment class
            self.subcomments = [Comment(comment) for comment in comment_dict['comments']['data']]
            if 'likes' in self.subcomments:
                self.sublikes = self.subcomments['likes']['data']
            else:
                self.sublikes = []
        else:
            self.subcomments = []
            self.sublikes = []
        if 'likes' in comment_dict:
            self.likes = comment_dict['likes']['data']
        else:
            self.likes = []

#class definition of a post
class Post():
    #initialize posts's poster, message, comments, likes, comment count and like count
    def __init__(self, post_dict={}):
        #who posted stores a string into self.poster
        if 'from' in post_dict:
            self.poster = post_dict['from']['name']
        else:
            self.poster = ''
        #the text of the post is stored as a string into self.message
        if 'message' in post_dict:
            self.message = post_dict['message']
        else:
            self.message = ''
        #the text of comments to the post are stored as a list of Comment instances into self.comments
        if 'comments' in post_dict:
            self.comments = [Comment(comment) for comment in post_dict['comments']['data']]
        else:
            self.comments = []
        #the names of people who liked the post are stored as a list into self.likes
        if 'likes' in post_dict:
            self.likes = post_dict['likes']['data']
        else:
            self.likes = []
        #store the number of comments and likes this post has
        self.comment_count = len(self.comments)
        self.like_count = len(self.likes)

    #returns a list of the names of people who commented on the post
    def getCommenters(self):
        return [commenter['from']['name'] for commenter in self.comments if 'from' in commenter]

    #returns a list of the names of people who liked the post
    def getLikers(self):
        return [liker['name']for liker in self.likes]

    def __str__(self):
        return self.message

#get facebook group feed data
r = getWithCaching(FB_BASEURL, params=url_params)
feed = json.loads(r)

#convert all posts into post instances
try:
    post_insts = [Post(post) for post in feed['data']]
except:
    print('Access token likely expired. Get a new one at https://developers.facebook.com/tools/explorer')
    sys.exit(0)

#create large user dictionary with the key being the name of a user who has interacted
#in the group, and the value is data about this user: their posts, their comments,
#how many times they liked things, and how many times their posts/comments were liked by others
users = {}

#look at every post in the group's feed to extract information about users
for post in post_insts:
    #add user to dictionary and add in post message data
    if post.poster not in users:
        users[post.poster] = {'posts': [post.message], 'comments': [], 'likes': 0, 'liked': 0}
    else:
        users[post.poster]['posts'].append(post.message)

    #add liked data to poster
    users[post.poster]['liked'] += len(post.likes)

    #look at this post's likes
    for like_info in post.likes:
        #update users that liked the post
        if like_info['name'] not in users:
            users[like_info['name']] = {'posts': [], 'comments': [], 'likes': 1, 'liked': 0}
        else:
            users[like_info['name']]['likes'] += 1

    #look at comments
    for comment in post.comments:
        #add commenter if not in users
        commenter = comment.commenter
        if commenter not in users:
            users[commenter] = {'posts': [], 'comments': [comment.comment], 'likes': 0, 'liked': 0}
        else:
            users[commenter]['comments'].append(comment.comment)

        users[commenter]['liked'] += len(comment.likes)

        #look at this comment's likes
        for like_info in comment.likes:
            #update users that liked the comment
            if like_info['name'] not in users:
                users[like_info['name']] = {'posts': [], 'comments': [], 'likes': 1, 'liked': 0}
            else:
                users[like_info['name']]['likes'] += 1

        #look at subcomments
        for subcomment in comment.subcomments:
            #updates users that commented on the comment
            if subcomment.commenter not in users:
                users[subcomment.commenter] = {'posts': [], 'comments': [subcomment.comment], 'likes': 0, 'liked': 0}
            else:
                users[subcomment.commenter]['comments'].append(subcomment.comment)
            #update liked values for this comment if it is liked
            users[subcomment.commenter]['liked'] += len(subcomment.likes)

            #look at this subcomment's likes
            for sublike in subcomment.likes:
                #update users that liked the subcomment
                if sublike['name'] not in users:
                    users[sublike['name']] = {'posts': [], 'comments': [], 'likes': 1, 'liked': 0}
                else:
                    users[sublike['name']]['likes'] += 1

#write big user dictionary to json file
f = open('fbgroup_user_data.json', 'w')
f.write(json.dumps(users))
f.close()

#REPORT ANALYSIS
f = open('fbgroup_report.txt', 'w')
f.write('=' * 20)
f.write('\nTop 15 people who wrote posts\n')
f.write('=' * 20)
top_posters = sorted(users.keys(), key = lambda x: len(users[x]['posts']), reverse = True)[:15]
for poster in top_posters:
    if len(users[poster]['posts']) > 0:
        f.write('\n{}: \t\twrote {} posts!'.format(poster, len(users[poster]['posts'])))

f.write('\n\n')
f.write('=' * 20)
f.write('\nTop 15 people who wrote comments\n')
f.write('=' * 20)
top_commenters = sorted(users.keys(), key = lambda x: len(users[x]['comments']), reverse = True)[:15]
for commenter in top_commenters:
    if len(users[commenter]['comments']) > 0:
        f.write('\n{}: \t\twrote {} comments!'.format(commenter, len(users[commenter]['comments'])))

f.write('\n\n')
f.write('=' * 20)
f.write('\nTop 15 people who wrote stuff period\n')
f.write('=' * 20)
top_writers = sorted(users.keys(), key = lambda x: len(users[x]['comments']) + len(users[x]['posts']), reverse = True)[:15]
for writer in top_writers:
    if len(users[writer]['comments']) + len(users[writer]['posts']) > 0:
        f.write('\n{}: \t\twrote {} things!'.format(writer, len(users[writer]['comments']) + len(users[writer]['posts'])))

f.write('\n\n')
f.write('=' * 20)
f.write('\nTop 15 "liked" people\n')
f.write('=' * 20)
top_liked = sorted(users.keys(), key = lambda x: users[x]['liked'], reverse = True)[:15]
for person in top_liked:
    if users[person]['liked'] > 0:
        f.write('\n{} \t\twas liked {} times!'.format(person, users[person]['liked']))

f.write('\n\n')
f.write('=' * 20)
f.write('\nTop 15 people who interacted (liked, commented, posted)\n')
f.write('=' * 20)
top_interacted = sorted(users.keys(), key = lambda x: users[x]['likes'] + len(users[x]['comments']) + len(users[x]['posts']), reverse = True)[:15]
for person in top_interacted:
    num_interactions = users[person]['likes'] + len(users[person]['comments']) + len(users[person]['posts'])
    if num_interactions > 0:
        f.write('\n{} \t\tinteracted {} times!'.format(person, num_interactions))
f.close()
