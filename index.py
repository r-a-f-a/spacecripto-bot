# -*- coding: utf-8 -*-    
from fileinput import close
from cv2 import cv2
from os import listdir
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

global monitor_size
global resolution 
images = []
diff_monitor = 0
login_attemps = 0
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']


print("""\
                   `. ___
                    __,' __`.                _..----....____
        __...--.'``;.   ,.   ;``--..__     .'    ,-._    _.-'
  _..-''-------'   `'   `'   `'     O ``-''._   (,;') _,'
,'________________                          \`-._`-','
 `._              ```````````------...___   '-.._'-:
    ```--.._      ,.                     ````--...__\-.
            `.--. `-`                       ____    |  |`
              `. `.                       ,'`````.  ;  ;`
                `._`.        __________   `.      \ '__/`
                   `-:._____/______/___/____`.     \  `
                               |       `._    `.    \ 
                               `._________`-.   `.   `.___
                                             SSt  `------'`
""")


print("""\
##################################################
#             WALLET FOR DONATE                  #
#------------------------------------------------#
#  0x3D2aEc88A2c73a23a25D4259A3B97740bBD8d53F    #
#------------------------------------------------#
#              PLEASE SUPPORT US                 #
##################################################
""")

resolution = c['resolution']
print("CONFIGURATION[RESOLUTION]:", resolution)

pyautogui.PAUSE = 1


def moveTo(x,y,t):
    pyautogui.moveTo(x + diff_monitor,y,t)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./targets/'):
    global monitor_size
    pathSize =  dir_path + monitor_size + "/"
    print("IMAGES FOLDER: ", pathSize)
    file_names = listdir(pathSize)
    targets = {}
    for file in file_names:
        path = pathSize + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

def printScreen():
    global monitor_size
    global diff_monitor
    with mss.mss() as sct:
        monitor =  sct.monitors[1]
        if( resolution["monitors"] > 1):
          selected = resolution["monitor_selected"]
          monitor =  sct.monitors[selected]
          diff_monitor = monitor["left"]
        sct_img = np.array(sct.grab(monitor))
        monitor_size = str(monitor['width']) + "x" + str(monitor['height'])
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printScreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles    
def clickBtn(img, timeout=3, threshold = ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)
      
        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
    
        moveTo(pos_click_x,pos_click_y,0.3)
        pyautogui.click()
        moveTo(pos_click_x + 100,pos_click_y + 100,0.3)
        return True

    return False

def checkImage(img, threshold=ct['default']):
    matches = positions(img, threshold=threshold)
    if(len(matches)==0):
        return False
    return True


def main():
  printScreen()
  images = load_images()

  while True:
    now = time.time()
    connect_wallet = checkImage(images['connect-wallet'])
    if connect_wallet:
      clickBtn(images['connect-wallet'], 0, 0.9)
      clickBtn(images['sign'], timeout=2)
      print("connect-wallet", now)

    play = checkImage(images['play'], threshold=0.9)
    if play:
      clickBtn(images['play'],0,0.9)  
      print("play", now)

    surrender = checkImage(images['surrender'], 0.9)
    genesis = checkImage(images['genesis'], 0.9)
    lose_confirm = checkImage(images['lose-confirm'], 0.9)
    close = checkImage(images['close'], 0.9)

    # CHECK IF YOU LOSE
    if(lose_confirm):
      clickBtn(images['lose-confirm'],0,0.9)
      print("lose-confirm", now)
      continue


    # CHECK IF NEED CLOSE
    if(close):
      clickBtn(images['close'],0,0.9)
      print("close", now)
      continue

    if(surrender):
      ## IN BATTLE
      # CHECK IF THE BATTLE IS OVER
      victory_confirm = checkImage(images['victory-confirm'], 0.8)
      if(victory_confirm):
        clickBtn(images['victory-confirm'],0,0.7)
        print("victory-confirm", now)
        continue
    
      
      # SURRENDER WHEN IT FINDS THE BOSS
      surrender_boss = checkImage(images['surrender-boss'], 1)  
      if(surrender_boss):
        clickBtn(images['surrender'], 0, 0.8)
        clickBtn(images['surrender-confirm'], 0.5, 0.8)
        print("surrender-confirm", now)
        continue

      # CHECK FOR EMPTY SPACESHIPS
      spaceship_empty = checkImage(images['spaceship-empty'], 0.95)
      if(spaceship_empty):
        clickBtn(images['rocket'], 0, 0.9)
        continue
      
  
    if(genesis):
      ## IN HOME
      team = checkImage(images['team'], 0.98)
      send_to_fight = checkImage(images['send-to-fight'], 0.9)
      # CHECK TARGET TEAM
      if(team):
        clickBtn(images['fight-boss'],0,0.8)
        print("fight-boss", now)
        continue
      else: 
        # SEND TO FIGHT
        if(send_to_fight):
          clickBtn(images['send-to-fight'],0,0.9)
          continue
        else:  
          # REMOVE SPACESHIPs
          remove = checkImage(images['remove-spaceship'], 0.9)
          if(remove): 
            clickBtn(images['remove-spaceship'],0,0.9)
            continue

      
if __name__ == '__main__':
  main()