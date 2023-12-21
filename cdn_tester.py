import requests
import dns.resolver
import time  
import get_server_info
import os
import json
class cdn_tester:
    def __init__(self , domain , dns_ip , requests_target):
        self.domain = domain
        self.dns_ip = dns_ip
        self.requests_target = requests_target

    def dns_get_server_ip(self):
        
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns_ip]
        resolver.lifetime = 5.0
        #IPv6
        try:
            answers = resolver.resolve(self.domain , 'AAAA')
            for data in answers:
                server_ipv6 = str(data)
            server_locationv6 = self.get_server_location(server_ipv6)
        except dns.resolver.NoAnswer :
            server_locationv6 = False
            server_ipv6 = "NoAnswer"
        '''
        except dns.resolver.NoNameservers :
            server_locationv6 = False
            server_ipv6 = "Not found"
        '''
        #IPv4
        try:
            answers = resolver.resolve(self.domain , 'A')
            for data in answers:
                server_ipv4 = str(data)
            server_locationv4 = self.get_server_location(server_ipv4)
        except dns.resolver.NoAnswer :
            server_locationv4 = False
            server_ipv4 = "NoAnswer"
        '''
        except dns.resolver.NoNameservers :
            server_locationv4 = False
            server_ipv4 = "Not found"
        '''
        return server_ipv6  , server_locationv6 , server_ipv4 , server_locationv4
    
    def get_server_location(self , ip):
        try:
            j = open(r'C:\ip_list.json','r',encoding = 'UTF-8')
            j = json.loads(j.read())
            location = '('+j[ip]+')'
            
        except Exception :
            location = ''
        return location


    def httping(self):
        try:
            r = requests.get(self.requests_target , stream=True)
            start_time = time.time()
            r = requests.get(self.requests_target , stream=True)
            end_time = time.time()
            if r.status_code / 100 == 4.0 or r.status_code / 100 == 5.0:
                httping_ms = "Test Failed"
                test_type = "None"
            else:

                test_type = r.raw.connection.sock.getpeername()
                test_type  = test_type[0]
                if ":" in test_type :
                    test_type = "IPv6 ("+test_type+")"
                elif "." in test_type :
                    test_type = "IPv4 ("+test_type+")"
                else :
                    test_type = "None"
                use_time = end_time - start_time
                httping_ms = str(int(((use_time)*1000))) +' ms'
            del r
            start_time = time.time()

            
            r = requests.get(self.requests_target)
            end_time = time.time()
            
            if r.status_code / 100 == 4.0 or r.status_code / 100 == 5.0:
                download_speed = "Test Failed"
                test_type = "None"
            else:
                use_time = end_time - start_time
                download_speed = format(int(r.headers.get("Content-Length")) * 8 / 1024 / 1024 / use_time , '.2f')+" Mbps"

            return httping_ms , download_speed , test_type
        except :
            return "Test Failed" , "Test Failed" , "Test Failed"
        


def get_client_info():
    txt = os.popen('ipconfig/all').read()
    tmp = txt.split('\n')
    flag = False
    ipv6_addr = None
    ipv4_addr = None
    dns_name = []
    for i in tmp :
        if 'IPv6 位址. . . . . . . . . . . . .: ' in i:
            ipv6_addr = i.replace('IPv6 位址. . . . . . . . . . . . .: ','').replace('(偏好選項)','').replace(' ','')
        if 'IPv4 位址 . . . . . . . . . . . . : ' in i:
            ipv4_addr = i.replace('IPv4 位址 . . . . . . . . . . . . : ','').replace('(偏好選項)','').replace(' ','')
        if 'DNS 伺服器 . . . . . . . . . . . .' in i:
            i = i.replace('DNS 伺服器 . . . . . . . . . . . .: ' , '').replace(' ','')
            flag = True   
        if 'NetBIOS over Tcpip' in i:
            flag = False
        if flag == True:
            i = i.replace('DNS 伺服器 . . . . . . . . . . . .: ' , '').replace(' ','')
            dns_name.append(i)
            
    del txt ,tmp , flag , i
    return ipv6_addr , ipv4_addr , dns_name


