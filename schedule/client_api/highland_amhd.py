class HIGHLANDS_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = '80_amhd'
        self.ADAPTER_TOKEN = '9efbf2b6aa6337f497c9a060b0fc2e658f27d06af0b514de3d50ba552af7f00a'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = '80_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '*xlsx'
        self.DATA = None
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        files = glob.glob(self.FULL_PATH + self.EXT)
        self.DATA = max(files, key=os.path.getmtime)
        print(self.DATA)