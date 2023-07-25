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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import sys
import os

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="P@ssw0rd2021",
    database="soccer"
)

mycursor = mydb.cursor(buffered=True)

driverpath = "C:\Soccer_betting\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('headless')
chrome_options.add_experimental_option("excludeSwitches", ['enable-logging']);
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-browser-side-navigation")

chrome_options.page_load_strategy = 'eager'
chrome_options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

site_url = "https://www.oddsportal.com/"
tfoot_index = 0
def switch_month(argument):
    switcher = {
      "Jan": "01",
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
        "2022" : 916,
        "2023" : 1013,
        "2022-2023" : 935,
        "2023-2024" : 1027,
    }
    return switcher.get(argument, "null")

def switch_league(argument):
    switcher = {
        "england/premier-league-": 6,       # England
        "spain/laliga": 16,                 # Spain
        "germany/bundesliga": 8,            # Germany
        "italy/serie-a" : 11,               # Italy
        "france/ligue-1" : 7,               # France
        "netherlands/eredivisie": 12,       # Netherland
        "austria/tipico-bundesliga": 1,     # Austria
        "portugal/primeira-liga": 14,       # Portugal
        "greece/super-league": 9,           # Greece
        "turkey/super-lig": 19,             # Turkey
        "norway/eliteserien": 13,           # Norway
        "sweden/allsvenskan": 17,           # Sweden
        "switzerland/super-league": 18,     # Swiztland
        "denmark/superliga": 5,             # Denmark
        "ukraine/premier-league": 20,       # Ukraine
        "bulgaria/parva-liga": 2,           # Bulgaria
        "czech-republic/1-liga": 3,         # Chezch
        "croatia/1-hnl": 4 ,                # Croatia
        "hungary/otp-bank-liga": 10,        # Hungary
        "serbia/super-liga": 15             # Serbia
    }
    return switcher.get(argument, "null")

