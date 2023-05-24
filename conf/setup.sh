#!/bin/sh

#env Centos7.9.2009
yum -y update
echo "[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.11.3/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1" > /etc/yum.repos.d/MariaDB.repo
yum clean all
yum -y group install "Development Tools"
yum -y install epel-release
yum -y install centos-release-scl
yum -y install nano mariadb-server mariadb-devel nginx redis gcc perl-core pcre-devel wget zlib-devel devtoolset-8
scl enable devtoolset-8 -- bash
wget https://ftp.openssl.org/source/openssl-3.1.0.tar.gz
tar -xvf openssl-3.1.0.tar.gz
rm -rf openssl-3.1.0.tar.gz
cd openssl-3.1.0
./config --prefix=/usr --openssldir=/etc/ssl --libdir=lib no-shared zlib-dynamic
make && make install
echo "export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64" > /etc/profile.d/openssl.sh
source /etc/profile.d/openssl.sh
cd .. && rm -rf openssl-3.1.0
wget https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz
tar -xvf Python-3.11.3.tgz
rm -rf Python-3.11.3.tgz
cd Python-3.11.3
./configure --enable-optimizations --with-openssl=/usr
make altinstall
cd .. && rm -rf Python-3.11.3
mkdir test
python3.11 -m venv test
cd test
source bin/activate
pip install uwsgi

cd /home/blackwings/webtool/conf
cp redis_6380.conf /etc/redis_6380.conf
cp redis_6380.service /usr/lib/systemd/system/redis_6380.service
systemctl start redis_6380
systemctl enable redis_6380
systemctl start redis
systemctl enable redis

cp adapter_web.service /etc/systemd/system/adapter_web.service
systemctl start adapter_web
systemctl enable adapter_web

cp converter.service /etc/systemd/system/converter.service
systemctl start converter
systemctl enable converter

cp technical.service /etc/systemd/system/technical.service
systemctl start technical
systemctl enable technical

cp adapter.nginx.conf /etc/nginx/conf.d/adapter.nginx.conf
cp /etc/letsencrypt/live/adapter.pos365.vn/cert.pem ../webgui/cert.pem
cp /etc/letsencrypt/live/adapter.pos365.vn/privkey.pem ../webgui/privkey.pem
chown blackwings:blackwings ../webgui/cert.pem
chown blackwings:blackwings ../webgui/privkey.pem

yes | cp /root/ssh_local.service /etc/systemd/system/ssh_local.service
systemctl daemon-reload
systemctl restart ssh_local
systemctl status ssh_local -l
# SQL
# GRANT USAGE ON *.* TO 'root'@localhost IDENTIFIED BY '7y!FY^netG!jn>f+';
# GRANT USAGE ON *.* TO 'ykbsaqlb_wp725'@localhost IDENTIFIED BY '4g5j.o0p@S';

*/10 * * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/resend.py >/dev/null 2>&1
0 10 * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/mail_report.py >/dev/null 2>&1
1 0 * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/total.py >/dev/null 2>&1
45 9 * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/total.py >/dev/null 2>&1