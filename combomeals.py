import xml.etree.ElementTree as ET
import urllib2
import time
import tweepy
import mmap

#open twitter
consumer_key = "<your consumer key here>"
consumer_secret = "<your consumer secret here>"
access_token = "<your access token here>"
access_token_secret = "<your access token secret here>"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# download the updated data
mlb_today = time.strftime("http://gd2.mlb.com/components/game/mlb/year_%Y/month_%m/day_%d")
updated_xml = urllib2.urlopen(mlb_today + "/master_scoreboard.xml").read()

# parse the downloaded XML
game_list = ET.fromstring(updated_xml)

with open("<your file of existing combo meals>", "a+") as combomeals:
    for game in game_list.findall('game'):
        for home_runs in game.findall('home_runs'):
            for players in home_runs.findall('player'):
                    combo_string = game.get('id') + "/" + players.get('id')
                    if(mmap.mmap(combomeals.fileno(), 0, access=mmap.ACCESS_READ).find(combo_string) == -1):
                        player_xml = urllib2.urlopen(mlb_today + "/batters/" + players.get('id') + "_1.xml").read()
                        player = ET.fromstring(player_xml)
                        if(int(player.get('sb')) > 0):
                            # this player has a combo meal today
                            tweet_string = players.get('first') + " " + players.get('last') + " combo meal! (" + player.get('hr') + " HR, " + player.get('sb') + " SB today) @danieldopp @SultanOfStat @KarabellESPN @the06010board"
                            combomeals.write(combo_string + "\n")
                            api.update_status(status=tweet_string)
                            # print players.get('first') + " " + players.get('last') + " (" + players.get('id') + ") "
                    # else:
                        # print players.get('first') + " " + players.get('last') + " (" + combo_string + ") already exists in combomeals.txt"