total_added_count = 0
def insert_odds(basic_match_href_url, match_date, home_team, away_team):
    global total_added_count
    three_way_url = basic_match_href_url + "#1X2;2" 
    OU_url  =  basic_match_href_url + "#over-under;2"
    AH_url = basic_match_href_url + "#ah;2"  
    
    home_team_name = home_team
    away_team_name = away_team
    sql = f"SELECT team_id from team_list where team_name_odd = '{home_team_name}'"
    mycursor.execute(sql)
    result = mycursor.fetchall()

    if result:
        home_team_id = result[0][0]
        sql = f"SELECT match_id from season_match_plan where date = '{match_date}' and home_team_id = {home_team_id}"
        mycursor.execute(sql)
        result  =  mycursor.fetchall()
        if result:
            match_id = result[0][0]
            print("        match_id is ", match_id)
            sql = f"select * from odds where match_id = {match_id} and bookmaker_id = 11"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            ################## inserting new odds data #######################################################################
            
            if (result and result[0][3] != 0) and (result and str(result[0][42]) >= match_date):    
                # that wasnt resch game's odd
                print("         # No need to insert")
                return "No update"
            else:
                if result:
                        sql = f"delete from odds where match_id = {match_id} and bookmaker_id = 11"
                        mycursor.execute(sql)
                        mydb.commit()
                        print("        * deleted existing one row !")
                odd_price = get_odds(three_way_url, OU_url, AH_url)
                print("        " , odd_price)
                updated_at = datetime.today().strftime('%Y-%m-%d')
                print(f"       inserted at {updated_at}")
                sql = f"INSERT INTO odds (match_id, bookmaker_id, Home, Draw, Away, Over2d5, Under2d5, AH2_1, AH2_2, AH1d75_1, AH1d75_2, AH1d5_1, AH1d5_2 , AH1d25_1, AH1d25_2, AH1_1, AH1_2, AH0d75_1, AH0d75_2, AH0d5_1, AH0d5_2, AH0d25_1, AH0d25_2, AH0_1, AH0_2 , AH_p0d25_1 , AH_p0d25_2, AH_p0d5_1, AH_p0d5_2, AH_p0d75_1 , AH_p0d75_2, AH_p1_1, AH_p1_2, AH_p1d25_1, AH_p1d25_2, AH_p1d5_1, AH_p1d5_2, AH_p1d75_1, AH_p1d75_2, AH_p2_1, AH_p2_2 , updated_at)"  \
			    f"VALUES ({match_id}, 11, {odd_price['3way']['highest'][0]}, {odd_price['3way']['highest'][1]}, {odd_price['3way']['highest'][2]}, {odd_price['O/U']['highest'][0]}, {odd_price['O/U']['highest'][1]}, " \
                f"{odd_price['AH']['AH_2']['highest'][0]} , {odd_price['AH']['AH_2']['highest'][1]} ,{odd_price['AH']['AH_1.75']['highest'][0]} , {odd_price['AH']['AH_1.75']['highest'][1]} , " \
                f"{odd_price['AH']['AH_1.5']['highest'][0]} , {odd_price['AH']['AH_1.5']['highest'][1]} ,{odd_price['AH']['AH_1.25']['highest'][0]} , {odd_price['AH']['AH_1.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_1']['highest'][0]} , {odd_price['AH']['AH_1']['highest'][1]} ,{odd_price['AH']['AH_0.75']['highest'][0]} , {odd_price['AH']['AH_0.75']['highest'][1]} , " \
                f"{odd_price['AH']['AH_0.5']['highest'][0]} , {odd_price['AH']['AH_0.5']['highest'][1]} ,{odd_price['AH']['AH_0.25']['highest'][0]} , {odd_price['AH']['AH_0.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_0']['highest'][0]} , {odd_price['AH']['AH_0']['highest'][1]} , {odd_price['AH']['AH_p0.25']['highest'][0]} , {odd_price['AH']['AH_p0.25']['highest'][1]} , " \
                f"{odd_price['AH']['AH_p0.5']['highest'][0]} , {odd_price['AH']['AH_p0.5']['highest'][1]},{odd_price['AH']['AH_p0.75']['highest'][0]} , {odd_price['AH']['AH_p0.75']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p1']['highest'][0]} , {odd_price['AH']['AH_p1']['highest'][1]},{odd_price['AH']['AH_p1.25']['highest'][0]} , {odd_price['AH']['AH_p1.25']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p1.5']['highest'][0]} , {odd_price['AH']['AH_p1.5']['highest'][1]},{odd_price['AH']['AH_p1.75']['highest'][0]} , {odd_price['AH']['AH_p1.75']['highest'][1]} , "  \
                f"{odd_price['AH']['AH_p2']['highest'][0]} , {odd_price['AH']['AH_p2']['highest'][1]} , '{updated_at}') "
                mycursor.execute(sql)
                mydb.commit()

                total_added_count += 1
                print("        # insert successful! ")
                return "update"
            ######################### updating Asian Handicap on existing rows #################################################################

            # odd_price = get_odds(three_way_url, OU_url, AH_url)
            # print("        " , odd_price)

            # sql = f"UPDATE odds set  AH2_1 = {odd_price['AH']['AH_2']['highest'][0]} , AH2_2 = {odd_price['AH']['AH_2']['highest'][1]} , " \
            # f"AH1d75_1 = {odd_price['AH']['AH_1.75']['highest'][0]} , AH1d75_2 = {odd_price['AH']['AH_1.75']['highest'][1]} ," \
            # f"AH1d5_1 = {odd_price['AH']['AH_1.5']['highest'][0]} , AH1d5_2 = {odd_price['AH']['AH_1.5']['highest'][1]} ," \
            # f"AH1d25_1 = {odd_price['AH']['AH_1.25']['highest'][0]} , AH1d25_2 = {odd_price['AH']['AH_1.25']['highest'][1]} ," \
            # f"AH1_1 = {odd_price['AH']['AH_1']['highest'][0]} , AH1_2 = {odd_price['AH']['AH_1']['highest'][1]} ," \
            # f"AH0d75_1 = {odd_price['AH']['AH_0.75']['highest'][0]} , AH0d75_2 = {odd_price['AH']['AH_0.75']['highest'][1]} ," \
            # f"AH0d5_1 = {odd_price['AH']['AH_0.5']['highest'][0]} , AH0d5_2 = {odd_price['AH']['AH_0.5']['highest'][1]} ," \
            # f"AH0d25_1 = {odd_price['AH']['AH_0.25']['highest'][0]} , AH0d25_2 = {odd_price['AH']['AH_0.25']['highest'][1]} ," \
            # f"AH0_1 = {odd_price['AH']['AH_0']['highest'][0]} , AH0_2 = {odd_price['AH']['AH_0']['highest'][1]} ," \
            # f"AH_p0d25_1 = {odd_price['AH']['AH_p0.25']['highest'][0]} , AH_p0d25_2 = {odd_price['AH']['AH_p0.25']['highest'][1]} ," \
            # f"AH_p0d5_1 = {odd_price['AH']['AH_p0.5']['highest'][0]} , AH_p0d5_2 = {odd_price['AH']['AH_p0.5']['highest'][1]} ," \
            # f"AH_p0d75_1 = {odd_price['AH']['AH_p0.75']['highest'][0]} , AH_p0d75_2 = {odd_price['AH']['AH_p0.75']['highest'][1]} ," \
            # f"AH_p1_1 = {odd_price['AH']['AH_p1']['highest'][0]} , AH_p1_2 = {odd_price['AH']['AH_p1']['highest'][1]} ," \
            # f"AH_p1d25_1 = {odd_price['AH']['AH_p1.25']['highest'][0]} , AH_p1d25_2 = {odd_price['AH']['AH_p1.25']['highest'][1]} ," \
            # f"AH_p1d5_1 = {odd_price['AH']['AH_p1.5']['highest'][0]} , AH_p1d5_2 = {odd_price['AH']['AH_p1.5']['highest'][1]} ," \
            # f"AH_p1d75_1 = {odd_price['AH']['AH_p1.75']['highest'][0]} , AH_p1d75_2 = {odd_price['AH']['AH_p1.75']['highest'][1]} ," \
            # f"AH_p2_1 = {odd_price['AH']['AH_p2']['highest'][0]} , AH_p2_2 = {odd_price['AH']['AH_p2']['highest'][1]} " \
            # f"WHERE match_id = {match_id} and bookmaker_id = 11"
            # mycursor.execute(sql)
            # mydb.commit()
            
            # print("        # Asian Handicap added on existing columns! ")

        else:
            print("        # Can't find match id in season_match_plan table.")
    else:
        print("        # Can't find team_id in team_list.")
    
