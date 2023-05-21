#!/bin/sh
cd /home/blackwings/365ipos/conf
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

# SQL
# GRANT USAGE ON *.* TO 'root'@localhost IDENTIFIED BY '7y!FY^netG!jn>f+';
# GRANT USAGE ON *.* TO 'ykbsaqlb_wp725'@localhost IDENTIFIED BY '4g5j.o0p@S';
