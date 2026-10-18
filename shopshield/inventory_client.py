#prblem 2 temporary service failure and retry with exponential backoff
#----------------------------------------------------------------------

import time
import json
import urllib.request     #built in HTTP client
import urllib.error       #to catch connection and HTTP errors

#configuraation
#URL where product seevice is running
PRODUCT_SERVICE_URL = "http://127.0.0.1:5001/api/stock"

#maximum seconds to wait for product service to respond before timing out
REQUEST_TIMEOUT_SECONDS = 1.0

#maximum no of retry attempts
MAX_RETRIES = 3

#base delay for exponential backoff (in seconds)
BASE_BACKOFF_SECONDS = 0.3

#Local in-memory cache: stores last known stock so we never  show empty data