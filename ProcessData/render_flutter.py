from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pyclip
import time
from curtsies.fmtfuncs import red, green, yellow
from PIL import Image
import os
from tqdm import tqdm
from playsound import playsound
import sys
import tty
import termios

def getchar():
    fd = sys.stdin.fileno()
    attr = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    except:
        print('could not find')
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, attr)

# ctrl + i skip => \x09
# ctrl + n next => \x0E

SKIP = '\x09'
NEXT = '\x0E'

PATH = '/home/saatwik/Desktop/My projects/FlutterGenerator/driver/chromedriver'

DIR = 'repos'

chromeOptions = Options()
chromeOptions.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(PATH, options=chromeOptions)

driver.maximize_window()
driver.get('https://www.dartpad.dev/')

# WIDTH OF OUTPUT
driver.execute_script("document.getElementById('editor-panel').style['flex-basis'] = 'calc(75% - 3px)';")
driver.execute_script("document.getElementById('output-panel').style['flex-basis'] = 'calc(25% - 3px)';")

first = True

ind = 0

oRendered = open('rendered_filenames.txt', 'r').readlines()
rendered = []
for x in oRendered:
    x = x.replace('\n', '')
    rendered.append(x)

for repo in tqdm(os.listdir(DIR)):

    try:

        print(green(str(ind)))

        ind += 1
        if ind <= 1164:
            continue

        files = []

        # COLLECTING ALL FILE PATHS
        for dirPath, subdir, file in os.walk(os.path.join(DIR, repo, 'lib')):
            for fs in file:
                files.append(os.path.join(dirPath, fs))

        s = ''
        with open('total_files.txt', 'r') as totalRead:
            number = int(totalRead.read()) + len(files)
            s = str(number)

        with open('total_files.txt', 'w') as totalWrite:
            totalWrite.write(s)

        for file in files:

            if file in rendered:
                print(green('SKIPPING............'))
                continue

            if file.endswith('dart'):

                try:

                    print(yellow(file))

                    content_to_be_pasted = open(file, 'r').read()
                    pyclip.copy(str(content_to_be_pasted))

                    try:

                        driver.find_element(By.XPATH, '//*[@id="editor-host"]/div/div[6]/div[1]/div/div/div/div[5]/div[1]').click()
                        ac = ActionChains(driver)
                        ac.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        ac.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

                    except:
                        print(red('some error'))
                        print(ind)
                        continue

                    time.sleep(3)

                    if first:
                        time.sleep(3)
                        first = False

                    # REMOVE ISSUES POPUP WHILE CAPTURING THE IMAGE
                    issues = driver.find_element(By.ID, 'issues-toggle')
                    if issues.text == 'show':
                        issues.click()

                    try:

                        issues_expanded = driver.find_elements(By.CSS_SELECTOR ,'.issuelabel')
                        error_found = False
                        issue_index = 0
                        skip = False
                        for i in issues_expanded:
                            if i.text == 'error':
                                issue_index += 1

                    except:
                        continue

                    
                    if issue_index > 10:
                        error_found = True
                    else:
                        # playsound('audio.mp3')
                        # while True:
                        #     c = getchar()
                        #     if c == NEXT:
                        #         break
                        #     elif c == SKIP:
                        #         skip = True
                        #         break
                        if issue_index != 0:
                            with open('render_list.txt', 'a') as list:
                                list.write(file + '\n')
                            skip = True

                    if error_found or skip:
                        continue

                    try:
                    
                        issues = driver.find_element(By.ID, 'issues-toggle')
                        if issues.text == 'hide':
                            issues.click()

                        format = driver.find_element(By.ID, 'format-button')
                        format.click()

                        driver.find_element(By.ID, 'run-button').click()

                    except:
                        continue

                    time.sleep(10)

                    try:

                        elem2 = driver.find_element(By.XPATH, '//*[@id="editor-host"]/div/div[6]/div[1]/div/div/div/div[5]/div[1]/pre/span')
                        elem2.click()
                        ac2 = ActionChains(driver)
                        ac2.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        ac2.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()

                    except:
                        continue

                    text = str(pyclip.paste())
                    with open(file, 'w') as dartFile:
                        dartFile.write(text)

                    try:
                        driver.save_screenshot('screenshot.png')
                        im = Image.open('screenshot.png')
                        width, height = im.size
                    except:
                        os.remove('screenshot.png')
                        continue
                    
                    # OUTPUT_PANEL {'height': 836, 'width': 477}
                    # HEADER {'height': 48, 'width': 1920}
                    # FOOTER {'height': 40, 'width': 1920}

                    left = width - 477
                    top = 48
                    right = width
                    bottom = height - 40
                    
                    im = im.crop((left, top, right, bottom))
                    im.save(file.replace('.dart', '.png'))

                    os.remove('screenshot.png')


                    # NO OF SUCCESSFUL RENDERS
                    st = ''
                    with open('rendered.txt', 'r') as renderedRead:
                        number = int(renderedRead.read()) + 1
                        st = str(number)

                    with open('rendered.txt', 'w') as renderedWrite:
                        renderedWrite.write(st)

                    # FILE NAME OF SUCCESSFUL RENDER
                    with open('rendered_filenames.txt', 'a') as renderedFiles:
                        renderedFiles.write(file + '\n')

                except Exception as e:
                    print(red(e))
                    continue

    except Exception as e:
        print(red(e))
        continue


driver.quit()