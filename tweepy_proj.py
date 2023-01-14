import tweepy
from tweepy import OAuthHandler
import json
import time
import xlwt


consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

auth = OAuthHandler(consumer_key, consumer_secret) #create your own keys tokens and secrets
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

#.encode('unicode-escape').decode('utf-8') decodes all characters (eg emojis to unicode)

def see_fav_rt():
    fav = str(api.favorites()[0].id)
    stat = api.get_status(fav)
    ret = api.retweets(fav, 100)
    print('Favorited post has {} retweets.'.format(len(ret)))
    

##see_fav_rt()



cnnbrk_id = api.search_users('cnnbrk')[0].id
lastpost_id = api.user_timeline(cnnbrk_id)[0].id
#at each time interval, a tuple with
#(rt_count, num of likes) will be added to timestamps.
#at each interval, user_records will be updated with RTer name as key
#and rt datetime and rt_followerscount as values

def test_rt():
    status = api.get_status(lastpost_id)
    print('Test_rt has run.')
    print('Last post has {} retweets.'.format(status.retweet_count))
##    print(len(api.retweets(lastpost_id, 100)))
##    print(type(api.retweets(lastpost_id, 100)))
    print(status._json['retweeted_status'])
    test = api.retweets(lastpost_id, 100)
    print(len(test))
    for rt in test:
        print(rt.user.id)

##test_rt()


def new_post(account): #returns lp_id when the account posts a new post
    acc_id = api.search_users(account)[0].id
    acc_lastpost = api.user_timeline(acc_id)[0]
    print('Selected account is {}.'.format(api.get_user(acc_id).name))
    acc_lastpost_id = acc_lastpost.id
    latest_id = int(acc_lastpost_id) #int of new_post's id
    
    timer = 0
    while latest_id <= int(acc_lastpost_id) or \
          'retweeted_status' in api.get_status(latest_id)._json: #we dont want it if its a RT
        latest_id = api.user_timeline(acc_id)[0].id
        print('Loading... Latest post was {}'.format(api.get_status(str(latest_id)).text\
                                                     .encode('unicode-escape').decode('utf-8')))
        time.sleep(5)
        timer += 5
        print('Runtime: {} minutes'.format(timer // 60))

    print('A new post! Title: {}'.format(api.get_status(str(latest_id)).text))

    return str(latest_id)


timestamps = []
user_records = []
tweet_info = []

def check(acc):

    lp_id = new_post(acc)
    status = api.get_status(lp_id)
    tweet_info.append(status.id)
    tweet_info.append(status.text.encode('unicode-escape').decode('utf-8'))
    tweet_info.append(status.author.name.encode('unicode-escape').decode('utf-8'))
    tweet_info.append(status._json['created_at'])
    
    count = 0
    runtime = 3 * 60 #3 hours, 180 minutes
    rt_lst = [] #list of user ids of retweeters
    print(status.text)
    while count < runtime + 1: #need +1 or else it'll have 1 less interval
        status = api.get_status(lp_id)
        rtc = status.retweet_count
        fc = status.favorite_count
        timestamps.append(('Retweet count: {}'.format(rtc),\
                           'Favorite count: {}'.format(fc),\
                           'Minutes in: {}'.format(count)))
        retweets = api.retweets(lp_id, 100)
        for rt in retweets:
            if rt.user.id not in rt_lst:
                user_records.append([rt._json['created_at'], \
                                    rt.user.followers_count]) 
                rt_lst.append(rt.user.id)
        print('{} minute(s) in'.format(count))
        count += 1 #count += must be put above so if loop will break correctly
        if count < runtime + 1: 
            time.sleep(60)

print('timestamps: {}'.format(timestamps))
print('user_records: {}'.format(user_records))
check('BreitbartNews')
print('timestamps: {}'.format(timestamps))
print('user_records: {}'.format(user_records))

def write(ts, ur, ti): #timestamps, user_records, tweet_info
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Timestamps')


    ts_desc = [] #contains description/headers of timestamps
    for data in ts[0]:
        ts_desc.append(data.split(':')[0] + ':')

    for init_col in range(len(ts[0])):
        ws.write(0, init_col, ts_desc[init_col])

    for row in range(len(ts)): #writes timestamps into excel
        for col in range(len(ts[0])):
            ws.write(row + 1, col, int(ts[row][col].split(':')[1][1::]))


    ti_desc = []
    ti_desc.append('Tweet id:')
    ti_desc.append('Tweet text:')
    ti_desc.append('Tweet author:')
    ti_desc.append('Tweet datetime:')

    for init_ti_col in range(1, len(ti) + 1): #the +1 is just to format in excel better
        ws.write(0, len(ts[0]) + init_ti_col, ti_desc[init_ti_col - 1])

    for ti_col in range(1, len(ti) + 1): #the +1 is just to format in excel better
        ws.write(1, len(ts[0]) + ti_col, tweet_info[ti_col - 1])


    ws2 = wb.add_sheet('User_records')

    ur_desc = [] #contains description/headers of user_records
    ur_desc.append('Retweeted on:')
    ur_desc.append('Follower count:')
    
    for init_ur_col in range(len(ur_desc)):
        ws2.write(0, init_ur_col, ur_desc[init_ur_col])

    for ur_row in range(len(ur)): #writes user_records into excel
        for ur_col in range(len(ur_desc)):
            input_data = str(ur[ur_row][ur_col])
            if input_data.isnumeric(): #its the follower_count
                ws2.write(ur_row + 1, ur_col, int(input_data))
            else: #its the datetime
                ws2.write(ur_row + 1, ur_col, input_data)

    wb.save('JC2MM_Data_BBN.xls')

write(timestamps, user_records, tweet_info)











