#!/bin/sh

#env Centos7.9.2009
yum -y update
echo "[mariadb]
name = MariaDB
baseurl = http://mirror.mariadb.org/yum/10.11.6/centos/8/x86_64
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

cd /home/adapter/webtool/conf
cp redis_6380.conf /etc/redis_6380.conf
cp redis_6380.service /usr/lib/systemd/system/redis_6380.service
systemctl start redis_6380
systemctl enable redis_6380
systemctl start redis
systemctl enable redis

cp adapter_web.service /etc/systemd/system/adapter_web.service
systemctl daemon-reload
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
cp /www/wwwroot/adapter/conf/client/amhd_acfc@.service /etc/systemd/system/amhd_acfc@.service
cp /www/wwwroot/adapter/conf/client/amhd_api@.service /etc/systemd/system/amhd_api@.service
cp /www/wwwroot/adapter/conf/client/amhd_augges@.service /etc/systemd/system/amhd_augges@.service
cp /www/wwwroot/adapter/conf/client/amhd_golden_gate@.service /etc/systemd/system/amhd_golden_gate@.service
cp /www/wwwroot/adapter/conf/client/amhd_kiotviet@.service /etc/systemd/system/amhd_kiotviet@.service
cp /www/wwwroot/adapter/conf/client/amhd_misa@.service /etc/systemd/system/amhd_misa@.service
cp /www/wwwroot/adapter/conf/client/amhd_mmenu@.service /etc/systemd/system/amhd_mmenu@.service
cp /www/wwwroot/adapter/conf/client/amhd_nhanh@.service /etc/systemd/system/amhd_nhanh@.service
cp /www/wwwroot/adapter/conf/client/amhd_sapo@.service /etc/systemd/system/amhd_sapo@.service
cp /www/wwwroot/adapter/conf/client/amhd_cloud@.service /etc/systemd/system/amhd_cloud@.service
cp /www/wwwroot/adapter/conf/client/amhd_txt@.service /etc/systemd/system/amhd_txt@.service
cp /www/wwwroot/adapter/conf/client/amhd_gmail@.service /etc/systemd/system/amhd_gmail@.service
cp /www/wwwroot/adapter/conf/client/amhd_csv@.service /etc/systemd/system/amhd_csv@.service
cp /www/wwwroot/adapter/conf/client/amhd_xls@.service /etc/systemd/system/amhd_xls@.service
cp /www/wwwroot/adapter/conf/client/amhd_xlsx@.service /etc/systemd/system/amhd_xlsx@.service
cp /www/wwwroot/adapter/conf/client/amhd_payment@.service /etc/systemd/system/amhd_payment@.service


0 6 * * * /usr/bin/certbot renew --nginx >/dev/null 2>&1
*/10 * * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/resend.py >/dev/null 2>&1
30 12 * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/mail_report.py >/dev/null 2>&1
0 0 * * * /home/blackwings/webtool/bin/python /home/blackwings/webtool/schedule/cronjob/shooz.py >/dev/null 2>&1

0 12 * * * /usr/bin/systemctl start amhd_payment@103
0 12 * * * /usr/bin/systemctl start amhd_payment@185
0 12 * * * /usr/bin/systemctl start amhd_payment@186
0 12 * * * /usr/bin/systemctl start amhd_payment@187

15 5 * * * /usr/bin/systemctl start amhd_gmail@003 # Skecher
0 11 * * * /usr/bin/systemctl start amhd_gmail@177 # Breadtalk

0 0 * * * /usr/bin/systemctl start amhd_api@056
0 0 * * * /usr/bin/systemctl start amhd_api@059 # Bloom
0 0 * * * /usr/bin/systemctl start amhd_api@060 # TGC
0 0 * * * /usr/bin/systemctl start amhd_api@110 # Boo
0 0 * * * /usr/bin/systemctl start amhd_api@113
0 0 * * * /usr/bin/systemctl start amhd_api@127 # Elise
0 0 * * * /usr/bin/systemctl start amhd_api@139
0 0 * * * /usr/bin/systemctl start amhd_api@140 # Aristino
0 0 * * * /usr/bin/systemctl start amhd_api@141 # Dchic
0 0 * * * /usr/bin/systemctl start amhd_api@146
0 12 * * * /usr/bin/systemctl start amhd_api@102 # Lock&Lock

