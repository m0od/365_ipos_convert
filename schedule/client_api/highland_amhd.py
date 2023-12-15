import os
f = open('test.txt', 'r')
_ = f.read().strip().split('\n')
f.close()
branch = {}
for __ in _:
    ___ = __.split()
    branch.update({___[0]: ___[1]})
for x,y,z in os.walk('../AMHD'):
    for _ in z:
        if _.startswith('am'):
            f = os.path.join(x, _)
            f = open(f, 'r')
            s = f.read()
            f.close()
            retailer = s.split('self.ADAPTER_RETAILER')[1].split("'")[1].split("'")[0]
            token = s.split('self.ADAPTER_TOKEN')[1].split("'")[1].split("'")[0]
            if not branch.get(retailer) == token:
                print(retailer, branch.get(retailer) == token)