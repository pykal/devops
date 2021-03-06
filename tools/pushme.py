#!/usr/bin/env python
# Use pushover.net to notify of 
# long running commands finishing. 
# Run as: pushme mysqlrepair -u root -p centstorage
# By Stefan Midjich

# Pushover.net configuration
AppToken = 'your app token'
UserToken = 'your user token'
AppHost = 'api.pushover.net'
AppPort = 443
AppPath = '/1/messages.json'

AppURL = 'https://{AppHost}{AppPath}'.format(
    AppHost = AppHost,
    AppPath = AppPath,
)

from sys import exit, argv, stderr
from datetime import datetime
import subprocess
import httplib
import urllib
import traceback

# Exit if no arguments provided
if len(argv[1:]) < 1:
    print >>stderr, 'No arguments'
    exit(1)

# CMD to execute with arguments as a list
cmd = argv[1:]

# Start timer for subprocess
startTime = datetime.now()

try:
    proc = subprocess.Popen(cmd)
    (out, err) = proc.communicate()
    rc = proc.returncode
except(IOError, OSError), e:
    rc = 1
    err = str(e)
except:
    rc = 1
    err = traceback.format_exc()

# Calculate runtime and format
stopTime = datetime.now()
runTime = stopTime - startTime
diff = divmod(runTime.days * 86400 + runTime.seconds, 60)
fTime = '%d minutes and %d seconds' % diff

if rc == 0:
    titleText = 'Command finished: %s' % ' '.join(cmd)
    messageText = 'Command finished in %s, with return code %d' % (fTime, rc)
else:
    titleText = 'Command failed: %s' % ' '.join(cmd)
    messageText = 'Command failed in %s, with return code %d\nError: %s' % (
        fTime, 
        rc, 
        err
    )

postData = "token={token}&user={userToken}&title={title}&message={message}".format(
    token = AppToken,
    userToken = UserToken,
    title = urllib.quote(titleText),
    message = urllib.quote(messageText),
)

postHeader = {"Content-type": "application/x-www-form-urlencoded", 
              "Accept":"text/plain"}

try:
    postConn = httplib.HTTPSConnection(AppHost, AppPort)
    postConn.request('POST', AppPath, postData, postHeader)
    postResponse = postConn.getresponse()
except(httplib.HTTPException), e:
    print >>stderr, 'Could not send notification: %s' % str(e)

postConn.close()
exit(rc)
