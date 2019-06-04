from gen_domains import *
from mongoengine import *

def main():
    connect("combosquatting_letter", host="127.0.0.1")
    gen_model = GenerativeModel()
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    gen_model.tmarks = [x.lower().strip() for x in tmarks]
    gen_model.tmarks = map(lambda x:x.split(' ')[0].split('.')[0], gen_model.tmarks)
    combosquatting_domains = []
    for tmark in gen_model.tmarks:
        for i in gen_model.english_alphabet:
            for tld in gen_model.main_tlds + [gen_model.us_tld] + gen_model.uk_tlds:
                is_last = tmark == gen_model.tmarks[-1] and i == gen_model.english_alphabet[-1] and tld == (gen_model.main_tlds + [gen_model.us_tld] + gen_model.uk_tlds)[-1]
                gen_model.visit_domain(tmark, tmark + str(i) + tld, is_last)


if __name__ == "__main__":
    main()
