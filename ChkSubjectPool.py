#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 15:27:50 2018

@author: halfsong
"""
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sona import ID,PW
import time
import telegram
import traceback
import datetime
import signal
import json
import subprocess

VERSION = 1.2
NOTES = '''
        update chat_ids everytime it crawls
        '''

interval = 2 #min

token='xxxxx'

chrome_dir = '/usr/local/bin/chromedriver'

cur_d = os.path.dirname(__file__)
join = os.path.join

with open(join(cur_d,'chat_ids.json'),'r') as f:
    chat_ids = json.load(f)


bot = telegram.Bot(token=token)

today = set()

def crawl():
    global chat_ids
    with open(join(cur_d,'chat_ids.json'),'r') as f:
        chat_ids = json.load(f)

    options = webdriver.ChromeOptions()
    
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_dir, chrome_options=options)
    driver.implicitly_wait(2)

    driver.get('https://uvt.sona-systems.com/default.aspx')
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_userid"]').send_keys(ID)
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_pw"]').send_keys(PW)
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_default_auth_button"]').click()

    
    driver.find_element_by_xpath('//*[@id="lnkStudySignupLink"]').click()
    table = driver.find_element_by_xpath('//*[@id="primary-content"]/section/div[2]/div/section/div/div/table')
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for r in rows[1:]:
        info = [td.text for td in r.find_elements(By.TAG_NAME,'td')]
        data.append(info)
    
    if len(data) ==0:
        data = ['no data available']
        return data
   
    global today
    for d in data:
        textmsg = u'{}.\n{}.\n{}'.format(d[2],d[1],d[0])
        if textmsg not in today:
            send_msg(bot,textmsg)
            today.add(textmsg)
    
    print len(data)
    
    driver.service.process.send_signal(signal.SIGTERM)
    driver.quit()
    return data
            
def send_msg(bot,msg,target=None):
    if target:
        bot.sendMessage(chat_id=target,text=msg)
        return
    for chat_id in chat_ids:
        bot.sendMessage(chat_id=chat_id, text=msg)
    
def main():
    while True:
        try:
            now = datetime.datetime.now().hour
            if now > 22 or now < 6:
                global today
                today = set()
                time.sleep(3600)
                continue
            crawl()
        except:
            bot.sendMessage(chat_id=chat_ids[0], text=traceback.format_exc())
        subprocess.call('pkill chrome',shell=True)
        time.sleep(60 * interval)
        
        
if __name__ == "__main__":
    print 'BOT Restarted\n v{}\nNotes:{}'.format(VERSION,NOTES)
    # send_msg(bot,'BOT Restarted\n v{}\nNotes:{}'.format(VERSION,NOTES))
    main()