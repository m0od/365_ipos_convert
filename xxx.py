import time
from concurrent import futures
import multiprocessing as mp
import time
from datetime import datetime

import json
a = json.loads('[[622],[620]]')
print(type(a))
print(', '.join(str(_[0]) for _ in a).strip())