from multiprocessing import cpu_count

bind = 'unix:/home/blackwings/webtool/tool/techtool.sock'
workers = 32
worker_class = 'uvicorn.workers.UvicornWorker'
