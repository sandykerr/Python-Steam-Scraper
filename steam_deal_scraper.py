import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import time
import datetime
import csv

'''
    TO DO: 
    1) FIX THE HEADER SITUATION IN THE CSV; it's not writing the date and time properly, something about pd.to_csv() is overwriting
    2) FIND A WAY TO MAKE INFINITE (OR NEAR-INFINITE) SCROLLING WORK (see yt vid)
    3) AUTOMATE THIS PROCESS

'''

#steam store searching for RPGs
url2 = 'https://store.steampowered.com/search/results/?query&start=50&count=50&dynamic_data=&force_infinite=1&tags=122&supportedlang=english&filter=topsellers&ndl=1&snr=1_7_7_7000_7&infinite=1'

def get_html(url):
    req = requests.get(url)
    req_to_json = dict(req.json())
    soup = bs(req_to_json['results_html'], 'html.parser')
    
    games_html = soup.find_all('a') #list of all games since all are under a tags
    
    return games_html

def create_games_list(games_html):
    games_list = []
    for game in games_html: 
        title = game.find('span', {'class' : 'title'}).text
        
        #all games have this, for discounted games this will be the discounted price
        price = game.find('div', {'class' : 'discount_final_price'}).text.strip().split('$')
        og_price = game.find('div', {'class' : 'discount_original_price'})
       
        #free games don't split the same
        if(price[0] != 'Free'): 
            price = price[1] 
        else:
            price = price[0]
        
        #discounted games have a non-null og_price var
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

def games_to_csv(games_list):
    games_df = pd.DataFrame(games_list)
    #games_df.to_csv('game_prices.csv', index=False)
    
    #write a header representing the date modified; still not working
    filepath = './game_prices.csv'
    with open(filepath, 'a') as f:
        f.write(create_csv_header())
        f.close()
    games_df.to_csv(filepath, index=False, header=False)
    
    print('Saved games to CSV')
    return

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
    csv_header = 'Game prices as of: ' + str(year) + '/' + str(month) + '/' + str(day) + ', at: ' + str(hrs) + ':' + str(mins) + ':' + str(secs) + '\n'
    return csv_header

games_html = get_html(url2)
games_list = create_games_list(games_html)
games_to_csv(games_list)


