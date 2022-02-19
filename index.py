# -*- coding: utf-8 -*-    
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

resolution = c['resolution']
print(resolution)

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

# [{'left': 0, 'top': 0, 'width': 3000, 'height': 2560}, {'left': 1080, 'top': 0, 'width': 1920, 'height': 1080}, {'left': 0, 'top': 0, 'width': 1080, 'height': 2560}]
def moveTo(x,y,t):
    pyautogui.moveTo(x + diff_monitor,y,t)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./targets/'):
    global monitor_size
    pathSize =  dir_path + monitor_size + "/"
    print("PATH: ", pathSize)
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
        # Grab the data
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printScreen()
    # print("IMG", img)
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
        # print("POSITION: ", x,y,w,h)
        # [793 790 335  41]
        moveTo(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

    return False

def scroll(images):
    
    scroll = positions(images['scroll-spaceship'], threshold = 1)
    x,y,w,h = scroll[0]
    print(scroll, x,y,w,h)
    
#     if (len(commoms) == 0):
#         return
#     x,y,w,h = commoms[len(commoms)-1]
# #
#     moveToWithRandomness(x,y,1)
    empty_scrolls_attempts = c['scroll']['attemps']

    while(empty_scrolls_attempts >0):
      moveTo(x,y,1)
      if not c['scroll']['use_click_and_drag_instead_of_scroll']:
          pyautogui.scroll(-c['scroll']['size'])
      else:
          pyautogui.dragRel(0,-c['scroll']['click_and_drag_amount'],duration=1, button='left')
      empty_scrolls_attempts -= 1    



def main():
  printScreen()
  images = load_images()
  # scroll(images)

  while True:
    now = time.time()
    if(clickBtn(images['connect-wallet'], timeout=1)):
      print("Connected", now)
      if(clickBtn(images['sign'], timeout=1)):
        print("Sign", now)
    if(clickBtn(images['play'], timeout=1)):
      print("Clicked play", now)
    if(clickBtn(images['ok'], timeout=1)):
      print("Clicked ok", now)

    if(clickBtn(images['close'], timeout=0.2, threshold=0.9)):
      print("CLOSE")    

    if(clickBtn(images['no-ammo'], timeout=0.2)):
      print(pyautogui.position())
      if(clickBtn(images['remove-spaceship'], timeout=1)):
        print("Remove Spaceship", now)
    if(clickBtn(images['newest'], timeout=1)):
      if(clickBtn(images['max-ammo'], timeout=1,threshold = 0.9)):
        print("SET MAX AMMO", now)
    if(clickBtn(images['send-to-fight'], timeout=0.5, threshold=0.9)):
      print("send-to-fight", now)
      if(clickBtn(images['15-15'], timeout=0.2, threshold = 1)):
        if(clickBtn(images['fight-boss'], timeout=0.2)):
          print("send-to-boss", now)
    else:
      if(clickBtn(images['15-15'], timeout=0.2, threshold = 1)):
        if(clickBtn(images['fight-boss'], timeout=0.2)):
          print("send-to-boss", now)
    if(clickBtn(images['victory-confirm'], timeout=0.5)):
      print("victory-confirm", now)
    if(clickBtn(images['surrender-boss'], timeout=0.5, threshold = 1)):
      if(clickBtn(images['surrender'], timeout=0.5)):
       if(clickBtn(images['surrender-confirm'], timeout=0.5)):
        print("surrender-confirm", now)
    if(clickBtn(images['spaceship-empty'], timeout=0.5, threshold = 0.9)):
      print("spaceship-empty", now)    
      if(clickBtn(images['rocket'], timeout=0.5, threshold = 0.9)):
        print("SEND TO REPAIR", now)
    if(clickBtn(images['lose-confirm'], timeout=0.5, threshold = 0.9)):
      print("lose-confirm", now)


      
if __name__ == '__main__':
  main()