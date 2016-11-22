import os
import time
import json
import subprocess
from urllib2 import Request, urlopen
from urllib import urlencode
from slackclient import SlackClient
# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "get"

#instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def get_ticker_list(command):
    print("In func ticker_list")
    l=[]
    for word in command.split(' '):
        word = word.upper()
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=n' % word
        request = Request(url)
        response = urlopen(request)
        content = response.read().decode().strip().strip('"')
        print(content)
        if content != 'N/A': 
            l.append(word)
        print(l)
    return l 
def get_ticker_for_company_name(command):
    print("In func get_ticker_for_company")        
    l=[]
    for word in command.split(' '):
        word = word.upper()
        url = 'http://d.yimg.com/aq/autoc?query=%s&region=CHI&lang=en-US&callback=YAHOO.util.ScriptNodeDataSource.callbacks' % word
        request = Request(url)
        response = urlopen(request)
        content = response.read().decode().strip().strip('"')
        print(content)
        if content != 'N/A':
            l.append(word)
        print(l)
    return l

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with company name."
    tick_list=get_ticker_list(command)
    if tick_list :
        for ticker in tick_list:
            get_value_url = 'http://finance.google.com/finance/info?client=ig&q=%s' % ticker
            value = subprocess.Popen(['curl', '-s', get_value_url], stdout=subprocess.PIPE).communicate()[0]
            j = json.loads(value[5:len(value)-2])
            stock_price = float(j['l'])
            response = "Sure... for ticker %s. Stock price is %s" %(ticker,stock_price)
            slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("ShareBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
