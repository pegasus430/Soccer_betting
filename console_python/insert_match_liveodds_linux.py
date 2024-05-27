import requests
from bs4 import BeautifulSoup
import argparse
import mysql.connector
import certifi
import urllib3
import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime , timedelta
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import sys

http = urllib3.PoolManager( cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="soccer"
)

mycursor = mydb.cursor(buffered=True) 

PROXY = "193.149.225.224:80"

chrome_options = Options()

chrome_options.add_argument('headless')
chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_driver_path = '/usr/local/bin/chromedriver'

site_url = "https://www.oddsportal.com/football/"

def switch_month(argument):
    switcher = {
        "Jan" : "01",
        "Feb" : "02",
        "Mar" : "03",
        "Apr" : "04",
        "May" : "05",
        "Jun" : "06",
        "Jul" : "07",
        "Aug" : "08",
        "Sep" : "09",
        "Oct" : "10",
        "Nov" : "11",
        "Dec" : "12"
    }
    return switcher.get(argument, "null")

def switch_season(argument):
    switcher = {
        "2020" : 64,
        "2021" : 844 ,
        "2019-2020": 12,
        "2020-2021": 799,
        "2021-2022": 857,
        "2022" : 916,
        "2022-2023" : 935,
        "2023" : 1013,
        "2023-2024" : 1027,
        "2024": 1101,
    }
    return switcher.get(argument, "null")
  
def switch_league(argument):
    switcher = {
        "england/premier-league-": 6,   #England
        "spain/laliga": 16,  #spain
        "germany/bundesliga": 8,   #Germany
        "italy/serie-a" : 11,  #italy
        "france/ligue-1" : 7,   #france
        "netherlands/eredivisie": 12,  #Netherland
        "austria/tipico-bundesliga": 1,  #Austria
        "portugal/primeira-liga": 14,  #portugal
        "greece/super-league": 9,   #Greece
        "turkey/super-lig": 19,   #Turkey
        "norway/eliteserien": 13,  #Norway
        "sweden/allsvenskan": 17,  #Sweden
        "switzerland/super-league": 18,   #Swiztland
        "denmark/superliga": 5,     #Denmark
        "ukraine/premier-league": 20,     #Ukraine
        "bulgaria/parva-liga": 2,       #bulgaria
        "czech-republic/1-liga": 3,      #Chezch
        "croatia/1-hnl": 4 ,          #Croatia
        "hungary/otp-bank-liga": 10,     #Hungary
        "serbia/super-liga": 15    #Serbia
    }
    return switcher.get(argument, "null")
  
total_inserted_count = 0
total_updated_count = 0