def main():
    
    j = open(r'C:\config.json','r' , encoding="utf-8")
    j = json.loads(j.read())
    domain = j["domain"]
    requests_target = j["requests_target"]
    nic_name = j["nic_name"]
    ipv6_addr = None
    ipv6_addr , ipv4_addr ,  dns_ip = get_client_info()
    #domain = 'origin-direct.tanetcdn.edu.tw'
    #requests_target = 'https://origin-direct.tanetcdn.edu.tw/assets/images/Video.mp4'
    #dhcp test
    check = os.popen('netsh interface ip set dnsservers "'+nic_name+'"  dhcp')
    os.popen('netsh interface ipv6 set dnsservers "'+nic_name+'"  dhcp')
    check = check.read()
    if '錯誤' in check :
        print('網卡名稱有誤')
        input("按任意鍵結束")
        quit()

    if '權限' in check :
        print('權限不足')
        input("按任意鍵結束")
        quit()

    time.sleep(5)   #buffer time
    ipv6_addr , ipv4_addr ,  dns_ip = get_client_info()
    cdn_tester_q = cdn_tester(domain , dns_ip[0] , requests_target )
    os.popen('ipconfig/flushdns')
    server_ipv6 , server_locationv6 , server_ipv4 , server_locationv4 = cdn_tester_q.dns_get_server_ip()
    httping , download_speed  , test_type = cdn_tester_q.httping()
    get_server_info.get_server_organization(ipv6_addr = ipv6_addr , ipv4_addr = ipv4_addr  , dns_ip = dns_ip , domain = domain , \
                                            server_ipv6 = server_ipv6 , server_locationv6 = server_locationv6 , server_ipv4 = server_ipv4 , server_locationv4 = server_locationv4 , \
                                            test_type=test_type , httping = httping  , download_speed = download_speed , dhcp=True)
    #normal test
    
    for dns_name in j['dns'] :
        #domain =  "www.tanetcdn.edu.tw"
        #requests_target = "https://www.tanetcdn.edu.tw/assets/images/Video.mp4"
        os.popen('netsh interface ip set dnsservers "'+nic_name+'" static '+dns_name['ipv4']+' primary')
        if ipv6_addr !=None:
            os.popen('netsh interface ipv6 set dnsservers "'+nic_name+'" static '+dns_name['ipv6']+' primary')
        time.sleep(5)   #buffer time
        ipv6_addr , ipv4_addr ,  dns_ip = get_client_info()
        cdn_tester_q = cdn_tester(domain , dns_ip[0] , requests_target )
        os.popen('ipconfig/flushdns')
        server_ipv6 , server_locationv6 , server_ipv4 , server_locationv4 = cdn_tester_q.dns_get_server_ip()
        httping , download_speed  , test_type = cdn_tester_q.httping()
        get_server_info.get_server_organization(ipv6_addr = ipv6_addr , ipv4_addr = ipv4_addr  , dns_ip = dns_ip , domain = domain , \
                                                server_ipv6 = server_ipv6 , server_locationv6 = server_locationv6 , server_ipv4 = server_ipv4 , server_locationv4 = server_locationv4 , \
                                                test_type=test_type , httping = httping  , download_speed = download_speed)
    
    del  j , domain , requests_target , dns_name , dns_ip , cdn_tester_q , server_ipv6 , server_locationv6 , server_ipv4 , server_locationv4 , ipv4_addr , ipv6_addr , httping  , download_speed 


def test():

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]
    resolver.lifetime = 5.0
    answers = resolver.resolve("www.tanetcdn.edu.tw" , 'A')
    for data in answers:
        server_ipv4 = str(data)
    print(server_ipv4)
    answers = resolver.resolve("www.tanetcdn.edu.tw" , 'AAAA')
    for data in answers:
        server_ipv6 = str(data)
    print(server_ipv6)

if __name__ == '__main__':
    main()
    input("按任意鍵結束")
    #test()
