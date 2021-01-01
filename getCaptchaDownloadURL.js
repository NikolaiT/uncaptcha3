const puppeteer = require('puppeteer-core');

// first start browser with this command:
// chromium-browser --incognito --remote-debugging-port=9222 --no-first-run --no-default-browser-check --user-data-dir=/tmp/t
// then visit: https://www.google.com/recaptcha/api2/demo and navigate to audio captcha
// then this script will yield the audio url

(async () => {
  if (process.argv.length != 3) {
    console.error('Usage: node getCaptchaDownloadURL.js ws://127.0.0.1:9222/devtools/browser/2f7d4355-4c7b-44a0-be0c-e9402493f586')
    process.exit(-1);
  }

  const wsChromeEndpointurl = process.argv[2];

  const browser = await puppeteer.connect({
    browserWSEndpoint: wsChromeEndpointurl,
  });

  const page = (await browser.pages())[0];

  await page.waitForSelector(`iframe[title="recaptcha challenge"]`);

  const elementHandle = await page.$('iframe[title="recaptcha challenge"]');
  const frame = await elementHandle.contentFrame();

  let captchaAudioURL = await frame.evaluate(function () {
    // check if we get bad bot text
    var bad = document.querySelector('.rc-doscaptcha-body-text');
    if (bad) {
      return bad.innerHTML;
    }
    
    var el = document.getElementById('audio-source');
    if (el) { 
      return el.getAttribute('src') 
    } else { 
      var other = document.querySelector('.rc-audiochallenge-tdownload-link');
      if (other) {
        return other.getAttribute('href') 
      }
    }
    return '';
  });

  console.log(captchaAudioURL);

  await browser.disconnect();
})();