def insert_update_odds(basic_match_href_url, match_date, home_team, away_team):
    global total_inserted_count , total_updated_count
    three_way_url = basic_match_href_url + "#1X2;2" 
    OU_url  =  basic_match_href_url + "#over-under;2"
    AH_url = basic_match_href_url + "#ah;2"  
    home_team_name = home_team
    away_team_name = away_team
    sql = f"SELECT team_id from team_list where team_name_odd = '{home_team_name}'"
    # print(sql)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if result:
        home_team_id = result[0][0]
        sql = f"SELECT match_id from season_match_plan where date = '{match_date}' and home_team_id = {home_team_id}"
        # print(sql)
        mycursor.execute(sql)
        result  =  mycursor.fetchall()
        if result:
            match_id = result[0][0]
            print("        match_id is ", match_id)
            odd_price = get_odds(three_way_url, OU_url, AH_url)
            print("        " , odd_price)
            sql = f"select * from odds where match_id = {match_id} and bookmaker_id = 13"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            if result:                  # alrady exist in odds table

                sql = f"UPDATE odds set Home = {odd_price['3way']['highest'][0]}, Draw =  {odd_price['3way']['highest'][1]}, Away = {odd_price['3way']['highest'][2]} " \
                  f", Over2d5 =  {odd_price['O/U']['highest'][0]}, Under2d5  =  {odd_price['O/U']['highest'][1]} , AH2_1 = {odd_price['AH']['AH_2']['highest'][0]} , AH2_2 = {odd_price['AH']['AH_2']['highest'][1]} , " \
                  f"AH1d75_1 = {odd_price['AH']['AH_1.75']['highest'][0]} , AH1d75_2 = {odd_price['AH']['AH_1.75']['highest'][1]} ," \
                  f"AH1d5_1 = {odd_price['AH']['AH_1.5']['highest'][0]} , AH1d5_2 = {odd_price['AH']['AH_1.5']['highest'][1]} ," \
                  f"AH1d25_1 = {odd_price['AH']['AH_1.25']['highest'][0]} , AH1d25_2 = {odd_price['AH']['AH_1.25']['highest'][1]} ," \
                  f"AH1_1 = {odd_price['AH']['AH_1']['highest'][0]} , AH1_2 = {odd_price['AH']['AH_1']['highest'][1]} ," \
                  f"AH0d75_1 = {odd_price['AH']['AH_0.75']['highest'][0]} , AH0d75_2 = {odd_price['AH']['AH_0.75']['highest'][1]} ," \
                  f"AH0d5_1 = {odd_price['AH']['AH_0.5']['highest'][0]} , AH0d5_2 = {odd_price['AH']['AH_0.5']['highest'][1]} ," \
                  f"AH0d25_1 = {odd_price['AH']['AH_0.25']['highest'][0]} , AH0d25_2 = {odd_price['AH']['AH_0.25']['highest'][1]} ," \
                  f"AH0_1 = {odd_price['AH']['AH_0']['highest'][0]} , AH0_2 = {odd_price['AH']['AH_0']['highest'][1]} ," \
                  f"AH_p0d25_1 = {odd_price['AH']['AH_p0.25']['highest'][0]} , AH_p0d25_2 = {odd_price['AH']['AH_p0.25']['highest'][1]} ," \
                  f"AH_p0d5_1 = {odd_price['AH']['AH_p0.5']['highest'][0]} , AH_p0d5_2 = {odd_price['AH']['AH_p0.5']['highest'][1]} ," \
                  f"AH_p0d75_1 = {odd_price['AH']['AH_p0.75']['highest'][0]} , AH_p0d75_2 = {odd_price['AH']['AH_p0.75']['highest'][1]} ," \
                  f"AH_p1_1 = {odd_price['AH']['AH_p1']['highest'][0]} , AH_p1_2 = {odd_price['AH']['AH_p1']['highest'][1]} ," \
                  f"AH_p1d25_1 = {odd_price['AH']['AH_p1.25']['highest'][0]} , AH_p1d25_2 = {odd_price['AH']['AH_p1.25']['highest'][1]} ," \
                  f"AH_p1d5_1 = {odd_price['AH']['AH_p1.5']['highest'][0]} , AH_p1d5_2 = {odd_price['AH']['AH_p1.5']['highest'][1]} ," \
                  f"AH_p1d75_1 = {odd_price['AH']['AH_p1.75']['highest'][0]} , AH_p1d75_2 = {odd_price['AH']['AH_p1.75']['highest'][1]} ," \
                  f"AH_p2_1 = {odd_price['AH']['AH_p2']['highest'][0]} , AH_p2_2 = {odd_price['AH']['AH_p2']['highest'][1]} , updated_at = '{datetime.today().strftime('%Y-%m-%d')}'" \
                  f"WHERE match_id = {match_id} and bookmaker_id = 13"
                mycursor.execute(sql)
                mydb.commit()

                total_updated_count += 1
                print("         # Update successful! ")
            else:                       # this is new in odds, so will insert
                
                sql = f"INSERT INTO odds (match_id, bookmaker_id, Home, Draw, Away, Over2d5, Under2d5 , AH2_1, AH2_2, AH1d75_1, AH1d75_2, AH1d5_1, AH1d5_2 , AH1d25_1, AH1d25_2, AH1_1, AH1_2, AH0d75_1, AH0d75_2, AH0d5_1, AH0d5_2, AH0d25_1, AH0d25_2, AH0_1, AH0_2 , AH_p0d25_1 , AH_p0d25_2, AH_p0d5_1, AH_p0d5_2, AH_p0d75_1 , AH_p0d75_2, AH_p1_1, AH_p1_2, AH_p1d25_1, AH_p1d25_2, AH_p1d5_1, AH_p1d5_2, AH_p1d75_1, AH_p1d75_2, AH_p2_1, AH_p2_2 , updated_at ) " \
                f"VALUES ({match_id}, 13, {odd_price['3way']['highest'][0]}, {odd_price['3way']['highest'][1]}, {odd_price['3way']['highest'][2]}, {odd_price['O/U']['highest'][0]}, {odd_price['O/U']['highest'][1]} , " \
                f"{odd_price['AH']['AH_2']['highest'][0]} , {odd_price['AH']['AH_2']['highest'][1]} ,{odd_price['AH']['AH_1.75']['highest'][0]} , {odd_price['AH']['AH_1.75']['highest'][1]} , " \
                f"{odd_price['AH']['AH_1.5']['highest'][0]} , {odd_price['AH']['AH_1.5']['highest'][1]} ,{odd_price['AH']['AH_1.25']['highest'][0]} , {odd_price['AH']['AH_1.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_1']['highest'][0]} , {odd_price['AH']['AH_1']['highest'][1]} ,{odd_price['AH']['AH_0.75']['highest'][0]} , {odd_price['AH']['AH_0.75']['highest'][1]} , " \
                f"{odd_price['AH']['AH_0.5']['highest'][0]} , {odd_price['AH']['AH_0.5']['highest'][1]} ,{odd_price['AH']['AH_0.25']['highest'][0]} , {odd_price['AH']['AH_0.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_0']['highest'][0]} , {odd_price['AH']['AH_0']['highest'][1]} ,{odd_price['AH']['AH_p0.25']['highest'][0]} , {odd_price['AH']['AH_p0.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_p0.5']['highest'][0]} , {odd_price['AH']['AH_p0.5']['highest'][1]},{odd_price['AH']['AH_p0.75']['highest'][0]} , {odd_price['AH']['AH_p0.75']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p1']['highest'][0]} , {odd_price['AH']['AH_p1']['highest'][1]},{odd_price['AH']['AH_p1.25']['highest'][0]} , {odd_price['AH']['AH_p1.25']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p1.5']['highest'][0]} , {odd_price['AH']['AH_p1.5']['highest'][1]},{odd_price['AH']['AH_p1.75']['highest'][0]} , {odd_price['AH']['AH_p1.75']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p2']['highest'][0]} , {odd_price['AH']['AH_p2']['highest'][1]} , '{datetime.today().strftime('%Y-%m-%d')}') "
                mycursor.execute(sql)
                mydb.commit()

                total_inserted_count += 1
                print("        # insert successful! ")
                
        else:
            print("        # Can't find match id in season_match_plan table.")
    else:
        print("        # Can't find team_id in team_list.")
    
