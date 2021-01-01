import time
import pyautogui
import speech_recognition as sr
import os
import sys
import random
import datetime
import re
import tempfile
import subprocess
from queryAPI import bing, google, ibm
import PIL.ImageGrab

'''You'll need to update based on the coordinates of your setup'''

CHROME_LAUNCH_COMMAND = 'chromium-browser --disable-gpu --disable-software-rasterizer' # command to start the chrome browser

OPEN_CAPTCHA_ONLY = False # Open the captcha and stops. for debugging purposes
UNTIL_PASTE_URL = False # Open the captcha and stops. for debugging purposes

USE_CHROME_DEBUG_BROWSER = False # whether to control the browser via remote debug protocol
USE_INCOGNITO = False # whether to use an incognito window or not
USE_TEMP_USER_DATA_DIR = True # when a temporary user data dir is used, all cookies and session data is eradicated

SEARCH_COORDS 		= (2164, 78) # Location of the Chrome Search box

GOOGLE_LOCATION     = (2225, 457) # Location of the ReCaptcha Icon after navigating to google.com/recaptcha/api2/demo
GOOGLE_COLOR 		= (27, 61, 173)  # Color of the Google Icon

CAPTCHA_COORDS		= (1981, 471) # Coordinates of the empty CAPTCHA checkbox
CHECK_COORDS 		= (1991, 471) # Location where the green checkmark will be
CHECK_COLOR 		= (0, 158, 85)  # Color of the green checkmark

CAPTCHA_UNAVAILABLE_COLOR = (163,199,240)
CAPTCHA_UNAVAILABLE_COORDS = (2212, 560)

CAPTCHA_INPUT_COORDS = (2138, 479) # captcha input coordinates
CAPTCHA_CHECK_BOX_COORDS = (2228, 577) # when submitting the captcha solution
CAPTCHA_SOLVED_COORDS = (1980, 479) # then green "good sign" to check the captcha color
RECAPTCHA_SYMBOL_COORDS = (2225, 457) # the recaptcha symbol coords for color check
ELEMENT_SELECTION_TOOL_COORDS = (40, 80) # coords of the dev tool element selection
IFRAME_SELECTION_COORDS = (2151, 415) # the captcha iframes
CONSOLE_COORDS = (501, 81) # dev console link coords

AUDIO_URL_COORDS = (732, 268) # where to right click on the url
COPY_URL_COORDS = (820, 321) # where the "copy url" text is in the context menu

CLOSE_DEV_CONSOLE_COORDS = (1907, 40) # coords to close the dev console
AUDIO_COORDS		= (2087, 732) # Location of the Audio button

DOWNLOAD_COORDS		= (318, 590) # Location of the Download button
FINAL_COORDS  		= (315, 534) # Text entry box
VERIFY_COORDS 		= (406, 647) # Verify button
CLOSE_LOCATION		= (3826, 17) # Close the browser

DEV_CONSOLE_COMMAND = "var bad = document.querySelector('.rc-doscaptcha-body-text'); if (bad) { bad.innerHTML; } else { var el = document.getElementById('audio-source'); if (el) { el.getAttribute('src') } else { var alt = document.querySelector('.rc-audiochallenge-tdownload-link'); if (alt) alt.getAttribute('href') } } \n"

r = sr.Recognizer()

def log(msg):
	ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print('{} - {}'.format(ts, msg))

def runCommand(command):
	''' Run a command and get back its output '''
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return proc.communicate()[0]

def launchBrowserInDebugMode():
	"""launch browser in debug mode and get web socket remote debug url"""
	incognito = ''
	if USE_INCOGNITO:
		incognito = '--incognito '

	tempdir = ''
	if USE_TEMP_USER_DATA_DIR:
		temp_dir = tempfile.TemporaryDirectory()
		tempdir = '--user-data-dir={} '.format(temp_dir.name)
		# use temp_dir, and when done:ffmpeg
		# temp_dir.cleanup()

	command = 'chromium-browser {}--window-size=3840,1080 --remote-debugging-port=9222 --no-first-run --no-default-browser-check {}2> browser.log &'.format(incognito, tempdir)
	print(command)
	os.system(command)
	time.sleep(1)
	data = open('browser.log').read()
	url = re.findall(r'DevTools listening on (.*)', data)[0]
	return url

def getDownloadURL(wsURL):
	command = 'node getCaptchaDownloadURL.js {}'.format(wsURL)
	print(command)
	outputs = runCommand('node getCaptchaDownloadURL.js ' + wsURL)
	outputs = outputs.decode('utf8')
	return outputs


