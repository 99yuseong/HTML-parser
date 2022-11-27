from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
from sys import exit
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


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

def Efind_element(option, value):
    try: 
        if option == "class":
            return driver.find_element(By.CLASS_NAME, value)
        elif option == "xpath":
            return driver.find_element(By.XPATH, value)
        elif option == "id":
            return driver.find_element(By.ID, value)
    except NoSuchElementException:
        print()
        print("Error: Cannot search on the map. Do not move the window")
        print("Program terminated")
        exit(1)
    
def dateGenerator(data: str): # Conver format of time crawled 
    data = data.split(' ', 1)
    period = data[0]
    data = data[1].split(' ', 1)
    data = data[0]
    if period == "오전":
        data = data + " AM"
    else:
        data = data + " PM"

    date = datetime.today()
    date = date.strftime("%Y-%m-%d ") + data

    format = "%Y-%m-%d %I:%M %p"
    dest_time = datetime.strptime(date, format) 
    return dest_time

def dateGenerator_input(data: str): # Conver format of the input time(deadline)
    date = datetime.today()
    date = date.strftime("%Y-%m-%d ") + data
    
    format = "%Y-%m-%d %H:%M"
    dest_time = datetime.strptime(date, format) 
    return dest_time

def timeVerification(deadline): # Check if the input time is available
    timeFormatValid = False
    while not timeFormatValid:
        regex = re.compile('[01][0-9]|2[0-3]:[0-5][0-9]')
        timeFormatValid = regex.match(deadline)
        if not timeFormatValid:
            return False
        else:
            return True
            
def locationVerification(start, goal): # Check if the input departure and arrival is available
    startValid = UserInput['start']['valid']
    goalValid = UserInput['goal']['valid']
    valid = startValid and goalValid
    
    
    while not valid:  
        driver.get('https://map.naver.com/v5/?c=14151527.5539962,4467341.8213876,15,0,0,0,dh')  
        driver.implicitly_wait(7)

        if not startValid: # Search the input departure on Naver map to check
            print("Checking Departure is Valid...")
            Efind_element("class", 'input_search').clear()
            Efind_element("class", 'input_search').send_keys(start)
            pyautogui.press('enter')
            time.sleep(0.3)
            try:
                frame = Efind_element("id", 'searchIframe')
                driver.switch_to.frame(frame)
                start = Efind_element("class", 'place_bluelink').text
                print("Departure Valid!")
                UserInput['start']['val'] = start
                UserInput['start']['valid'] = True
            except:
                print("Can't find Departure")
            driver.switch_to.parent_frame()
                
        if not goalValid: # Search the input arrival on Naver map to check
            print("Checking Goal is Valid...")
            Efind_element("class", 'input_search').clear()
            Efind_element("class", 'input_search').send_keys(goal)
            pyautogui.press('enter')
            time.sleep(0.3)
            try:
                frame = Efind_element("id", 'searchIframe')
                driver.switch_to.frame(frame)
                goal = Efind_element("class", 'place_bluelink').text
                print("Goal Valid!")
                UserInput['goal']['val'] = goal
                UserInput['goal']['valid'] = True
            except:
                print("Can't find Goal")
            driver.switch_to.parent_frame()
                
        valid = UserInput['start']['valid'] and UserInput['goal']['valid']
       
        if not valid:
            driver.quit()
            return False
        else: # if both of then are available,
            print("Checking complete! Your inputs are valid")
            print()
            return True

def crawlingMap():
    print("Finding routes...")
    driver.get('https://map.naver.com/v5/directions/-/-/-/transit?c=14120592.9969593,4195075.5803126,14.9,0,0,0,dh')
    delay = 5
    driver.implicitly_wait(delay)

    # 출발지 입력
    Efind_element("xpath", '//*[@id="directionStart0"]').send_keys(UserInput['start']['val'])
    time.sleep(0.02)
    pyautogui.press('enter')
    time.sleep(0.3)

    #도착지 입력
    Efind_element("xpath",'//*[@id="directionGoal1"]').send_keys(UserInput['goal']['val'])
    time.sleep(0.02)
    pyautogui.press('enter')
    driver.implicitly_wait(3)

    #길찾기 버튼 클릭
    Efind_element("xpath", '//*[@id="container"]/shrinkable-layout/div/directions-layout/directions-result/div[1]/div/directions-search/div[2]/button[2]').click()
    driver.implicitly_wait(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find('span', {'class' : 'summary_info ng-star-inserted'}).get_text()
    print()
    return data


if __name__ == "__main__": 
    # deadline = input("Enter when you must arrive (ex 16:00): ")
    # start = input("Enter where you go: ")
    # goal = input("Enter where you leave: ")
    deadline = "15:40"
    start = "광주과학기술원"
    goal = "LC타워"
    
    driver = set_chrome_driver()
    print("Program started. DO NOT move your mouse and keyboard!!")
    print()
    
    if timeVerification(deadline):
        deadline = dateGenerator_input(deadline)
    else:
        print('Time Format is invalid')
        exit(1)
         
    if not locationVerification(start, goal):
        exit(1)
        
    destTime = dateGenerator(crawlingMap())
    
    if deadline > destTime:
        # find out how much time is required by subtraction
        # The time required can be overestimated if this program is used late at night
        # since There are no buses
        timeLeft = deadline - destTime
        temp = datetime.now() + timeLeft
        print("You have to leave at least", temp.strftime("%H:%M"))
    elif deadline == destTime:
        print("You must leave now!!!")
    else:
        print("You are already late...")
    


    
    
    
    
