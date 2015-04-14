# -*- coding: utf-8 -*-
"""
Code to scrape website contents 

Created on Wed Oct 22 19:36:30 2014
@author: tobie
"""
import requests 
from lxml import html
import smtplib
from time import sleep
import BulkSMS



def Send_SSMS(msg):
    s =  BulkSMS.Server('Tooblippe','Tobiesandra69@',address='bulksms.2way.co.za')
    s.send_sms( ['27798979035'], msg )

    
def Send_Mail(msg): 
    fromaddr = 'tobie.nortje@gmail.com'
    toaddrs  = 'tobie.nortje@eon.co.za' 
    # Credentials (if needed)
    username = 'tobie.nortje@gmail.com'
    password = 'Tobiesandra69@' 
    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    print server.login(username,password)
    print server.sendmail(fromaddr, toaddrs,msg)
    print server.quit()
 
def get_etikweni():
    scrape_url = 'http://www.durban.gov.za/City_Services/electricity/Load_Shedding/Pages/default.aspx'
    page  = requests.get(scrape_url)
    dom   = html.fromstring(page.text)
    status = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_RichHtmlField"]/div[1]/p[1]/b/span/text()')
    stage  = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_RichHtmlField"]/div[1]/p[3]/b[1]/font/text()')
    #print 'Etikweni', status[0], stage[0]
    etikweni =  status[0] +','+ stage[0]
    return etikweni.decode('unicode_escape').encode('ascii','ignore')
    
def get_city_power():
    scrape_url = 'https://www.citypower.co.za/customers/pages/Load_Shedding.aspx'
    page  = requests.get(scrape_url)
    dom   = html.fromstring(page.text)
    status = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl02__ControlWrapper_RichHtmlField"]/p[1]/span[2]/strong/text()')
    message = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl02__ControlWrapper_RichHtmlField"]/p[3]/text()')
    status = status[0].decode('unicode_escape').encode('ascii','ignore')
    #print 'City Power: ', status, message[0]
    citypower = 'City Power: ' + status + ',' + message[0]
    return citypower.decode('unicode_escape').encode('ascii','ignore')

status_old = get_etikweni()
Send_Mail(status_old)

while True:
    sleep(10)
    print 'checking'
    status_new = get_etikweni()
    if status_new == status_old:
        print 'no change'
        pass
    else:
        status_old = status_new
        print 'update emailed'
        print status_old
        Send_Mail(status_old)

