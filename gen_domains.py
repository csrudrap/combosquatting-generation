import urllib2
import json
from bs4 import BeautifulSoup
import re
from mongoengine import *
import datetime
import dns.resolver
import dns.exception
import socket
import grequests
import requests
from async_dns import AsyncResolver

class CombosquattingDomain(DynamicDocument):
    domain_name = StringField()
    response_url = StringField()
    trademark = StringField()
    exists_now = BooleanField()
    response_code = IntField(default=0)
    is_malicious = BooleanField(default=False)
    time_inserted = DateTimeField(default=datetime.datetime.utcnow)
    
class GenerativeModel:
    gsb_url = "127.0.0.1:8080"
    google_api_url = "https://www.google.com/complete/search?output=toolbar&q="
    bing_api_url = "https://api.bing.com/osjson.aspx?language=EN-US&JsonCallback=sas_SearchAutoSuggest.setData&query="
    #yahoo_api_url = "https://sugg.search.yahoo.net/sg/?output=fxjsonp&nresults=10&command="

    # TODO: Categorize each trademark and remove some irrelevant letters.
    tmarks = []
    main_tlds = [".com", ".org", ".net"]

    us_tld = ".us"
    uk_tlds = [".uk", ".co.uk"]
    us_names = ["america", "usa", "us", "unitedstates"]
    countries_and_tlds = {"india": ".in", "china": ".cn", "japan": ".jp", "russia": ".ru", \
                            "germany": ".de", "france": ".fr", "mexico": ".mx", "czech": ".cz", \
                            "philippines": ".ph", "vietnam": ".vn", "canada": ".ca", \
                            "iran": ".ir", "spain": ".es", "italy": ".it", "korea": ".kr", \
                            "poland": ".pl", "netherlands": ".nl"}
    countries_without_tlds = ["brazil", "ukraine", "australia", "turkey", "nigeria", "indonesia", "egypt", \
                              "uk", "britain", "england"] 
    
    english_alphabet = "abcdefghijklmnopqrstuvwyz"
    exception_domains = dict()
    combodomain_objs = []
    MAX_DOMAIN_BATCH_COUNT = 2000

    def generate_combodomains_by_tmark(self, tmark):
        # Logic to generate a list of combo-domains given a trademark.
        # Keep the suggestion only if it has less than 3 spaces. 
        # If space count is 2, add separately and together.
        combosquatting_domains = []
        api_keywords = self.get_api_keywords(tmark)
        for word in set(api_keywords):
            if word.count(' ') < 2:
                for tld in self.main_tlds + self.countries_and_tlds.values():
                    if word.count(' ') == 1:
                        word_split = word.split(' ')
                        first_word = word_split[0]
                        second_word = word_split[1]
                        word_nospace = ''.join(word_split)
                        word_dash = '-'.join(word_split)

                        combosquatting_domains.append(tmark + word_nospace + tld)
                        combosquatting_domains.append(tmark + '-' + word_nospace + tld)
                        combosquatting_domains.append(tmark + word_dash + tld)
                        combosquatting_domains.append(tmark + '-' + word_dash + tld)
                       
                        combosquatting_domains.append(tmark + first_word + tld)
                        combosquatting_domains.append(tmark + '-' + first_word + tld)
                        combosquatting_domains.append(first_word + tmark + tld)
                        combosquatting_domains.append(first_word + '-' + tmark + tld)
                        
                        combosquatting_domains.append(tmark + second_word + tld)
                        combosquatting_domains.append(tmark + '-' + second_word + tld)
                        combosquatting_domains.append(second_word + tmark + tld)
                        combosquatting_domains.append(second_word + '-' + tmark + tld)
                    elif ' ' not in word:
                        combosquatting_domains.append(word + '-' + tmark + tld)
                        combosquatting_domains.append(tmark + '-' + word + tld)
                        combosquatting_domains.append(word + tmark + tld)
                        combosquatting_domains.append(tmark + word + tld)
                    for i in range(100):
                        combosquatting_domains.append(tmark + str(i) + tld)
        for country in self.countries_and_tlds.keys():
            combosquatting_domains.append(tmark + country + self.countries_and_tlds[country])                
            combosquatting_domains.append(tmark + '-' + country + self.countries_and_tlds[country])
            for main_tld in self.main_tlds:
                combosquatting_domains.append(tmark + country + main_tld)
                combosquatting_domains.append(tmark + '-' + country + main_tld)
                        
        return combosquatting_domains                

    def get_api_keywords(self, tmark):
        # Get keywords from Bing and Google and return a set of keywords.
        api_keywords = []
        for letter in self.english_alphabet:
            google_keywords = self.get_google_keywords(tmark, letter)
            bing_keywords = self.get_bing_keywords(tmark, letter)
            if google_keywords:
                api_keywords.extend(google_keywords)
            if bing_keywords:
                api_keywords.extend(bing_keywords)
        return api_keywords
    
    def get_bing_keywords(self, tmark, letter):
        # Bing results processing. Return a list.
        url_bing = self.bing_api_url + tmark + "%20" + letter        
        try:
            response = urllib2.urlopen(url_bing)
        except urllib2.HTTPError:
            print "Exception with {}".format(url_bing)
            return None
        data = json.loads(response.read())
        bing_api_keywords = []
        if data[1]:
            for j in range(len(data[1])):
                if tmark in data[1][j]:
                    if data[1][j].startswith(tmark):
                        ind = data[1][j].find(tmark) + len(tmark)
                        to_append = data[1][j][ind:].strip()
                        # Also check if tmark is in data[1][j] and remove.
                        if re.match("[a-zA-Z0-9\- ]{" + str(len(to_append)) + "}", to_append):
                            bing_api_keywords.append(to_append)
                    else:
                        ind = data[1][j].find(tmark)
                        to_append = data[1][j][:ind].strip()
                        if re.match("[a-zA-Z0-9\- ]{" + str(len(to_append)) + "}", to_append):
                            bing_api_keywords.append(to_append)
        return bing_api_keywords

    def get_google_keywords(self, tmark, letter):
        # Google results processing. Return a list.
        url_google = self.google_api_url + tmark + "%20" + letter
        try:
            response = urllib2.urlopen(url_google)
        except urllib2.HTTPError:
            print "Exception with {}".format(url_google)
            return None
        soup = BeautifulSoup(response, "xml")
        google_api_keywords = []
        suggestions = soup.find_all("suggestion")
        for suggestion in suggestions:
            data = suggestion.get("data")
            if tmark in data:
                ind = data.find(tmark) + len(tmark)
                to_append = data[ind:].strip()
                if re.match("[a-zA-Z0-9\- ]{" + str(len(to_append)) + "}", to_append):
                    google_api_keywords.append(to_append)
        return google_api_keywords

    def visit_domain(self, tmark, domain, is_last=False):
        # Buffer requests and then send them out at once.
        
        objs = CombosquattingDomain.objects(domain=domain, trademark=tmark)
        if objs is not None and len(objs) < 1:
            if not next((x for x in self.combodomain_objs if x.domain == domain and x.trademark == tmark), None):
                self.combodomain_objs.append(CombosquattingDomain(domain=domain, trademark=tmark))
        if len(self.combodomain_objs) == self.MAX_DOMAIN_BATCH_COUNT or is_last:
            domains = [i.domain for i in self.combodomain_objs]
            gr_domains = [grequests.get("http://" + i.domain, timeout=2) if i.domain else grequests.get(None) for i in self.combodomain_objs]
            response_list = grequests.map(gr_domains, exception_handler=self.gr_exception_handler)
            try:
                assert len(response_list) == len(gr_domains) == len(domains)
            except AssertionError:
                print "Length mismatch in grequests. Returning."
                return
            for i in range(len(self.combodomain_objs)):
                self.combodomain_objs[i].url = response_list[i].url if response_list[i] is not None and response_list[i].url else "http://" + domains[i]
                self.combodomain_objs[i].response_code = self.get_status_code(response_list[i], domains[i]) if response_list[i] is not None else 0
                self.combodomain_objs[i].exists_now = True if response_list[i] is not None else self.check_domain_existence(domains[i])
                if self.is_malicious(domains[i]):
                    self.combodomain_objs[i].is_malicious = True
                # If domain doesn't already exist with this tmark, save.
                objs = CombosquattingDomain.objects(domain=domains[i], trademark=self.combodomain_objs[i].trademark)
                if objs is None or len(objs) < 1:
                    self.combodomain_objs[i].save()
                else:
                    print "Already exists: {} for tmark {}.".format(domains[i], self.combodomain_objs[i].trademark)
                    print "This should not have happened as we are only making GET reqs for unique domains."
            # Clear objs list
            self.combodomain_objs = []

    def get_status_code(self, response, domain):
        # If response code is 200, it is not guaranteed that there is no redirect.
        # Check additionally if the URL in the response is the same as the URL in the request.
        return response.status_code if not str(response.status_code).startswith('2') or domain[7:] in response.url else 300

    def gr_exception_handler(self, request, exception):
        self.exception_domains[request.url[7:]] = exception

    def check_domain_existence(self, domain):
        if not domain or not self.exception_domains.get(domain):
            print "Either domain {} is None or it doesn't exist in exception_domains while checking existence.".format(domain)
        if domain and isinstance(self.exception_domains.get(domain), requests.exceptions.ConnectionError):
            return isinstance(self.exception_domains.get(domain), requests.exceptions.ConnectTimeout)
        return False 
        
