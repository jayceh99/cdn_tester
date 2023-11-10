import prettytable as pt
from lxml import html
import requests
import json

def get_server_organization(ipv6_addr , ipv4_addr  , dns_ip , domain , server_ipv6 , server_locationv6 , server_ipv4 , server_locationv4  , httping  , download_speed , test_type = None , dhcp = False):
    if server_ipv6 == "NoAnswer" :
        keyv6 , valuev6 = "Chinese Name" , "NoAnswer"
    else:

        try:
            keyv6 , valuev6 = tanetwhois(server_ipv6 , server_locationv6)
        except Exception:
            keyv6 , valuev6 = "Chinese Name" , ""
    if server_ipv4 == "NoAnswer" :
        keyv4 , valuev4 = "Chinese Name" , "NoAnswer" 
    else:
        try:
            keyv4 , valuev4 = tanetwhois(server_ipv4 , server_locationv4)
        except Exception:
            keyv4 , valuev4 = "Chinese Name" , "NoAnswer"
    i = 1
    tb = pt.PrettyTable()
    tb.field_names = ['Key','Value']
    tb.add_row(['HTTPing',httping])
    tb.add_row(['Download Speed',download_speed])
    tb.add_row([keyv6+" IPv6" , valuev6+"  #IPv6"])
    tb.add_row([keyv4+" IPv4" , valuev4+"  #IPv4"])
    tb.add_row(['Server IPv6 Address' , server_ipv6])
    tb.add_row(['Server IPv4 Address' , server_ipv4])
    tb.add_row(['Test type (IPv6 or IPv4)' , test_type])
    if ipv6_addr != None :
        tb.add_row(['Client IPv6 Address', ipv6_addr])
    tb.add_row(['Client IPv4 Address' , ipv4_addr]) 
    if dhcp == True:
        for dns_ips in dns_ip :
            tb.add_row(['DNS '+str(i)+' IP Address' , dns_ips+' (DHCP DNS)'])
            i = i + 1     
    else:
        for dns_ips in dns_ip :
            tb.add_row(['DNS '+str(i)+' IP Address' , dns_ips])
            i = i + 1 
    tb.add_row(['Test Domain Name' , domain]) 
    print(tb)
    del ipv6_addr , ipv4_addr  , dns_ip , domain , server_ipv6 , server_locationv6 , server_ipv4 , server_locationv4 ,  httping , download_speed , tb 

def tanetwhois(server_ip , server_location):
    r = requests.get(r'https://whois.tanet.edu.tw/showWhoisPublic.php?queryString='+str(server_ip)+'&submit=%E9%80%81%E5%87%BA')
    data = html.fromstring(r.content.decode('UTF-8'))
    max = len(data.xpath('/html/body/center/table[2]/tr'))
    
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
                del r , data , max ,  flag 
                return key , value

    

def format_data(data):
    formated_data = str(data).replace('[','').replace(']','').replace('\'','')
    if '：' in formated_data:
        formated_data = formated_data.split('：')
        return formated_data
    else:
        return formated_data
    