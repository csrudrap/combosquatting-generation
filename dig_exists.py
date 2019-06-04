# Filter objects that have exists_now: true.
# dig the trademark with SOA and create a list of nameservers/responsible emails, cache this.
# dig the current domain SOA and extract the xxxxx.xxx part of each of the answers (split on . and take -1 and -2 if 3-letter, else -3)
# Check if there is any match. If there is no match, belongs_to_tmark: False.
# Check if the url field starts with https. If yes, figure out a way to get the issuing authority info. 

import subprocess
from gen_domains import *
from mongoengine import *

def main():
    with open("soa_dig_alexatop150.txt") as f:
        l_soa = f.readlines()
    tmarks_ns = dict()
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    tmarks = [x.lower().strip() for x in tmarks]
    tmarks = map(lambda x:x.split(' ')[0].split('.')[0], tmarks)
    connect("combosquatting_keyword", host="127.0.0.1")
    for i in range(len(l_soa)):
        tmarks_ns[tmarks[i]] = l_soa[i].split('\t')[-1].split()[:2]
        tmarks_ns[tmarks[i]] = map(lambda x: '.'.join(x.split('.')[-2:]) if len(x.split('.')[-1]) == 3 else '.'.join(x.split('.')[-3:]), tmarks_ns[tmarks[i]])   
    for tmark in tmarks_ns.keys():
        # query mongo where trademark is tmark and exists_now is true.
        # for each of those domains, execute dig and extract nameservers' 2nd level domain.
        # check if any of these is in tmarks_ns[tmark]. 
        objs = CombosquattingDomain.objects(exists_now=True, trademark=tmark)
        domains = map(lambda x:x.domain, objs)
        for domain in domains:
            cmd = "dig SOA {} | sed -e '1,/ANSWER SECTION/d'".format(domain)
            try:
                op = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                print "Couldn't execute command for domain {}".format(domain)
                continue
            answer = op.split('\n')[0]
            ns = answer.split('\t')[-1].split()[:2]
            ns = map(lambda x:x[:-1], ns)
            ns = map(lambda x: '.'.join(x.split('.')[-2:]) if len(x.split('.')[-1]) == 3 else '.'.join(x.split('.')[-3:]), ns)
            if len(set(ns) & set(tmarks_ns[tmark])) == 0:
                print 'MALICIOUS', tmark, ', '.join(tmarks_ns[tmark]), '\t\t', domain, ', '.join(ns)
            else:
                print 'BENIGN', tmark, ', '.join(tmarks_ns[tmark]), '\t\t', domain, ', '.join(ns)
                

if __name__ == "__main__":
    main()