#    def visit_one_domain(self, domain):
#        if domain == '':
#            return None, None, None, None
#        try:
#            response = urllib2.urlopen("http://" + domain, timeout=2)
#            curl = pycurl.Curl()
#            curl.setopt(curl.URL, domain)
#            curl.setopt(curl.TIMEOUT, 3)
#            curl.perform()
#            response_code = curl.getinfo(pycurl.HTTP_CODE)
#            return domain, response_code, True, self.resolve_dns(domain)
#        #except urllib2.URLError as e:
            # urlopen() may have timed out but the domain might be up.
            # Check if the domain resolves to an IP.
            #ip_val = self.resolve_dns(domain)
            #exists = True if ip_val else False
            #return domain, e.code, exists, ip_val
#        except pycurl.error as e:
#            ip_val = self.resolve_dns(domain)
#            exists = True if ip_val else False
#            return domain, curl.getinfo(pycurl.HTTP_CODE), exists, ip_val
#        except ValueError as e:
#            print "For {}, ValueError was obtained - {}".format(domain, e)
#            return domain, 0, False, None
#        except Exception as e:
#            print "Exception {} for {}".format(e, domain)
#            return domain, 0, False, None
        
#    def resolve_dns(self, domain):
#        try:
#            dns_resolver = dns.resolver.Resolver()
#            dns_resolver.timeout = 3
#            dns_resolver.lifetime = 3
#            answers = dns_resolver.query(domain, 'A')
#            if len(answers) > 0:
#                return answers[0].address.encode('utf-8')
#            else:
#                print "DNS response received for domain {} but no answers.".format(domain)
#                return None
#        except (dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN), e:
#            print "Exception on DNS lookup for {}. {}".format(domain, e)
#            return None
#        except (TypeError, dns.resolver.NoNameservers), e:
#            print "Exception on DNS lookup for {}. {}".format(domain, e)
#            return None
#        except (dns.exception.Timeout, dns.resolver.NoAnswer), e:
#            print "Exception on DNS lookup for {}. {}".format(domain, e)
#            return None
#        
    def is_malicious(self, domain):
        return self.get_gsb(self.gsb_url, domain) is not "OK"
    
    def get_gsb(self, gsb_url, url):
        url_gsb_agent = 'http://{}/v4/threatMatches:find'.format(gsb_url)
        data = '{"threatInfo": {"threatEntries": [{"url": "' + url + '"}]}}'
        try:
            request = urllib2.Request(url_gsb_agent, data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(request).read()
            res_json = json.loads(response)
            if res_json.get('matches') is not None and len(res_json['matches']) > 0:
                if res_json['matches'][0].get('threatType') is not None:
                    return res_json['matches'][0]['threatType']
        except Exception as e:
            try:
                print "GSB Exception with URL {}: {}".format(url, e)
            except UnicodeEncodeError, UnicodeDecodeError:
                print "GSB Exception for a URL that cannot be decoded into ASCII."
        return "OK"


def main():
    # Main function to be used for testing only.
    connect("combosquatting", host="127.0.0.1")
    gen_model = GenerativeModel()
    with open("smaller_trademarks.txt") as f:
        tmarks = f.readlines()
    gen_model.tmarks = [x.lower().strip() for x in tmarks]
    gen_model.tmarks = map(lambda x:x.split(' ')[0].split('.')[0], gen_model.tmarks)
    for tmark in gen_model.tmarks:
        combosquatting_domains = set(gen_model.generate_combodomains_by_tmark(tmark))
        for domain in combosquatting_domains:
            if domain == combosquatting_domains[-1] and tmark == gen_model.tmarks[-1]:
                gen_model.visit_one_domain(tmark, domain, True)
            else:
                gen_model.visit_one_domain(tmark, domain)
            

if __name__ == "__main__":
    main()
