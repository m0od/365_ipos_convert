import sys

sys.path.append('/home/blackwings/365ipos')
from client_api.megane import MeganePrince
from client_api.boo import Boo
from client_api.lemino import Lemino
from client_api.sneaker_buzz import SneakerBuzz
from client_api.vans import Vans
from client_api.ato import ATO
from client_api.anta import Anta
from client_api.antakids import AntaKids
from client_api.atz import ATZ
from client_api.balabala import Balabala
from client_api.jm import JM
from client_api.tgc_bloom import TGC_BLOOM
from concurrent import futures
from datetime import datetime, timedelta
from pytz import timezone
from client_api.aokang import AoKang
from client_api.adore import Adore
from client_api.kakao import Kakao

tgc_bloom = TGC_BLOOM()
ao = AoKang()
bl = Balabala()
at = Anta()
atk = AntaKids()
jm = JM()
lemino = Lemino()
boo = Boo()
atz = ATZ()
adore = Adore()
kakao = Kakao()
sneaker = SneakerBuzz()
vans = Vans()
ato = ATO()
megane = MeganePrince()
now = datetime.now(timezone('Etc/GMT-7'))
if now.hour < 9:
    with futures.ThreadPoolExecutor(max_workers=13) as mt:
        thread = [
            mt.submit(tgc_bloom.get_data, now - timedelta(days=1)),
            mt.submit(ao.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            mt.submit(bl.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            mt.submit(at.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            mt.submit(atk.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            mt.submit(jm.get_data, (now - timedelta(days=1)).strftime('%Y-%m-%d')),
            mt.submit(lemino.get_data, now - timedelta(days=1)),
            mt.submit(boo.get_data, now - timedelta(days=1)),
            mt.submit(atz.get_data, (now - timedelta(days=1)).strftime('%Y-%m-%d')),
            mt.submit(adore.get_data, now - timedelta(days=1), now),
            mt.submit(kakao.get_data, now - timedelta(days=1), now),
            mt.submit(sneaker.get_data, now - timedelta(days=1)),
            mt.submit(vans.get_data, now - timedelta(days=1))
        ]
        futures.as_completed(thread)
else:
    with futures.ThreadPoolExecutor(max_workers=2) as mt:
        thread = [
            mt.submit(ato.get_data, now - timedelta(days=1), now - timedelta(days=1)),
            mt.submit(megane.get_data, now - timedelta(days=1))
            # mt.submit(ao.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            # mt.submit(bl.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            # mt.submit(at.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
            # mt.submit(atk.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
        ]
        futures.as_completed(thread)
