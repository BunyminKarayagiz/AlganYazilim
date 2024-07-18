import subprocess

def wlan_ip():
    result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True,encoding="latin-1").stdout.lower()
    scan=0
    for i in result.split('\n'):
        if 'wireless lan adapter wi-fi:' in i: scan=4
        if scan:
            if 'ipv4' in i:
                return i.split(':')[1].strip()

def ethernet_ip_for_teknofest():
    result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True,encoding="latin-1").stdout.lower()
    scan=0
    for i in result.split('\n'):
        if 'ethernet adapter ethernet:' in i: scan=4
        if scan:
            if 'ipv4' in i:
                return i.split(':')[1].strip()

