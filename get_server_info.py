import prettytable as pt
from lxml import html
import requests
import json

def get_server_organization(ipv6_addr , ipv4_addr  , dns_ip , domain , server_ip , server_location ,  httping  , download_speed):

    tb = pt.PrettyTable()
    tb.field_names = ['Key','Value']
    
    
    r = requests.get(r'https://whois.tanet.edu.tw/showWhoisPublic.php?queryString='+str(server_ip)+'&submit=%E9%80%81%E5%87%BA')
    #r = requests.get(r'https://whois.tanet.edu.tw/showWhoisPublic.php?queryString=203.68.82.33&submit=%E9%80%81%E5%87%BA')
    data = html.fromstring(r.content.decode('UTF-8'))
    max = len(data.xpath('/html/body/center/table[2]/tr'))
    tb.add_row(['HTTPing',httping])
    tb.add_row(['Download Speed',download_speed])
    flag = False
    for i in range(1,max+1):
        if '用戶單位' in str(data.xpath('/html/body/center/table[2]/tr['+str(i)+']/td/text()')) :
            '''
            tmp_data  = format_data(data.xpath('/html/body/center/table[2]/tr['+str(i)+']/td/text()'))
            key = format_data(str(tmp_data[0]))
            value = format_data(str(tmp_data[1]))
            tb.add_row(['-'*35,'-'*35])
            tb.add_row([key,value])
            '''
            flag = True
        if len(data.xpath('/html/body/center/table[2]/tr['+str(i)+']/td')) == 2 and flag == True:
            key = format_data(str(data.xpath('/html/body/center/table[2]/tr['+str(i)+']/td[1]/text()')))
            if key == 'Chinese Name' :
                value = format_data(str(data.xpath('/html/body/center/table[2]/tr['+str(i)+']/td[2]/text()')))+server_location
                tb.add_row([key,value])
                break
    tb.add_row(['Server IP Address',server_ip])
    tb.add_row(['DNS IP Address',dns_ip])
    if ipv6_addr != None :
        tb.add_row(['Client IPv6 Address', ipv6_addr])
    tb.add_row(['Client IPv4 Address', ipv4_addr]) 
    tb.add_row(['Domain Name',domain]) 
    print(tb)
    del ipv6_addr , ipv4_addr  , dns_ip , domain , server_ip , server_location ,  httping , download_speed , r , data , max , key , value , tb , flag 

def format_data(data):
    formated_data = str(data).replace('[','').replace(']','').replace('\'','')
    if '：' in formated_data:
        formated_data = formated_data.split('：')
        return formated_data
    else:
        return formated_data
    