import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import time
import datetime
import csv

'''
    TO DO: 
    1) DO SOMETHING WITH THE DATA (FIND BEST DEALS)
    2) LOOK AT REVIEWS OF EACH GAME
    3) AUTOMATE THIS PROCESS

'''

#steam store searching for RPGs
url = 'https://store.steampowered.com/search/results/?query&start=50&count=50&dynamic_data=&force_infinite=1&tags=122&supportedlang=english&filter=topsellers&ndl=1&snr=1_7_7_7000_7&infinite=1'

'''
    FUNCTION THAT RETRIEVES HTML INFO FOR GAME TITLES AND PRICES ON STEAM USING JSON; RETURNS TUPLE OF GAMES LIST AND INT OF TOTAL RESULTS
'''

def get_all_games(url):
    req = requests.get(url)
    req_dict = dict(req.json())
    soup = bs(req_dict['results_html'], 'html.parser')
    games_html = soup.find_all('a') #list of all games since all are under a tags
    total_results = req_dict['total_count'] #element of json that indicates total games in infinite scroll
    
    return (games_html, total_results)

'''
    FUNCTION THAT CREATES A LIST OF GAME DICTIONARIES, WITH TITLE, ORIGINAL PRICE, AND DISCOUNTED PRICE
'''

def create_games_list(games_html):
    games_list = []
    for game in games_html:
        title = game.find('span', {'class' : 'title'}).text
        gid = game['data-ds-appid'] #game id, will use this for reviews scraping
        
        #all games have this, for discounted games this will be the discounted price
        try:
            price = game.find('div', {'class' : 'discount_final_price'}).text.strip().split('$') #price of game, after discount if discounted
        except:
            price = ['Free']
        
        #free games don't split the same
        if(price[0] != 'Free'): 
            price = price[1] 
        else:
            price = price[0]
        
        #original price before discount
        og_price = game.find('div', {'class' : 'discount_original_price'})
        
        #og_price only found if game is discounted
        if(og_price == None): 
            og_price = price
        else:
            og_price = og_price.text.strip().split('$')[1]
        
        game_dict = {
            'title': title,
            'og_price': og_price,
            'disc_price': price
        }
        
        games_list.append(game_dict)
    return games_list

'''
    FUNCTION TO OUTPUT THE SCRAPED DATA TO A CSV FILE, ADDING DATE AND TIME AT FILE'S HEADER
'''

def games_to_csv(games_list):
    games_df = pd.concat([pd.DataFrame(g) for g in results])
    #games_df.to_csv('game_prices.csv', index=False)
    
    #write a header representing the date modified; still not working
    filepath = './game_prices.csv'
    with open(filepath, 'w') as f:
        f.write(create_csv_header())
        f.close()
    games_df.to_csv(filepath, index=False, header=False, mode='a')
    
    print('Saved games to CSV')
    return

'''
    FUNCTION TO ADD A DATETIME STAMP TO THE CSV
'''
def create_csv_header():
    #get current date and time
    now = datetime.datetime.now()
    
    #time
    secs = now.second
    mins = now.minute
    hrs = now.hour
    
    #date
    day = now.day
    month = now.month
    year = now.year

    #create header for csv with date and time, we will write this into our csv
    csv_header = 'Game prices as of: ' + str(year) + '/' + str(month) + '/' + str(day) + ', at ' + str(hrs) + ':' + str(mins) + ':' + str(secs) + '\n'
    return csv_header

#get the total amount of results (games) from get_all_games tuple returned
total_results = get_all_games(url)[1]
print(total_results)
results = []


#loop thru all of the games in the infinite scroll page, shows 50 at a time
for x in range(0, total_results, 50):
    all_games = get_all_games(f'https://store.steampowered.com/search/results/?query&start={x}&count=50&dynamic_data=&force_infinite=1&tags=122&supportedlang=english&filter=topsellers&ndl=1&snr=1_7_7_7000_7&infinite=1')
    if(all_games != None): results.append(create_games_list(all_games[0])) #get_all_games returns tuple of list, int, just want list
    print(x)

games_to_csv(results)


