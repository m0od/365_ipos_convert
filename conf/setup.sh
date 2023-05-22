#!/bin/sh
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