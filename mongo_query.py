from gen_domains import *
from mongoengine import *

def main():
    connect("combosquatting_num", host="127.0.0.1")
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    tmarks = [x.lower().strip() for x in tmarks]
    tmarks = map(lambda x:x.split(' ')[0].split('.')[0], tmarks)
    tmarks_d = dict()
    for tmark in tmarks:
        #combodomains = CombosquattingDomain.objects(trademark=tmark, exists_now=True)
        count = CombosquattingDomain.objects(trademark=tmark, exists_now=True).count()
        tmarks_d[tmark] = count
    for key, value in sorted(tmarks_d.iteritems(), key=lambda (k,v): (v,k)):
        print "%s: %s" % (key, value)

if __name__ == "__main__":
    main()
