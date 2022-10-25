import json
import sys 
from datetime import datetime

def round_minutes(dt):
    rounded_minute = round(dt.minute / 15) * 15
    
    if rounded_minute == 60:
        rounded_hour = dt.hour + 1
        
        if rounded_hour > 23:
           return dt.replace(day=dt.day + 1, hour=0, minute=0)
        return dt.replace(hour=rounded_hour, minute=0)
    return dt.replace(minute=rounded_minute)

def find(arr, predicate):
    for elem in arr:
        if predicate(elem):
            return elem
    return None

def main():
    tweets = 0 
    sys.stdout.write('date\t time\t username\t original_poster\n')

    for line in sys.stdin:
        tweets += 1
        tweet = json.loads(line)
        tweet_data = tweet['data']
        tweet_includes = tweet['includes']       
        tweet_users = tweet_includes['users']

        dt = datetime.fromisoformat(tweet_data['created_at'].replace('Z',''))
        
        date = dt.strftime('%Y-%m-%d')
        time = round_minutes(dt).strftime('%H:%M')
        
        username = find(tweet_users, lambda user: user['id'] == tweet_data['author_id'])['username']
        original_poster = None

        original_tweet = find(tweet_includes['tweets'], lambda tweet: tweet['id'] == tweet_data['id'])
        
        if original_tweet and original_tweet.get('referenced_tweets'):
            retweeted_ref = find(original_tweet['referenced_tweets'], lambda ref: ref['type'] == 'retweeted')
            
            if retweeted_ref:
                rt_id = retweeted_ref['id']
                retweeted = find(tweet_includes['tweets'], lambda tweet: tweet['id'] == rt_id)
            
                original_poster_id = retweeted['author_id']
                original_poster = find(tweet_users, lambda user: user['id'] == original_poster_id)['username']
	
        sys.stdout.write(f'{date}\t{time}\t{username}\t{original_poster}\n')

    print("Successfully read", tweets, "tweets")

main()