def get_odds(turl, OU_url , AH_url):
    odd_price = {"3way": {}, "O/U": {}, "AH": {}}
   
    highest_list = [] 
   
    ################################ driver setting part start############################
    driver1 = webdriver.Chrome(driverpath, options=chrome_options)
    driver1.get(turl)
    driver1.refresh()
    time.sleep(0.5)
    ################################ driver setting part End #############################`
    
    ############## 3 way result ###################################################################
    print("        * start scraping 1X2 data --------------------")
    main = driver1.find_element(By.TAG_NAME, 'main')
    time.sleep(0.5)
    high_elemnet = main.find_elements(By.TAG_NAME, '.bg-gray-light')
    high_elemnet = high_elemnet[2]

    if high_elemnet:
        av_values = high_elemnet.find_elements(By.TAG_NAME, ".justify-center.font-bold")
        if len(av_values) > 2:
          for i in range(0, 3):
            if av_values[i].text == "-" or av_values[i].text == "":
              highest_list.append("0")
            else: 
              highest_list.append(av_values[i].text)

    three_way = {"highest": highest_list}
    # print("   three_way ", three_way)
    odd_price['3way'] = three_way
    
    # ############### Over / Under result ############################################################

    print("        * start scraping Over Under data --------------------")
    driver1.get(OU_url)
    driver1.refresh()
    time.sleep(0.5)
    # wait = WebDriverWait(driver1, 20)
    # wait.until(EC.presence_of_element_located((By.ID, 'odds-data-table')))
    
    highest_list = []
    main = driver1.find_element(By.TAG_NAME, 'main')
    # wait = WebDriverWait(driver1, 20)
    # wait.until(EC.presence_of_element_located((By.TAG_NAME, '.relative.flex.flex-col')))
    time.sleep(2)
    element_OU = main.find_elements(By.TAG_NAME , '.relative.flex.flex-col')

    if len(element_OU) == 0:
        print("    Couldn't find Over 2.5 values !")
        highest_list = ['0', '0']
    else:
        for element in element_OU:
            OU_name = element.find_element(By.TAG_NAME, 'p')
            OU_name =  OU_name.text.strip()
            if OU_name == "Over/Under +2.5":
                av_values = element.find_elements_by_class_name("gradient-green-added-border")
                if len(av_values) > 1:
                    for i in  range(0, 2):
                        if av_values[i].text == "-" or av_values[i].text == "":
                            highest_list.append("0")
                        else:
                            highest_list.append(av_values[i].text)
                else:
                    highest_list = ['0', '0']
                break
      
    O_U = {"highest": highest_list}
    # print("   OU ", O_U)
    odd_price['O/U'] = O_U
    ############### Asian Handicap result ############################################################
   
    print("        * start scraping Asian Handicap data --------------------")
    AH_odds = {"AH_2":{}, "AH_1.75":{}, "AH_1.5":{}, "AH_1.25":{}, "AH_1":{}, "AH_0.75":{}, "AH_0.5":{}, "AH_0.25":{}, "AH_0":{} , 
    "AH_p2":{}, "AH_p1.75":{}, "AH_p1.5":{}, "AH_p1.25":{}, "AH_p1":{}, "AH_p0.75":{}, "AH_p0.5":{}, "AH_p0.25":{}}
    driver1.get(AH_url)
    driver1.refresh()
    time.sleep(0.5)

    main = driver1.find_element(By.TAG_NAME, 'main')
    time.sleep(1.5)
    AH_elements = main.find_elements(By.TAG_NAME , '.relative.flex.flex-col')

    if len(AH_elements) == 0:
        print("    Couldn't find AH values !")
        highest_list = ['0', '0']
    else:
        ah_values_object = {}
        for index in range(0, len(AH_elements)):
            highest_list = []
            element = AH_elements[index]
            ah_name = element.find_element(By.TAG_NAME, 'p')
            ah_name =  ah_name.text.strip()
            av_values = element.find_elements_by_class_name("gradient-green-added-border")
            if len(av_values) > 1:
                for i in  range(0, 2):
                    if av_values[i].text == '-' or av_values[i].text == '':
                        highest_list.append('0')
                    else:
                        highest_list.append(av_values[i].text)
            else:
                highest_list = ['0', '0']
            ah_values_object[ah_name] = {'highest': highest_list}
        
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
    elif 'Yesterday' in date_txt:
        yesterday = datetime.now() - timedelta(1)
        return datetime.strftime(yesterday, '%Y-%m-%d')
    else:
        date_part = date_txt.split(' ');
        return date_part[2] + "-" +switch_month(date_part[1]) + '-' + date_part[0]

