import time
from concurrent import futures
import multiprocessing as mp
import time
from datetime import datetime

import json
a = json.loads('[]')
print(type(a))
print(f"|{', '.join(str(_[0]) for _ in a).strip()}|")