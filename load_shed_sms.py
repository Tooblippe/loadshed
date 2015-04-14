
import requests 
from lxml import html
from time import sleep
import BulkSMS  #


def Send_SMS(msg):
    s =  BulkSMS.Server('Tooblippe','Tobiesandra69@',address='bulksms.2way.co.za')
    s.send_sms( ['27798979035'], msg )

def get_etikweni():
    scrape_url = 'http://www.durban.gov.za/City_Services/electricity/Load_Shedding/Pages/default.aspx'
    page  = requests.get(scrape_url)
    dom   = html.fromstring(page.text)
    status = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_RichHtmlField"]/div[1]/p[1]/b/span/text()')
    stage  = dom.xpath('//*[@id="ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_RichHtmlField"]/div[1]/p[3]/b[1]/font/text()')
    #print 'Etikweni', status[0], stage[0]
    etikweni =  status[0] +','+ stage[0]
    return etikweni.decode('unicode_escape').encode('ascii','ignore')
    
status_old = get_etikweni()
print status_old
Send_SMS(status_old)

while True:
    sleep(60)
    print 'checking'
    status_new = get_etikweni()
    if status_new == status_old:
        print 'no change'
        pass
    else:
        status_old = status_new
        print 'update emailed'
        print status_old
        Send_SMS(status_old)

