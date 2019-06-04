from gen_domains import *
from mongoengine import *

def old_visit_url(gen_model, tmark, domain):
    response_url_val, response_code_val, exists_now_val, ip_val = gen_model.visit_domain(domain)
    combo_domain_record = CombosquattingDomain(domain=domain, trademark=tmark, ip=ip_val, \
                    exists_now=exists_now_val, response_code=response_code_val, response_url=response_url_val)
    if gen_model.is_malicious(domain):
        combo_domain_record.is_malicious = True
    combo_domain_record.save()

def main():
    connect("combosquatting_num", host="127.0.0.1")
    gen_model = GenerativeModel()
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    gen_model.tmarks = [x.lower().strip() for x in tmarks]
    gen_model.tmarks = map(lambda x:x.split(' ')[0].split('.')[0], gen_model.tmarks)
    combosquatting_domains = []
    for tmark in gen_model.tmarks:
        for i in range(100):
            for tld in gen_model.main_tlds + [gen_model.us_tld] + [gen_model.uk_tlds[1]]:
                is_last = tmark == gen_model.tmarks[-1] and i == 99 and tld == (gen_model.main_tlds + [gen_model.us_tld] + gen_model.uk_tlds)[-1]
                gen_model.visit_domain(tmark, tmark + str(i) + tld, is_last)


if __name__ == "__main__":
    main()