# function for scraping MO, O/U, AH odds of following matches    
def get_odds(turl, OU_url , AH_url):
    odd_price = {"3way": {}, "O/U": {}, "AH": {}}
   
    highest_list = [] 
   
    ################################ driver setting part start############################
    driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    
    driver1.get(turl)
    driver1.refresh()
    time.sleep(1)
    ################################ driver setting part End #############################`
    
    ############## 3 way result ###################################################################
    print("        * start scraping 1X2 data --------------------")
    main = driver1.find_element(By.TAG_NAME, 'main')
    time.sleep(1)
    high_elemnet = main.find_elements(By.CSS_SELECTOR, '.bg-gray-light')
    if len(high_elemnet) > 2:
        high_ = high_elemnet[2]

        if high_:
            av_values = high_.find_elements(By.CSS_SELECTOR, ".justify-center.font-bold")
            if len(av_values) > 2:
                for i in range(0, 3):
                    if av_values[i].text == "-" or av_values[i].text == "":
                        highest_list.append("0")
                    else: 
                        highest_list.append(convert_odds(av_values[i].text))
            else:
                highest_list = ['0', '0', '0']
        else:
            highest_list = ['0', '0', '0']
    else:
         highest_list = ['0', '0', '0']
            

    three_way = {"highest": highest_list}
    # print("   three_way ", three_way)
    odd_price['3way'] = three_way
    
    # ############### Over / Under result ############################################################

    print("        * start scraping Over Under data --------------------")
    
    driver1.get(OU_url)
    driver1.refresh()
    time.sleep(1)
    # wait = WebDriverWait(driver1, 20)
    # wait.until(EC.presence_of_element_located((By.ID, 'odds-data-table')))
    
    highest_list = []
    main = driver1.find_element(By.TAG_NAME, 'main')
    # wait = WebDriverWait(driver1, 20)
    # wait.until(EC.presence_of_element_located((By.TAG_NAME, '.relative.flex.flex-col')))
    time.sleep(2)
    element_OU = main.find_elements(By.CSS_SELECTOR , '.relative.flex.flex-col')

    if len(element_OU) == 0:
        print("    Couldn't find Over 2.5 values !")
        highest_list = ['0', '0']
    else:
        try:
            for element in element_OU:
                OU_name = element.find_element(By.TAG_NAME, 'p')
                
                OU_name =  OU_name.text.strip()
                if OU_name == "Over/Under +2.5":
                    av_values = element.find_elements(By.CLASS_NAME, "gradient-green-added-border")
                    
                    if len(av_values) > 1:
                        for i in  range(0, 2):
                            
                            if av_values[i].text == "-" or av_values[i].text == "":
                                highest_list.append("0")
                            else:
                                highest_list.append(convert_odds(av_values[i].text))
                    else:
                        highest_list = ['0', '0']
                    break
            if len(highest_list) == 0:
                highest_list = ['0', '0']
                    
        except Exception as ex:
            highest_list = ['0' , '0']
      
    O_U = {"highest": highest_list}
    # print("   OU ", O_U)
    odd_price['O/U'] = O_U
    ############### Asian Handicap result ############################################################
   
    print("        * start scraping Asian Handicap data --------------------")
    AH_odds = {"AH_2":{'highest': ['0', '0']}, "AH_1.75":{'highest': ['0', '0']}, "AH_1.5":{'highest': ['0', '0']}, "AH_1.25":{'highest': ['0', '0']}, "AH_1":{'highest': ['0', '0']}, "AH_0.75":{'highest': ['0', '0']}, "AH_0.5":{'highest': ['0', '0']}, "AH_0.25":{'highest': ['0', '0']}, "AH_0":{'highest': ['0', '0']} , 
    "AH_p2":{'highest': ['0', '0']}, "AH_p1.75":{'highest': ['0', '0']}, "AH_p1.5":{'highest': ['0', '0']}, "AH_p1.25":{'highest': ['0', '0']}, "AH_p1":{'highest': ['0', '0']}, "AH_p0.75":{'highest': ['0', '0']}, "AH_p0.5":{'highest': ['0', '0']}, "AH_p0.25":{'highest': ['0', '0']}}
    driver1.get(AH_url)
    driver1.refresh()
    time.sleep(1)

    main = driver1.find_element(By.TAG_NAME, 'main')
    time.sleep(1.5)
    AH_elements = main.find_elements(By.CSS_SELECTOR , '.relative.flex.flex-col')

    if len(AH_elements) == 0:
        print("    Couldn't find AH values !")
        highest_list = ['0', '0']
    else:
        ah_values_object = {}
        try:
            for index in range(0, len(AH_elements)):
                highest_list = []
                element = AH_elements[index]
                ah_name = element.find_element(By.TAG_NAME, 'p')
                ah_name =  ah_name.text.strip()
                av_values = element.find_elements(By.CLASS_NAME, "gradient-green-added-border")
                if len(av_values) > 1:
                    for i in  range(0, 2):
                        if av_values[i].text == '' or  av_values[i].text == '-':
                            highest_list.append('0')
                        else:
                            highest_list.append(convert_odds(av_values[i].text))
                else:
                    highest_list = ['0', '0']
                ah_values_object[ah_name] = {'highest': highest_list}
        except:
            print("    found unkown error in founding AH handicap")
        
        if('Asian Handicap -2' in ah_values_object) :
            AH_odds["AH_2"] = ah_values_object['Asian Handicap -2']
        else:
            AH_odds["AH_2"] = { "highest": ['0', '0']}

        if('Asian Handicap -1.75' in ah_values_object) :
            AH_odds["AH_1.75"] = ah_values_object['Asian Handicap -1.75']
        else:
            AH_odds["AH_1.75"] = { "highest": ['0', '0']}

        if('Asian Handicap -1.5' in ah_values_object) :
            AH_odds["AH_1.5"] = ah_values_object['Asian Handicap -1.5']
        else:
            AH_odds["AH_1.5"] = { "highest": ['0', '0']}

        if('Asian Handicap -1.25' in ah_values_object) :
            AH_odds["AH_1.25"] = ah_values_object['Asian Handicap -1.25']
        else:
            AH_odds["AH_1.25"] = { "highest": ['0', '0']}

        if('Asian Handicap -1' in ah_values_object) :
            AH_odds["AH_1"] = ah_values_object['Asian Handicap -1']
        else:
            AH_odds["AH_1"] = { "highest": ['0', '0']}

        if('Asian Handicap -0.75' in ah_values_object) :
            AH_odds["AH_0.75"] = ah_values_object['Asian Handicap -0.75']
        else:
            AH_odds["AH_0.75"] = { "highest": ['0', '0']}

        if('Asian Handicap -0.5' in ah_values_object) :
            AH_odds["AH_0.5"] = ah_values_object['Asian Handicap -0.5']
        else:
            AH_odds["AH_0.5"] = { "highest": ['0', '0']}

        if('Asian Handicap -0.25' in ah_values_object) :
            AH_odds["AH_0.25"] = ah_values_object['Asian Handicap -0.25']
        else:
            AH_odds["AH_0.25"] = { "highest": ['0', '0']}

        if('Asian Handicap 0' in ah_values_object) :
            AH_odds["AH_0"] = ah_values_object['Asian Handicap 0']
        else:
            AH_odds["AH_0"] = { "highest": ['0', '0']}

        if('Asian Handicap +2' in ah_values_object) :
            AH_odds["AH_p2"] = ah_values_object['Asian Handicap +2']
        else:
            AH_odds["AH_p2"] = { "highest": ['0', '0']}

        if('Asian Handicap +1.75' in ah_values_object) :
            AH_odds["AH_p1.75"] = ah_values_object['Asian Handicap +1.75']
        else:
            AH_odds["AH_p1.75"] = { "highest": ['0', '0']}

        if('Asian Handicap +1.5' in ah_values_object) :
            AH_odds["AH_p1.5"] = ah_values_object['Asian Handicap +1.5']
        else:
            AH_odds["AH_p1.5"] = { "highest": ['0', '0']}

        if('Asian Handicap +1.25' in ah_values_object) :
            AH_odds["AH_p1.25"] = ah_values_object['Asian Handicap +1.25']
        else:
            AH_odds["AH_p1.25"] = { "highest": ['0', '0']}

        if('Asian Handicap +1' in ah_values_object) :
            AH_odds["AH_p1"] = ah_values_object['Asian Handicap +1']
        else:
            AH_odds["AH_p1"] = { "highest": ['0', '0']}

        if('Asian Handicap +0.75' in ah_values_object) :
            AH_odds["AH_p0.75"] = ah_values_object['Asian Handicap +0.75']
        else:
            AH_odds["AH_p0.75"] = { "highest": ['0', '0']}

        if('Asian Handicap +0.5' in ah_values_object) :
            AH_odds["AH_p0.5"] = ah_values_object['Asian Handicap +0.5']
        else:
            AH_odds["AH_p0.5"] = { "highest": ['0', '0']}

        if('Asian Handicap +0.25' in ah_values_object) :
            AH_odds["AH_p0.25"] = ah_values_object['Asian Handicap +0.25']
        else:
            AH_odds["AH_p0.25"] = { "highest": ['0', '0']}

    
    odd_price['AH'] = AH_odds
    driver1.quit()
    return odd_price