def someWhereRandomClose(x, y, max_dist=100):
	"""
	Find a random position close to (x, y)
	with maximal dist @max_dist
	"""
	shape = pyautogui.size()

	cnt = 0

	while True:
		randX = random.randrange(1, max_dist)
		randY = random.randrange(1, max_dist)

		if cnt % 2 == 0:
			randX *= -1
			randY *= -1

		if x + randX < shape.width and y + randY < shape.height:
			return (x + randX, y + randY)

		cnt += 1

		if cnt > 20:
			return (x, y)


def humanMove(coords, steps=0):
	"""
	Moves like a human to the coordinate (x, y) and 
	clicks the coordinate.

	Randomizes move time and the move type.

	Visits random steps coordinates before going to the goal.

	@param steps: How many random intermediate steps
				 to make before clicking on the target coords.
	"""
	move_types = [
		pyautogui.easeInQuad, # start slow, end fast
		pyautogui.easeOutQuad, # start fast, end slow
		pyautogui.easeInOutQuad,   # start and end fast, slow in middle
		# pyautogui.easeInBounce,  # bounce at the end
		# pyautogui.easeInElastic, # rubber band at the end
	]

	x, y = coords

	shape = pyautogui.size()

	# move close to the target
	for i in range(steps):
		random_close = someWhereRandomClose(x, y, 220)
		pyautogui.moveTo(random_close[0], random_close[1], random.uniform(0.1, .8), random.choice(move_types))

	pyautogui.moveTo(x, y, random.uniform(0.3, 1.1), random.choice(move_types))
	pyautogui.click()


def waitFor(x, y, color):
	''' Wait for a coordinate to become a certain color '''
	pyautogui.moveTo(x, y, .5)
	numWaitedFor = 0
	while color != getPixel(x, y):
		time.sleep(.15)
		numWaitedFor += 1
		if numWaitedFor > 25:
			return -1
	return 0

	
def getPixel(x, y):
	return PIL.ImageGrab.grab().load()[x, y]


def getDownloadLinkWithDevConsole():
	log("Getting Audio Download URL with Chrome Dev Console")
	# open dev console
	pyautogui.hotkey('ctrlleft', 'shiftleft', 'I')
	time.sleep(.5)
	
	# pick selector tool
	log("Pick element selection tool in order to focus captcha Iframe")
	humanMove(ELEMENT_SELECTION_TOOL_COORDS)
	time.sleep(.5)
	
	# select element (for iframe)
	log("Selecting Captcha Iframe")
	humanMove(IFRAME_SELECTION_COORDS)

	# click on console
	humanMove(CONSOLE_COORDS)
	
	# get download link
	log("Inject JavaScript to scrape Download URL")
	pyautogui.typewrite(DEV_CONSOLE_COMMAND)
	time.sleep(4)
	
	# paste url
	log("Right Click on the URL")
	pyautogui.moveTo(AUDIO_URL_COORDS[0], AUDIO_URL_COORDS[1], .74, pyautogui.easeInOutQuad)
	pyautogui.click(button='right')
	
	time.sleep(1)

	if UNTIL_PASTE_URL:
		return -1
	
	# click on copy url
	log("Click on `copy url` in the context menu")
	humanMove(COPY_URL_COORDS)
	time.sleep(.5)
	
	audioURL = runCommand('xclip -selection clipboard -o')
	audioURL = audioURL.decode("utf-8")

	if not audioURL.startswith('https://www.google.com/recaptcha/api2/payload'):
		log("Error: Bad audioURL: {}".format(audioURL))
		return -1

	log("Got audio mp3 URL: {}".format(audioURL))

	# close the dev console
	humanMove(CLOSE_DEV_CONSOLE_COORDS, steps=1)

	return audioURL

