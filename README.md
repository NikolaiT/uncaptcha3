This repository uses the idea of [uncaptcha2](https://github.com/ecthros/uncaptcha2) to
solve Google's Audio ReCaptcha with Google's own Speech-to-Text API.

Yes you read that correctly: **It is possible to solve Google's Audio version of ReCaptcha v2 with Google's own [Speech-to-Text API](https://cloud.google.com/speech-to-text).**

Since the release of [uncaptcha2](https://github.com/ecthros/uncaptcha2) is from **Janunary 18, 2019**,
the Proof of Concept code does not work anymore (as the authors predicted correctly)

This repository attempts to keep the proof of concept up to date and working.

### Known Issues

Of course Google is not easily tricked. After all, ReCaptcha v3 is still based on ReCaptcha v2.

When you think that 97% of all captchas can be solved with this method in production, I need to warn you:

Google is very reluctant to serve the audio captcha. After all, audio captchas are supposed to be solved by visually impaired people. 

Even if you are navigating as real human being to the audio captcha, you will often get banned by the captcha. If you are not logged into the Google account, you will get very often the following error when attempting to solve the audio captcha:

![Google Says no to the audio captcha](images/Google-says-no.png)

I do not know how Google decides to block you, but I heavily assume that the very simple act of repeatingly prompting for the audio captcha is enough to become suspicious.

---

Another issue: It is no longer possible to download the recaptcha audio. Google removed this download option. Instead, the audio download link is obtained by opening the dev tools window and inserting some JavaScript which extracts the audio url.

If I am not mistaken, Google sanctions the opening of dev tools when solving the captcha.

Another possibility is to obtain the download link via the remote debug protcol. This solution is implementd in `getCaptchaDownloadURL.js`.

### Installation

The code was developed and tested on Ubuntu 18.04.

The following software needs to be installed:

```
chromium-browser
xclip
ffmpeg
curl
```

In order to install the Python 3.7 dependencies, create an virtual environment with `pipenv`:

```
# create pipenv
pipenv --python 3.7

# install dependencies
pipenv install -r dependencies.txt

# create pipenv shell
pipenv shell
```

After those commands, the program `solveAudioCaptcha.py` may be executed:

```
python solveAudioCaptcha.py
```

### Adjust Coordinates

The captcha is solved with mouse pointer automation using the python module `pyautogui`.  Coordinates are used to automate the captcha solving.

Your setup very likely differs from my setup.

Therefore, you need to adjust the coordinates in `solveAudioCaptcha.py`.