def getDate_from_trTxt(date_txt):
    if 'Today' in date_txt:
        return datetime.today().strftime('%Y-%m-%d')
    elif 'Tomorrow' in date_txt:
        tomorrow = datetime.now() + timedelta(1)
        return datetime.strftime(tomorrow, '%Y-%m-%d')
    else:
        date_part = date_txt.split(' ');
        return date_part[2] + "-" +switch_month(date_part[1]) + '-' + date_part[0]

def insert_Price_To_Matchplan(league, season):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

    current_season = False
    page_url = site_url + league
    driver.get(page_url)
    driver.refresh()
    print(f"----------------{league}  start--------------------------------")
  
    time.sleep(2)

    WebDriverWait(driver, 15).until(
      EC.presence_of_element_located((By.TAG_NAME, 'main'))
    )
    main = driver.find_element(By.TAG_NAME, 'main')                # get main components

    index = 0
    match_date = ""
    
    div_element = main.find_element(By.CLASS_NAME, 'w-full')
    all_elements = div_element.find_elements(By.CSS_SELECTOR, '.flex.flex-col.w-full.text-xs')

    # print(" length of all elements" , len(all_elements))

    for element in all_elements:
        if(index % 2 == 0):  
            all_leading = element.find_elements(By.CSS_SELECTOR, '.leading-5')
            if(len(all_leading) > 1):
                # have date filed
                date_txt = all_leading[0].text
                match_date = getDate_from_trTxt(date_txt)
            
            group_element = element.find_element(By.CSS_SELECTOR, '.group')
            if(group_element):
                # match field
                print(f"    --- {league} {season} { str(int(index/2))} th match start---")
                main_text_element = group_element.find_element(By.CSS_SELECTOR, '.flex.w-full')
                team_elements = main_text_element.find_elements(By.TAG_NAME, ("a"))
                href_a_element = group_element.find_element(By.TAG_NAME, ("a"))
                home_team = team_elements[0].get_attribute('title')
                away_team = team_elements[2].get_attribute('title')
                print(f"          {match_date} , {home_team} - {away_team} ")
                hrefUrl = href_a_element.get_attribute('href')
                status = insert_update_odds(hrefUrl, match_date, home_team, away_team )
        
        index += 1    

    print(f"---------------- {league} -  End--------------------------------")
    driver.quit()

