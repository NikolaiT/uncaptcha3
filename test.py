import subprocess

def runCommand(command):
	''' Run a command and get back its output '''
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return proc.communicate()[0]

wsURL = 'ws://127.0.0.1:9222/devtools/browser/0cd8e668-c42d-40fc-957a-070cd6301a80'
command = 'node getCaptchaDownloadURL.js {}'.format(wsURL)
print(command)
outputs = runCommand('node getCaptchaDownloadURL.js ' + wsURL)
print(outputs.decode('utf8'))