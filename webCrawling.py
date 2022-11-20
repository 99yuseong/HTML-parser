from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

UserInput = { 
             'start' : { 
                 'valid' : False, 
                 'val': None 
                },
             'goal' : {
                 'valid' : False, 
                 'val' : None
                }
            }

timeFormatValid = False
startValid = UserInput['start']['valid']
goalValid = UserInput['goal']['valid']
valid = startValid and goalValid
    
while not timeFormatValid:
    # deadline = input("Until When (ex 09:00): ")
    deadline = "09:00"
    regex = re.compile('[01][0-9]|2[0-3]:[0-5][0-9]')
    timeFormatValid = regex.match(deadline)
    if not timeFormatValid:
        print('Time Format is invalid')
    
while not valid:
    if not startValid:
        # start = input("Where's departure : ")
        start = "광주과학기술원"
    if not goalValid:
        # goal = input("Where to go : ")
        goal = "유스퀘어"
    
    driver = set_chrome_driver()
    driver.get('https://map.naver.com/v5/?c=14151527.5539962,4467341.8213876,15,0,0,0,dh')  
    driver.implicitly_wait(7)

    if not startValid:
        # time.strftime('%X')
        print("Checking Departure is Valid...")
        driver.find_element(By.CLASS_NAME, 'input_search').clear()
        driver.find_element(By.CLASS_NAME, 'input_search').send_keys(start)
        pyautogui.press('enter')
        time.sleep(0.3)
        try:
            frame = driver.find_element(By.ID, 'searchIframe')
            driver.switch_to.frame(frame)
            start = driver.find_element(By.CLASS_NAME, 'place_bluelink').text
            print("Departure Valid!")
            UserInput['start']['val'] = start
            UserInput['start']['valid'] = True
        except:
            print("Can't find Departure")
        driver.switch_to.parent_frame()
            
    if not goalValid:
        print("Checking Goal is Valid...")
        driver.find_element(By.CLASS_NAME, 'input_search').clear()
        driver.find_element(By.CLASS_NAME, 'input_search').send_keys(goal)
        pyautogui.press('enter')
        time.sleep(0.3)
        try:
            frame = driver.find_element(By.ID, 'searchIframe')
            driver.switch_to.frame(frame)
            goal = driver.find_element(By.CLASS_NAME, 'place_bluelink').text
            print("Goal Valid!")
            UserInput['goal']['val'] = goal
            UserInput['goal']['valid'] = True
        except:
            print("Can't find Goal")
        driver.switch_to.parent_frame()
            
    valid = UserInput['start']['valid'] and UserInput['goal']['valid']
    
    if not valid:
        driver.quit()
 
print("Finding routes...")
driver.get('https://map.naver.com/v5/directions/-/-/-/transit?c=14120592.9969593,4195075.5803126,14.9,0,0,0,dh')
delay = 5
driver.implicitly_wait(delay)

# 출발지 입력
driver.find_element(By.XPATH, '//*[@id="directionStart0"]').send_keys(UserInput['start']['val'])
time.sleep(0.02)
pyautogui.press('enter')
time.sleep(0.3)

#도착지 입력
driver.find_element(By.XPATH,'//*[@id="directionGoal1"]').send_keys(UserInput['goal']['val'])
time.sleep(0.02)
pyautogui.press('enter')
time.sleep(0.3)

#길찾기 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="container"]/shrinkable-layout/div/directions-layout/directions-result/div[1]/div/directions-search/div[2]/button[2]').click()
time.sleep(3) 

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
route = soup.find_all('div', {'class' : 'route_summary_info_area'})