# function for converting UK odds to EU odds
def convert_odds(uk_odds):
    
    if '/' in uk_odds:
        a_b_list = uk_odds.split('/')
        if len(a_b_list) == 2:
            a = int(a_b_list[0].strip())
            b = int(a_b_list[1].strip())
            eu_odd = 1 + round(a/b , 2)
            eu_odd = '%.2f' % eu_odd
            return str(eu_odd)
        else:
            return '0'
    else:
        return '0'

insert_Price_To_Matchplan("england/premier-league",   "2023-2024")
insert_Price_To_Matchplan("spain/laliga",             "2023-2024")
insert_Price_To_Matchplan("germany/bundesliga",       "2023-2024")
insert_Price_To_Matchplan("italy/serie-a",            "2023-2024")
insert_Price_To_Matchplan("france/ligue-1",           "2023-2024")
insert_Price_To_Matchplan("netherlands/eredivisie",   "2023-2024")
insert_Price_To_Matchplan("austria/tipico-bundesliga","2023-2024")
insert_Price_To_Matchplan("portugal/primeira-liga",   "2023-2024")
insert_Price_To_Matchplan("greece/super-league",      "2023-2024")
insert_Price_To_Matchplan("turkey/super-lig",         "2023-2024")
insert_Price_To_Matchplan("norway/eliteserien",       "2024")
insert_Price_To_Matchplan("sweden/allsvenskan",       "2024")
insert_Price_To_Matchplan("switzerland/super-league", "2023-2024")
insert_Price_To_Matchplan("denmark/superliga",        "2023-2024")
insert_Price_To_Matchplan("ukraine/premier-league",   "2023-2024")
insert_Price_To_Matchplan("bulgaria/parva-liga",      "2023-2024")
insert_Price_To_Matchplan("czech-republic/1-liga",    "2023-2024")
insert_Price_To_Matchplan("croatia/1-hnl",            "2023-2024")
insert_Price_To_Matchplan("hungary/otp-bank-liga",    "2023-2024")
insert_Price_To_Matchplan("serbia/super-liga",        "2023-2024")

print(" Total inserted count is : ", total_inserted_count)
print(" Total updated count is : ", total_updated_count)
