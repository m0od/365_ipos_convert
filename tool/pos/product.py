import json

from . import FullApi


class Product(FullApi):
    def __init__(self, domain, cookie):
        super().__init__(domain, cookie=cookie)
        self.PartnerId = None
        self.CategoryId = None
        self.Id = None
        self.Code = None
        self.Code2 = None
        self.Code3 = None
        self.Code4 = None
        self.Code5 = None
        self.Name = None
        self.Hidden = False
        self.Price = 0
        self.Unit = None
        self.LargeUnit = None
        self.LargeUnitCode = None
        self.PriceLargeUnit = 0
        self.Printer = None
        self.ProductType = 1
        self.IsSerialNumberTracking = False
        self.SplitForSalesOrder = False
        self.OrderQuickNotes = None
        self.DontPrintLabel = False
        self.PriceConfig = {}
        self.ConversionValue = None
        self.MaxQuantity = 999
        self.MinQuantity = 0
        self.BonusPoint = None
        self.BonusPointForAssistant = None
        self.BonusPointForAssistant2 = None
        self.BonusPointForAssistant3 = None
        self.ShowOnBranchId = []
        self.AttributesName = None
        self.ProductImages = []
        self.ProductAttributes = []
        self.CompositeItemProducts = []
        self.Formular = None
        self.OnHand = None

    def setMulPrinter(self, data):
        _ = data.strip().split(',')
        idx = 0
        while idx < len(_):
            if len(_[idx].strip()) > 0:
                self.PriceConfig.update({'SecondPrinter': _[idx].strip()})
                break
            idx += 1
        c = 3
        for i in range(idx + 1, len(_)):
            if c > 5: break
            try:
                if len(_[i].strip()) > 0:
                    self.PriceConfig.update({f'Printer{c}': _[i].strip()})
                    c += 1
            except:
                pass

    def setMulCode(self, data):
        # print(data)
        _ = str(data).strip().split(',')
        self.Code = _[0].strip()
        c = 2
        for i in range(1, 5):
            try:
                if len(_[i].strip()) > 0:
                    try:
                        exec(f'self.Code{c}={_[i].strip()}')
                        c += 1
                    except:
                        pass
            except:
                pass

    def setSplitForSalesOrder(self, data):
        _ = str(data).strip()
        if _ == '1':
            self.SplitForSalesOrder = True
        else:
            self.SplitForSalesOrder = False

    def setId(self, data):
        self.Id = str(data).strip()
        if self.Id == '0' or len(self.Id) == 0:
            self.Id = 0

    def setName(self, data):
        self.Name = data.strip()
        if len(self.Name) == 0:
            self.Name = self.Code

    def setSerial(self, data):
        _ = str(data).strip()
        if _ == '1':
            self.IsSerialNumberTracking = True
        else:
            self.IsSerialNumberTracking = False

    def setBonus(self, data):
        _ = data.strip().split(',')
        c = 0
        for i in range(len(_)):
            if c > 4: break
            if len(_[i].strip()) > 0:
                if c == 0:
                    try:
                        exec(f'self.BonusPoint = {float(_[i].strip())}')
                    except:
                        pass
                elif c == 1:
                    try:
                        exec(f'self.BonusPointForAssistant = {float(_[i].strip())}')
                    except:
                        pass
                else:
                    try:
                        exec(f'self.BonusPointForAssistant{c} = {float(_[i].strip())}')
                    except:
                        pass
                c += 1

    def setVAT(self, data):
        _ = str(data).strip()
        if len(_) > 0:
            try:
                if float(_) > 0:
                    self.PriceConfig.update({'VAT': float(_)})
            except:
                pass

    def setMaxQuantity(self, data):
        _ = str(data).strip()
        if len(_) > 0:
            try:
                self.MaxQuantity = float(_)
            except:
                pass

    def setMinQuantity(self, data):
        _ = str(data).strip()
        if len(_) > 0:
            try:
                self.MinQuantity = float(_)
            except:
                pass

    def setHidden(self, data):
        _ = str(data).strip()
        if _ == '1':
            self.Hidden = True
        else:
            self.Hidden = False

    def setPrintLabel(self, data):
        _ = str(data).strip()
        if _ == '1':
            self.PriceConfig.update({'DontPrintLabel': True})
        else:
            self.PriceConfig.update({'DontPrintLabel': False})

    def setOpenTopping(self, data):
        _ = str(data).strip()
        if _ == '1':
            self.PriceConfig.update({'OpenTopping': True})
        else:
            self.PriceConfig.update({'OpenTopping': False})

    def setShowBranch(self, data):
        _ = str(data).strip().split(',')
        for i in range(len(_)):
            if len(_[i].strip()) > 0:
                self.ShowOnBranchId.append(json.dumps([int(_[i].strip())]))
        # print(self.ShowOnBranchId)

    def setImage(self, data):
        _ = data.strip().split(',')
        for i in range(len(_)):
            self.ProductImages.append({'ImageURL': _[i].strip(), 'ThumbnailUrl': _[i].strip()})

    def setProductAttributes(self, data):
        _ = data.strip().split(',')
        for i in range(len(_)):
            if len(_[i].strip()) > 0:
                self.ProductAttributes.append({
                    'AttributeName': _[i].split(':')[0].strip(),
                    'AttributeValue': _[i].split(':')[1].strip(),
                })

    def setCompositeItemProducts(self, data):
        _ = data.strip().split(',')
        for i in range(len(_)):
            if len(_[i].strip()) > 0:
                id = self.product_by_code(_[i].split('=')[0].strip())
                if id is not None:
                    self.CompositeItemProducts.append({
                        'ItemId': id,
                        'Quantity': _[i].split('=')[1].strip()
                    })

    # def ignore_null(_):
    #     """recursively remove empty lists, empty dicts, or None elements from a dictionary"""
    #
    #     def empty(x):
    #         return x is None or x == {} or x == []
    #
    #     if not isinstance(_, (dict, list)):
    #         return _
    #     elif isinstance(_, list):
    #         return [v for v in (ignore_bull(v) for v in _) if not empty(v)]
    #     else:
    #         return {k: v for k, v in ((k, ignore_bull(v)) for k, v in _.items()) if not empty(v)}
    def setCategory(self, data):
        if len(str(data).strip()) > 0:
            self.CategoryId = self.category_save(str(data).strip())
        else:
            self.CategoryId = None

    def setPartner(self, data):
        if len(str(data).strip()) == 0:
            self.PartnerId = self.search_partner(str(data).strip())

    def toJson(self):
        return {
            'Product': {
                'Id': self.Id,
                'Code': self.Code,
                'Code2': self.Code2,
                'Code3': self.Code3,
                'Code4': self.Code4,
                'Code5': self.Code5,
                'Name': self.Name,
                'Price': self.Price,
                'PriceLargeUnit': self.PriceLargeUnit,
                'PriceConfig': json.dumps(self.PriceConfig),
                'Printer': self.Printer,
                'ProductImages': self.ProductImages,
                'ProductType': self.ProductType,
                'SplitForSalesOrder': self.SplitForSalesOrder,
                'Unit': self.Unit,
                'AttributesName': self.AttributesName,
                'BonusPoint': self.BonusPoint,
                'BonusPointForAssistant': self.BonusPointForAssistant,
                'BonusPointForAssistant2': self.BonusPointForAssistant2,
                'BonusPointForAssistant3': self.BonusPointForAssistant3,
                'CategoryId': self.CategoryId,
                'ConversionValue': self.ConversionValue,
                'Hidden': self.Hidden,
                'IsSerialNumberTracking': self.IsSerialNumberTracking,
                'ShowOnBranchId': self.ShowOnBranchId,
                'ProductAttributes': self.ProductAttributes,
                'CompositeItemProducts': self.CompositeItemProducts,
                'Formular': self.Formular
            },
            # 'OnHand': self.OnHand,
            # 'CompareOnHand': self.OnHand
            'ProductPartners': [{
                'PartnerId': self.PartnerId
            }]
        }

