# To get one line of the answer section of the SOA Records for each of the 150 trademarks.

import subprocess

with open("smaller_trademarks.txt") as f:
    tmarks_domains = f.readlines()
tmarks_domains = [x.lower().strip() for x in tmarks_domains]
tmarks_domains = map(lambda x:x.split(' ')[0], tmarks_domains)
count = 0
for domain in tmarks_domains:
    cmd = "dig SOA {} | sed -e '1,/ANSWER SECTION/d'".format(domain)
    try:
        op = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        print "Couldn't execute command for domain {}".format(domain)
        continue
    with open("soa_dig_alexatop150.txt", "a+") as f:
        f.write(op.split('\n')[0] + "\n")
