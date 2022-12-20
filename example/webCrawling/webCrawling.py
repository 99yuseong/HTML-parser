from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
from sys import exit, setrecursionlimit
from selenium.common.exceptions import NoSuchElementException

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from HTML import HTML


def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

UserInput = { # simple DB to store the verification result and location inputs
             'start' : { 
                 'valid' : False, 
                 'val': None 
                },
             'goal' : {
                 'valid' : False, 
                 'val' : None
                }
            }

def printLog(input): # let log be printed with timestamp
    timestamp = datetime.now()
    log = f'[{timestamp}] {input}'
    print(log)


 # Error handler for 'NoSuchElementException' caused by a method 'find_element'
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
        printLog("Error: Cannot search on the map. Do not move the window")
        printLog("Program terminated")
        exit(1)
    
# Conver format of time crawled (original format: 오전/오후 %H:%M 도착)
def dateGenerator(data: str): 
    data = data.split(' ', 1)
    period = data[0] #split '오전/오후' and store it in a variable
    data = data[1].split(' ', 1)
    data = data[0] # throw out a meaningless word '도착' 
    if period == "오전": # Korean to English 
        data = data + " AM"
    else:
        data = data + " PM"

    date = datetime.today()
    date = date.strftime("%Y-%m-%d ") + data # add date information in front of the input

    format = "%Y-%m-%d %I:%M %p"
    dest_time = datetime.strptime(date, format) # convert 'str' type into 'datetime' type
    return dest_time

def dateGenerator_input(data: str): # Conver format of the input time(deadline)
    date = datetime.today()
    date = date.strftime("%Y-%m-%d ") + data
    
    format = "%Y-%m-%d %H:%M"
    dest_time = datetime.strptime(date, format) 
    return dest_time

def timeVerification(deadline): # Check if the input time is available
    timeFormatValid = False
    if  1 < datetime.now().hour < 6:
        printLog("Error: You cannot use this program while bus is unavailable")
        exit(1)
    while not timeFormatValid:
        regex = re.compile('[01][0-9]|2[0-3]:[0-5][0-9]') #regular expression of time input
        timeFormatValid = regex.match(deadline) 
        if not timeFormatValid: #if not matched, terminate the program
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
        
        # Search the input departure on Naver map to check if the given location is available
        if not startValid: 
            printLog("Checking Departure is Valid...")
            Efind_element("class", 'input_search').clear()
            Efind_element("class", 'input_search').send_keys(start)
            pyautogui.press('enter')
            time.sleep(0.3)
            try:
                frame = Efind_element("id", 'searchIframe')
                driver.switch_to.frame(frame)
                start = Efind_element("class", 'place_bluelink').text
                printLog("Departure Valid!")
                UserInput['start']['val'] = start
                UserInput['start']['valid'] = True
            except:
                printLog("Can't find Departure")
            driver.switch_to.parent_frame()
            
        # Search the input arrival on Naver map to check         
        if not goalValid: 
            printLog("Checking Goal is Valid...")
            Efind_element("class", 'input_search').clear()
            Efind_element("class", 'input_search').send_keys(goal)
            pyautogui.press('enter')
            time.sleep(0.3)
            try:
                frame = Efind_element("id", 'searchIframe')
                driver.switch_to.frame(frame)
                goal = Efind_element("class", 'place_bluelink').text
                printLog("Goal Valid!")
                UserInput['goal']['val'] = goal
                UserInput['goal']['valid'] = True
            except:
                printLog("Can't find Goal")
            driver.switch_to.parent_frame()
                
        valid = UserInput['start']['valid'] and UserInput['goal']['valid']
       
        if not valid:
            driver.quit()
            return False
        else: # if both of then are available,
            printLog("Checking complete! Your inputs are valid")
            printLog("")
            return True

def crawlingMap():
    printLog("Finding routes...")
    driver.get('https://map.naver.com/v5/directions/-/-/-/transit?c=14120592.9969593,4195075.5803126,14.9,0,0,0,dh')
    delay = 5
    driver.implicitly_wait(delay)

    # Entering the departure
    Efind_element("xpath", '//*[@id="directionStart0"]').send_keys(UserInput['start']['val'])
    time.sleep(0.02)
    pyautogui.press('enter')
    time.sleep(0.3)

    #Entering the destination
    Efind_element("xpath",'//*[@id="directionGoal1"]').send_keys(UserInput['goal']['val'])
    time.sleep(0.02)
    pyautogui.press('enter')
    driver.implicitly_wait(3)

    #Click the result button
    Efind_element("xpath", '//*[@id="container"]/shrinkable-layout/div/directions-layout/directions-result/div[1]/div/directions-search/div[2]/button[2]').click()
    time.sleep(3)
    printLog("")
    html = driver.page_source   
    return html


# Parsing html source code using our own tokenizer & parser
def createCompiler():
    return HTML("example/source.txt")

def timeSpent(com): # expectation time to arrive (format: 오전/오후 %H:%M 도착)
    text_node1 = com.search(['span', 'class', '"summary_info ng-star-inserted"'])
    res1 = com.getTextNode(text_node1).split('$')
    return(res1[1])

def walkingTime(com): # Time you have to walk to reach the first bus stop (format: %M)
    # soup = BeautifulSoup(html, 'html.parser')
    # data = soup.find('span', {'class' : 'value ng-star-inserted'}).get_text()
    text_node2 = com.search(['span', 'class', '"value ng-star-inserted"'])
    res2 = com.getTextNode(text_node2).split('$')
    data2 = datetime.strptime(res2[1], "%M")
    return timedelta(minutes=data2.minute)

def busName(com): # Bus name (ex 첨단30)
    # soup = BeautifulSoup(html, 'html.parser')
    text_node3 = com.search(['em', 'class', '"label"'])
    res3 = com.getTextNode(text_node3).split('$')
    return res3[1]

if __name__ == "__main__": 
    start = "광주과학기술원" # fixed input: GIST
    goal = input("Enter your destination: ")
    deadline = input("Enter when you must arrive (ex 16:00): ")
    
    driver = set_chrome_driver() # set and start the browser driver
    printLog("Program started. DO NOT move your mouse and keyboard!!")
    print()
    
    if timeVerification(deadline): # Time format verification
        deadline = dateGenerator_input(deadline) # if so, convert the given time into time format fit to python
    else:
        printLog('Time Format is invalid')
        exit(1)
         
    if not locationVerification(start, goal): # Location format verification 
        exit(1)
        
        
    html = crawlingMap() # crawling whole html source code from browser
    text_file = open("example/source.txt", "w", encoding='UTF-8')
    n = text_file.write(html)
    text_file.close()
    
    compiler = createCompiler()
    
    # automatically write a visible DOM tree in text file
    # compiler.print_dom_tree("DomTree.txt")
    
    
    destTime = dateGenerator(timeSpent(compiler))  # tentative arrival time given by Naver map 
    walkTime = walkingTime(compiler) # Time to reach the bus stop 
    bus = busName(compiler) # Bus name and number to take 
    printLog("Parsing Complete")
    
    
    if deadline > destTime:
        # find out how much time is required by subtraction
        # The time required can be overestimated if this program is used late at night
        # since There are no buses
        timeLeft = deadline - destTime - walkTime # Time to arrive in destination from first bus stop
        temp = datetime.now() + timeLeft # time limit to reach the bus stop for not being late 
        text = f'You need to take {bus} bus at leat {temp.strftime("%H:%M")}'
        printLog(text)
    elif deadline == destTime:
        printLog("You must leave now! RUNNN!!!")
    else:
        printLog("You are already late… ")
        printLog("Take a taxi not to lose your friends!!")