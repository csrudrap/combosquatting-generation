from gen_domains import *
from mongoengine import *
import re

def main():
    connect("combosquatting_num_new", host="127.0.0.1")
    combodomains = CombosquattingDomain.objects(exists_now=True)
    count_d = dict()
    for domain in combodomains:
        for i in range(500):
            if re.search("[a-z]" + str(i) + "\.", domain.domain):
                if i in count_d.keys():
                    count_d[i] += 1
                else:
                    count_d[i] = 1
    for key, value in count_d.iteritems():
        print key, ": (count is:)", value  

if __name__ == "__main__":
    main()