def insert_price_to_matchplan(league, season, breakFlag = True, startPage = None):
      
    driver = webdriver.Chrome(driverpath, options=chrome_options)
    current_season = False

    ###################### going to result page ###############################
    if season == "":
        page_url = site_url + "soccer/" + league + season + "/results/"
        current_season = True
    else:
        page_url = site_url +"soccer/" + league + "-" + season + "/results/"
    driver.get(page_url)

    time.sleep(2)
    pagination = driver.find_elements(By.ID, 'pagination')
  
    if len(pagination):
        pagenumber = len(pagination[0].find_elements(By.TAG_NAME, 'a')) + 1
    else:
        pagenumber = 1

    # print("whole page count", pagenumber)
    breakflag = 0
    if startPage ==  None:
          startPage = 1
    for page in range(startPage, 2):
        search_url = page_url + '#/page/' + str(page) + '/'
        # print(search_url)
        
        print(f"----------------{league} - {season} {page}page start--------------------------------")
        
        driver.get(search_url)    
        driver.refresh()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'main'))
        )
        main = driver.find_element(By.TAG_NAME, 'main')                # get main components

        index = 0
        match_date = ""
        
        div_element = main.find_element(By.CLASS_NAME, 'w-full')
        all_elements = div_element.find_elements(By.CSS_SELECTOR, '.flex.flex-col.w-full.text-xs')
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
                    print(f"    --- {league} {season} {page} page { str(int(index/2))} th match start---")
                    main_text_element = group_element.find_element(By.CSS_SELECTOR, '.relative.w-full')
                    home_team = main_text_element.find_elements_by_tag_name("a")[0].get_attribute('title')
                    away_team = main_text_element.find_elements_by_tag_name("a")[1].get_attribute('title')
                    print(f"        {match_date} , {home_team} - {away_team} ")
                    hrefUrl = main_text_element.find_elements_by_tag_name("a")[1].get_attribute('href')
                    status = insert_odds(hrefUrl, match_date, home_team, away_team )
                    if current_season & (status == "No update"):
                            print("     * No need to update , this is already inserted!")
                            breakflag = 1
                            if breakFlag:
                                break
            index  += 1
        if breakflag:
            breakflag = 0
            break
        print(f"---------------- {league} - {season} {page}page End--------------------------------")
    driver.quit()

insert_price_to_matchplan("england/premier-league",   "")
insert_price_to_matchplan("spain/laliga",             "")
insert_price_to_matchplan("germany/bundesliga",       "")
insert_price_to_matchplan("italy/serie-a",            "")
insert_price_to_matchplan("france/ligue-1",           "")
insert_price_to_matchplan("netherlands/eredivisie",   "")
insert_price_to_matchplan("austria/tipico-bundesliga","")
insert_price_to_matchplan("portugal/primeira-liga",   "")
insert_price_to_matchplan("greece/super-league",      "")
insert_price_to_matchplan("turkey/super-lig",         "")
insert_price_to_matchplan("norway/eliteserien",       "")
insert_price_to_matchplan("sweden/allsvenskan",       "")
insert_price_to_matchplan("switzerland/super-league", "")
insert_price_to_matchplan("denmark/superliga",        "")
insert_price_to_matchplan("ukraine/premier-league",   "")
insert_price_to_matchplan("bulgaria/parva-liga",      "")
insert_price_to_matchplan("czech-republic/1-liga",    "")
insert_price_to_matchplan("croatia/1-hnl",            "")
insert_price_to_matchplan("hungary/otp-bank-liga",    "")
# insert_price_to_matchplan("serbia/super-liga",        "")

print(" Total added count is : ", total_added_count)