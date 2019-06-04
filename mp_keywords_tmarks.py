from gen_domains import *
from mongoengine import *
import threading
import multiprocessing
import signal
import time
import subprocess
import os

def visit_url(gen_model, tmark, domain):
    gen_model.visit_domain(tmark, domain)


def tmark_process_worker(core_id, tmarks):
    #os.sched_setaffinity(os.getpid(), {core_id})
    print tmarks[0], open("/proc/{pid}/stat".format(pid=os.getpid()), 'rb').read().split()[-14]
    connect("combosquatting_keyword", host="127.0.0.1")
    gen_model = GenerativeModel()
    gen_model.tmarks = [x.lower().strip() for x in tmarks]
    gen_model.tmarks = map(lambda x:x.split(' ')[0].split('.')[0], gen_model.tmarks)
    for tmark in gen_model.tmarks:
        api_keywords = gen_model.get_api_keywords(tmark)
        for word in list(set(api_keywords)):
            if word.count(' ') < 2:
                for tld in gen_model.main_tlds + [gen_model.us_tld] + gen_model.uk_tlds:
                    is_last = True if tmark == gen_model.tmarks[-1] and word == api_keywords[-1] and tld == (gen_model.main_tlds + [gen_model.us_tld] + gen_model.uk_tlds)[-1] else False
                    if word.count(' ') == 1:
                        word_split = word.split(' ')
                        first_word = word_split[0]
                        second_word = word_split[1]
                        word_nospace = ''.join(word_split)
                        word_dash = '-'.join(word_split)

                        gen_model.visit_domain(tmark, tmark + word_nospace + tld)
                        gen_model.visit_domain(tmark, tmark + '-' + word_nospace + tld)
                        gen_model.visit_domain(tmark, tmark + word_dash + tld)
                        gen_model.visit_domain(tmark, tmark + '-' + word_dash + tld)
    
                        gen_model.visit_domain(tmark, tmark + first_word + tld)
                        gen_model.visit_domain(tmark, tmark + '-' + first_word + tld)
                        gen_model.visit_domain(tmark, first_word + tmark + tld)
                        gen_model.visit_domain(tmark, first_word + '-' + tmark + tld)
    
                        gen_model.visit_domain(tmark, tmark + second_word + tld)
                        gen_model.visit_domain(tmark, tmark + '-' + second_word + tld)
                        gen_model.visit_domain(tmark, second_word + tmark + tld)
                        gen_model.visit_domain(tmark, second_word + '-' + tmark + tld, is_last=is_last)
                    elif ' ' not in word:
                        gen_model.visit_domain(tmark, word + '-' + tmark + tld)
                        gen_model.visit_domain(tmark, tmark + '-' + word + tld)
                        gen_model.visit_domain(tmark, word + tmark + tld)
                        gen_model.visit_domain(tmark, tmark + word + tld, is_last=is_last)


def main():
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    for i in range(10, len(tmarks), 10):
        print i, tmarks[i-10:i]
        new_proc = multiprocessing.Process(target=tmark_process_worker, args=(i/10 - 1, tmarks[i-10:i],))
        new_proc.start()

if __name__ == "__main__":
    main()