0 5 * * * /usr/bin/systemctl start amhd_kiotviet@025 # Rabity
0 5 * * * /usr/bin/systemctl start amhd_kiotviet@041 # Kakao
0 5 * * * /usr/bin/systemctl start amhd_kiotviet@055 # Adore
0 5 * * * /usr/bin/systemctl start amhd_kiotviet@070 # Wundertute
0 5 * * * /usr/bin/systemctl start amhd_kiotviet@151 # Gabby

0 0 * * * /usr/bin/systemctl start amhd_augges@065 # Aokang
0 0 * * * /usr/bin/systemctl start amhd_augges@069 # Balabala
0 0 * * * /usr/bin/systemctl start amhd_augges@100 # Anta
0 0 * * * /usr/bin/systemctl start amhd_augges@101 # AntaKids


0 0 * * * /usr/bin/systemctl start amhd_misa@108 # SneakerBuzz
0 0 * * * /usr/bin/systemctl start amhd_misa@109 # Vans

0 0 * * * /usr/bin/systemctl start amhd_sapo@181 # Inochi

0 2 * * * /usr/bin/systemctl start amhd_mmenu@148 # Jajang

0 9 * * * /usr/bin/systemctl start amhd_nhanh@037 # ATZ
0 9 * * * /usr/bin/systemctl start amhd_nhanh@043 # JM
0 9 * * * /usr/bin/systemctl start amhd_nhanh@165 # Mulgati

0 12 * * * /usr/bin/systemctl start amhd_golden_gate@150 # Gogi
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@162 # Kichi Kichi
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@179 # Manwah
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@180 # Sumo BBQ
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@182 # Kpub Yutang
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@184 # Isushi
0 12 * * * /usr/bin/systemctl start amhd_golden_gate@188 # Ktop

55 9 * * * /usr/bin/systemctl start amhd_acfc@152
55 9 * * * /usr/bin/systemctl start amhd_acfc@153
55 9 * * * /usr/bin/systemctl start amhd_acfc@154
55 9 * * * /usr/bin/systemctl start amhd_acfc@155
55 9 * * * /usr/bin/systemctl start amhd_acfc@156
55 9 * * * /usr/bin/systemctl start amhd_acfc@157
55 9 * * * /usr/bin/systemctl start amhd_acfc@158
55 9 * * * /usr/bin/systemctl start amhd_acfc@159
55 9 * * * /usr/bin/systemctl start amhd_acfc@160
55 9 * * * /usr/bin/systemctl start amhd_acfc@161

0 3 * * * /usr/bin/systemctl start amhd_csv@045 # IvyModa
0 3 * * * /usr/bin/systemctl start amhd_csv@190 # KOI
0 12 * * * /usr/bin/systemctl start amhd_csv@192 # Kohnan

0 12 * * * /usr/bin/systemctl start amhd_txt@120 # Timezone
15 4 * * * /usr/bin/systemctl start amhd_txt@163 # NKID
0 12 * * * /usr/bin/systemctl start amhd_txt@167 # McDonald
15 9 * * * /usr/bin/systemctl start amhd_txt@173 # Pizza4P
0 4 * * * /usr/bin/systemctl start amhd_txt@175 # TheBodyShop

0 12 * * * /usr/bin/systemctl start amhd_xls@169
0 0 * * * /usr/bin/systemctl start amhd_xls@171
0 0 * * * /usr/bin/systemctl start amhd_xls@183
0 0 * * * /usr/bin/systemctl start amhd_xls@191
0 0 * * * /usr/bin/systemctl start amhd_xls@199

0 12 * * * /usr/bin/systemctl start amhd_cloud@174
0 12 * * * /usr/bin/systemctl start amhd_cloud@178

0 0 * * * /usr/bin/systemctl start amhd_xlsx@057
0 0 * * * /usr/bin/systemctl start amhd_xlsx@067
0 0 * * * /usr/bin/systemctl start amhd_xlsx@114
5 0 * * * /usr/bin/systemctl start amhd_xlsx@119
0 0 * * * /usr/bin/systemctl start amhd_xlsx@136
0 12 * * * /usr/bin/systemctl start amhd_xlsx@142
0 12 * * * /usr/bin/systemctl start amhd_xlsx@147
0 0 * * * /usr/bin/systemctl start amhd_xlsx@164
0 0 * * * /usr/bin/systemctl start amhd_xlsx@168
0 12 * * * /usr/bin/systemctl start amhd_xlsx@172
0 12 * * * /usr/bin/systemctl start amhd_xlsx@189
0 11 * * * /usr/bin/systemctl start amhd_xlsx@193

