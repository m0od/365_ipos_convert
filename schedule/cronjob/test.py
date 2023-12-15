from crontab import CronTab
cron = CronTab(user='root')
for job in cron:
    print(job)
    print()