def downloadCaptcha(wsURL):
	log("Visiting Demo Site")

	humanMove(SEARCH_COORDS, steps=1)

	pyautogui.typewrite('https://www.google.com/recaptcha/api2/demo', interval=.02)
	pyautogui.press('enter')
	time.sleep(.5)

	# Check if the page is loaded...
	log("Check if Google ReCaptcha Symbol has correct color")
	pyautogui.moveTo(RECAPTCHA_SYMBOL_COORDS[0], RECAPTCHA_SYMBOL_COORDS[1], .55, pyautogui.easeInOutQuad)
	
	if waitFor(RECAPTCHA_SYMBOL_COORDS[0], RECAPTCHA_SYMBOL_COORDS[1], GOOGLE_COLOR) == -1:
		log('recaptcha symbol does not have matching color')
		return -1

	# click on captcha coords
	log("Click on ReCaptcha solving Button")
	humanMove(CAPTCHA_COORDS, steps=1)
	time.sleep(1)

	# check if the captcha is already solved
	# if yes, terminate
	if checkCaptcha():
		log("Google lets us in without solving the ReCaptcha")
		return 2
	
	# click on audio captcha
	log("Click on Audio Captcha")
	humanMove(AUDIO_COORDS, steps=1)
	time.sleep(.5)

	if OPEN_CAPTCHA_ONLY:
		return -1

	# check if we are banned from solving the audio captcha
	if getPixel(CAPTCHA_UNAVAILABLE_COORDS[0], CAPTCHA_UNAVAILABLE_COORDS[1]) == CAPTCHA_UNAVAILABLE_COLOR:
		log("Error: Google does not serve audio capcha, apparently we are a bot! (happens a lot as human as well)")
		humanMove(CLOSE_LOCATION)
		return -1

	audioURL = -1

	# get audioURL
	if wsURL:
		audioURL = getDownloadURL(wsURL)

		if audioURL.startswith('Your computer or network may be sending automated queries.'):
			log('You got detected as a bot.')
			return -1
	else:
		audioURL = getDownloadLinkWithDevConsole()
		if UNTIL_PASTE_URL:
			return -1

	if audioURL == -1:
		return -1

	# download the audio file with curl
	log('Downloading audio URL with Curl')
	runCommand("curl '{}' > audioCurl.mp3".format(audioURL))
	
	return 0

def checkCaptcha():
	''' Check if we've completed the captcha successfully. '''
	pyautogui.moveTo(CAPTCHA_SOLVED_COORDS[0], CAPTCHA_SOLVED_COORDS[1], .45, pyautogui.easeInOutQuad)

	if CHECK_COLOR == getPixel(CAPTCHA_SOLVED_COORDS[0], CAPTCHA_SOLVED_COORDS[1]):
		return True
	else:
		log("Captcha not solved")
		return False

def runCap():
	try:
		log("Removing old audio files...")
		os.system('rm ./audio.wav 2>/dev/null') # These files may be left over from previous runs, and should be removed just in case.

		wsURL = None

		if USE_CHROME_DEBUG_BROWSER:
			log("Opening Chrome in Debug Mode")
			wsURL = launchBrowserInDebugMode()
			log(wsURL)
		else:
			log("Starting Chrome")
			command = CHROME_LAUNCH_COMMAND
			if USE_INCOGNITO:
				command += ' --incognito'
			runCommand(command)

		# First, download the file
		downloadResult = downloadCaptcha(wsURL)
		if downloadResult != 0:
			return downloadResult

		if OPEN_CAPTCHA_ONLY:
			return -1

		# Convert the file to a format our APIs will understand
		log("Converting Captcha to .wav format...")
		os.system("echo 'y' | ffmpeg -i audioCurl.mp3 ./audio.wav 2>/dev/null")

		# play the sound
		os.system("aplay audio.wav")
		
		with sr.AudioFile('./audio.wav') as source:
			audio = r.record(source)

		log("Submitting To Speech to Text API...")
		determined = google(audio) # Instead of google, you can use ibm or bing here

		log('[!] Google speech to text API: "{}"'.format(determined))
		
		log("Inputting Answer into Captcha")
		# Input the captcha
		humanMove(CAPTCHA_INPUT_COORDS, steps=1)
		time.sleep(.5)
		pyautogui.typewrite(determined, interval=.025)
		time.sleep(.5)

		# click the check box
		humanMove(CAPTCHA_CHECK_BOX_COORDS, steps=1)

		# if Google gives us half correct solution: "Multiple correct solutions required - please solve more."
		log("Verifying Answer")
		time.sleep(1)
		# Check that the captcha is completed
		result = checkCaptcha()
		return result
	except Exception as e:
		log('Error: {}'.format(str(e)))
		return 3

if __name__ == '__main__':
	success = 0
	fail = 0
	allowed = 0

	# Run this forever and print statistics
	res = runCap()
	if res == 1:
		success += 1
	elif res == 2: # Sometimes google just lets us in
		allowed += 1
	else:
		fail += 1

	log("SUCCESSES: " + str(success) + " FAILURES: " + str(fail) + " Allowed: " + str(allowed))