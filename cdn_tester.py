import requests
import dns.resolver
import re
import time  
import get_server_info
import os
import json
class cdn_tester:
    def __init__(self,domain,dns_ip,requests_target,dhcp=False):
        self.domain = domain
        self.dns = dns_ip
        self.requests_target = requests_target
        if dhcp == False :
            os.popen('netsh interface ip set dnsservers "wifi" static '+self.dns+' primary')
            time.sleep(3)  #buffer time 

    def dns_get_server_ip(self):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns]
        resolver.lifetime = 5.0
        answers = resolver.resolve(self.domain , 'A')

        for data in answers:
            server_ip = str(data)
        server_ip = self.format_data(server_ip)
        server_location = self.get_server_location(server_ip)
        del resolver , answers , data
        return server_ip  , server_location
    
    def get_server_location(self , ip):
        try:
            j = open(r'C:\ip_list.json','r',encoding='UTF-8')
            j = json.loads(j.read())
            location = '('+j[ip]+')'
            
        except Exception :
            location = ''
        return location


    def httping(self):
        try:
            r = requests.head(self.requests_target)
            start_time = time.time()
            r = requests.head(self.requests_target)
            end_time = time.time()
            if r.status_code / 100 == 4.0 or r.status_code / 100 == 5.0:
                httping_ms = "Test Failed"
            else:
                use_time = end_time - start_time
                httping_ms = str(int(((use_time)*1000))) +' ms'
            del r
            start_time = time.time()
            r = requests.get(self.requests_target)
            end_time = time.time()
            
            if r.status_code / 100 == 4.0 or r.status_code / 100 == 5.0:
                download_speed = "Test Failed"
            else:
                use_time = end_time - start_time
                download_speed = format(int(r.headers.get("Content-Length")) * 8 / 1024 / 1024 / use_time , '.2f')+" Mbps"

            return httping_ms , download_speed
        except :
            return "Test Failed" , "Test Failed"

    def format_data(self , data):
        formated_data = str(data).replace('[','').replace(']','').replace('\'','')
        if '：' in formated_data:
            formated_data = formated_data.split('：')
            return formated_data
        else:
            return formated_data
    
def get_client_info(dhcp=False):
    txt = os.popen('ipconfig/all').read()
    tmp = txt.split('\n')
    flag = False
    ipv6_addr = None
    ipv4_addr = None
    dns_name = None
    for i in tmp :

        if 'IPv6 位址. . . . . . . . . . . . .: ' in i:
            ipv6_addr = i.replace('IPv6 位址. . . . . . . . . . . . .: ','').replace('(偏好選項)','').replace(' ','')
        if 'IPv4 位址 . . . . . . . . . . . . : ' in i:
            ipv4_addr = i.replace('IPv4 位址 . . . . . . . . . . . . : ','').replace('(偏好選項)','').replace(' ','')
        if 'DNS 伺服器 . . . . . . . . . . . .' in i:
            i = i.replace('DNS 伺服器 . . . . . . . . . . . .: ' , '').replace(' ','')
            dns_name = i
            flag = True   
        if 'NetBIOS over Tcpip' in i:
            flag = False
        if flag == True:
            i = i.replace('DNS 伺服器 . . . . . . . . . . . .: ' , '').replace(' ','')
            if len(i) > len(dns_name) and dhcp == True:
                dns_name = i  
            elif len(i) < len(dns_name) and dhcp == False:
                dns_name = i
    del txt ,tmp , flag , i
    #print('v6 : '+str(ipv6_addr)+'\nv4 : '+str(ipv4_addr)+'\ndns : '+str(dns_name) ) 
    return ipv6_addr , ipv4_addr , dns_name


def main():
    j = open(r'C:\config.json','r')
    j = json.loads(j.read())
    domain = j["domain"]
    requests_target = j["requests_target"]
    #dhcp test
    os.popen('netsh interface ip set dnsservers "wifi"  dhcp')
    time.sleep(3)   #buffer time
    ipv6_addr , ipv4_addr ,  dns_ip = get_client_info(dhcp=True)
    cdn_tester_q = cdn_tester(domain,dns_ip,requests_target,dhcp=True)
    os.popen('ipconfig/flushdns')
    server_ip , server_location = cdn_tester_q.dns_get_server_ip()
    httping , download_speed = cdn_tester_q.httping()
    get_server_info.get_server_organization(ipv6_addr = ipv6_addr , ipv4_addr = ipv4_addr  , dns_ip = dns_ip+"(DHCP DNS)" , domain = domain , \
                                            server_ip = server_ip , server_location = server_location ,  httping = httping  , \
                                            download_speed = download_speed)
    #normal test
    for dns_name in j['dns'] :
        cdn_tester_q = cdn_tester(domain,dns_name['ip'],requests_target)
        os.popen('ipconfig/flushdns')
        server_ip , server_location = cdn_tester_q.dns_get_server_ip()
        ipv6_addr , ipv4_addr ,  dns_ip = get_client_info()
        httping , download_speed = cdn_tester_q.httping()
        get_server_info.get_server_organization(ipv6_addr = ipv6_addr , ipv4_addr = ipv4_addr  , dns_ip = dns_ip , domain = domain , \
                                                server_ip = server_ip , server_location = server_location ,  httping = httping  , \
                                                download_speed = download_speed)
    
    del  j , domain , requests_target , dns_name , dns_ip , cdn_tester_q , server_ip , server_location , ipv4_addr , ipv6_addr , httping  , download_speed 

if __name__ == '__main__':
    main()
    input("按任意鍵結束")
