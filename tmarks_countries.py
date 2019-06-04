from gen_domains import *
from mongoengine import *

def main():
    connect("combosquatting_country", host="127.0.0.1")
    gen_model = GenerativeModel()
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    gen_model.tmarks = [x.lower().strip() for x in tmarks]
    gen_model.tmarks = map(lambda x:x.split(' ')[0].split('.')[0], gen_model.tmarks)
    combosquatting_domains = []
    for tmark in gen_model.tmarks:
        for country in gen_model.countries_and_tlds.keys():
            gen_model.visit_domain(tmark, tmark + country + gen_model.countries_and_tlds[country], False)
            gen_model.visit_domain(tmark, tmark + '-' + country + gen_model.countries_and_tlds[country], False)
            for main_tld in gen_model.main_tlds:
                gen_model.visit_domain(tmark, tmark + country + main_tld, False)
                gen_model.visit_domain(tmark, tmark + '-' + country + main_tld, False)
        for country in gen_model.countries_without_tlds:
            for main_tld in gen_model.main_tlds:
                gen_model.visit_domain(tmark, tmark + country + main_tld, False)
                gen_model.visit_domain(tmark, tmark + '-' + country + main_tld, False)
        for country in gen_model.us_names:
            gen_model.visit_domain(tmark, tmark + country + ".us", False)
            gen_model.visit_domain(tmark, tmark + "-" + country + ".us", False)
            for main_tld in gen_model.main_tlds:
                gen_model.visit_domain(tmark, tmark + country + main_tld, False)
                gen_model.visit_domain(tmark, tmark + '-' + country + main_tld, False)

        for country in ["britain", "uk", "england"]:            
           gen_model.visit_domain(tmark, tmark + country + ".co.uk", False)
           is_last = country == "england" and tmark == gen_model.tmarks[-1]
           gen_model.visit_domain(tmark, tmark + "-" + country + ".co.uk", is_last)


if __name__ == "__main__":
    main()
