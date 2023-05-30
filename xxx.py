import time
from concurrent import futures
import multiprocessing as mp
import time
from datetime import datetime

import json
b = ["[152759]", "[132942]", "[31236]"]
x = {"ShowOnBranchId": b}
print(json.dumps(x, separators=(',', ':')))