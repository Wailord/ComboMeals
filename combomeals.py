import os.path
import xml.etree.ElementTree as ET
import urllib2
import time
import tweepy

def ordinal(n):
    return "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

def getPlayerString(player, player_stats, season_count):
    first_name = player.get('first')
    last_name = player.get('last')
    player_hr = player_stats.get('hr')
    player_sb = player_stats.get('sb')
    count_string = ordinal(season_count)
    return first_name + ' ' + last_name + ' combo meal, his ' + count_string + ' this season! (' + player_hr + ' HR, ' + player_sb + ' SB today)'

# twitter credentials
consumer_key = os.environ['CM_CONSUMER_KEY']
consumer_secret = os.environ['CM_CONSUMER_SECRET']
access_token = os.environ['CM_ACCESS_TOKEN']
access_token_secret = os.environ['CM_ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# download the updated data
mlb_today = time.strftime("http://gd2.mlb.com/components/game/mlb/year_%Y/month_%m/day_%d")

# used for testing
# fake_year='2016'
# fake_month='08'
# fake_day='03'
# mlb_today = 'http://gd2.mlb.com/components/game/mlb/year_' + fake_year + '/month_' + fake_month + '/day_' + fake_day + '/'

updated_xml = urllib2.urlopen(mlb_today + "/master_scoreboard.xml").read()
filename = 'combo_meals.txt'

# parse the downloaded XML
game_list = ET.fromstring(updated_xml)

with open(filename, "a+") as master_list:
    # read our master list of combo meals
    master_list.seek(0)
    combo_contents = master_list.read()

    # iterate over all of today's games
    for game in game_list.findall('game'):
        game_id = game.get('id')

        # look at each HR/player pairing in each game
        for home_run in game.findall('home_runs'):

            # look at the home run hitters
            for player in home_run.findall('player'):

                # first, have we already tweeted about this player in this game? no reason to do anything else if so
                player_id = player.get('id')
                combo_string = game_id + "/p_" + player_id
                already_tweeted = combo_contents.find(combo_string) >= 0

                if not already_tweeted:
                    # how many combo meals does this player have this season?
                    season_count = combo_contents.count('p_' + player_id) + 1

                    # make sure we don't get mixed up between doubleheader games
                    game_in_doubleheader = game_id[-1]
                    player_xml = urllib2.urlopen(mlb_today + '/batters/' + player_id + '_' + game_in_doubleheader + '.xml').read()
                    player_stats = ET.fromstring(player_xml)

                    if(int(player_stats.get('sb')) > 0):
                        player_string = getPlayerString(player, player_stats, season_count)
                        # this player has a combo meal today
                        tweet_string = player_string + ' @danieldopp @SultanOfStat @KarabellESPN @the06010board'
                        api.update_status(status=tweet_string)
                        master_list.write(combo_string + "\n")
                        print tweet_string