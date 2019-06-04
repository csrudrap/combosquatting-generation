git clone https://github.com/christiandt/google-safebrowsing-docker.git
sed -i 's/FROM golang:1.6/FROM golang:1.7/g' google-safebrowsing-docker/Dockerfile
apt-get install -y python-pip
apt-get install -y libcurl4-openssl-dev
pip install -r requirements.txt
apt-get install -y docker.io
cd google-safebrowsing-docker
docker build -t gsb-local-agent .
mkdir -p /root/scripts/gsb_docker/
cd ..
cp gsb_docker.sh /root/scripts/gsb_docker/
cp apikeys.conf /root/scripts/gsb_docker/
cp get_google_key.py /root/scripts/gsb_docker/
cp gsb-docker.service /etc/systemd/system/
cd /etc/systemd/system;sudo systemctl enable gsb-docker.service
apt-get install -y mongodb mongodb-clients
mkdir /data
mkdir /data/db
systemctl enable mongodb
systemctl start gsb-docker
