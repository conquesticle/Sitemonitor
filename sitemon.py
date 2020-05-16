import requests
import time
import getpass
import re
import lxml
from bs4 import BeautifulSoup
from datetime import datetime
from pushbullet import Pushbullet

# requirements below, literally copy paste the line into a terminal
# pip install requests getpass pushbullet.py bs4
# you'll also need to install pushbullet on your mobile device and 
# get a valid api key

urls = {
    'ticket_url':'https://www.derbycon.com/purchase-tickets', 
    'site_url':'https://www.derbycon.com', 
    'blog_url':'https://www.derbycon.com/blog',
    'event_url':"https://www.eventbrite.com/e/derbycon-2019-90-finish-line-tickets-61137416659"
}

def checkForUpdates(urls, log_path, interval, pb):
    old_state = dict()
    with open(log_path,"a+") as log_file:
        try:
            # get the initial state for each url
            for url in urls:
                log_message = f'{getDate()}\tFirst pass, getting {urls[url]}\n'
                log_file.write(log_message)
                with requests.get(urls[url]) as response:
                    if response.status_code != 200:
                        pb.push_note("status fail",f'Got status code {response.status_code} trying to get {urls[url]}')
                        break
                    old_state[url] = response.text
            while True:
                for url in urls:
                    with requests.get(urls[url]) as response:
                        if response.status_code != 200:
                            pb.push_note("status fail",f'Got status code {response.status_code} trying to get {urls[url]}')
                        if url == 'event_url':
                            html = BeautifulSoup(response.text, features="lxml")
                            flag = False
                            # shtml = str(html.find_all(class_='js-event-password')[0])
                            # for tag in html.find_all(re.compile("^a")):
                            #     if 'data-automation' in tag.attrs and tag.attrs['data-automation'] == 'remind-me-btn':
                            #        flag = True
                            for tag in html.find_all(re.compile("^button$")):
                                if 'data-automation' in tag.attrs and tag.attrs['data-automation'] == 'ticket-modal-btn' and tag.text != "Details":
                                    pb.push_note("OMG IT'S HERE", urls[url])
                                    flag = True
                                    break
                            # if not flag:
                            #     pb.push_note("Reminder removed", urls[url])
                            #    break
                            continue
                        else:
                            shtml = response.text
                        if old_state[url] != shtml:
                            log_message = f'{getDate()}\tDetected change in {urls[url]}\n'
                            log_file.write(log_message)
                            old_state[url] = shtml
                            pb.push_note("log",log_message)
                        else:
                            log_message = f'{getDate()}\tNo change detected for {urls[url]}\n'
                            log_file.write(log_message)
                # set timer to sleep time and loop again
                if flag:
                    break
                time.sleep(interval)
        except Exception as e:
            log_file.write(f'{str(e)}\n')
            pb.push_note("Error encountered",str(e))


def getDate():
    return datetime.now().strftime("%m_%d_%y--%H:%M:%S")

if __name__ == "__main__":
    pb = Pushbullet(getpass.getpass("Enter your API Key:"))
    checkForUpdates(urls=urls, log_path=r'./sitemon.log', interval=1, pb=pb)