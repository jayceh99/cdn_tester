import requests
import dns.resolver
import re
import time  
import get_server_info
import os
import json
class cdn_tester:
    def __init__(self,domain,dns_name,requests_target):
        self.domain = domain
        self.dns = dns_name
        self.requests_target = requests_target
        os.popen('netsh interface ip set dnsservers "wifi" static '+self.dns+' primary')
        time.sleep(3)  #buffer time 

    def dns_get_server_ip(self):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns]
        resolver.lifetime = 5.0
        answers = resolver.resolve(self.domain,'A')

        for data in answers:
            server_ip = str(data)
        server_ip = self.format_data(server_ip)
        server_location = self.get_server_location(server_ip)
        return server_ip  , server_location
    
    def get_server_location(self , ip):
        try:
            j = open(r'C:\Users\jayce\Desktop\cdn_tester\ip_list.json','r',encoding='UTF-8')
            j = json.loads(j.read())
            location = '('+j[ip]+')'
            
        except Exception as e  :
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
    
def get_client_info():
    re_pattern_dns = r'DNS 伺服器 . . . . . . . . . . . .: (\d+\.\d+\.\d+\.\d+)'
    re_pattern_ipv4 = r'IPv4 位址 . . . . . . . . . . . . : (\d+\.\d+\.\d+\.\d+)'
    txt = os.popen('ipconfig/all').read()

    dns_result = re.search(re_pattern_dns, txt)
    if dns_result:
        dns_result = dns_result.group(1)
    else:
        dns_result = 'not found'

    ip_result = re.search(re_pattern_ipv4, txt)
    if ip_result:
        ip_result = ip_result.group(1)
    else:
        ip_result = 'not found'
    return ip_result , dns_result
        
def main():
    j = open(r'C:\Users\jayce\Desktop\cdn_tester\config.json','r')
    j = json.loads(j.read())
    domain = j["domain"]
    requests_target = j["requests_target"]

    os.popen('netsh interface ip set dnsservers "wifi"  dhcp')
    time.sleep(3)   #buffer time
    client_ip , dns_ip = get_client_info()
    cdn_tester_q = cdn_tester(domain,dns_ip,requests_target)
    os.popen('ipconfig/flushdns')
    server_ip , server_location = cdn_tester_q.dns_get_server_ip()
    client_ip , dns_ip = get_client_info()
    httping , download_speed = cdn_tester_q.httping()
    get_server_info.get_server_organization(domain , server_ip ,server_location,  client_ip , dns_name=dns_ip+'(DHCP DNS)' , \
                                            httping=httping , download_speed = download_speed)
    for dns_name in j['dns'] :
        cdn_tester_q = cdn_tester(domain,dns_name['ip'],requests_target)
        os.popen('ipconfig/flushdns')
        server_ip , server_location = cdn_tester_q.dns_get_server_ip()
        client_ip , dns_ip = get_client_info()
        httping , download_speed = cdn_tester_q.httping()
        get_server_info.get_server_organization(domain , server_ip ,server_location,  client_ip , dns_name=dns_ip , \
                                                httping=httping , download_speed = download_speed)
        
    del  j , domain , requests_target , dns_name , cdn_tester_q , server_ip , server_location , client_ip , httping  , download_speed 

if __name__ == '__main__':
    main()
    input("按任意鍵結束")
