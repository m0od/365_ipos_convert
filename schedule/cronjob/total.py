from os.path import dirname




def main():
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
    aristino = Aristino()
    matviet = MatViet()
    elise = Elise()
    dchic = Dchic()
    hoangphuc = HoangPhuc()
    routine = Routine()
    pnj = PNJ_AMHD()
    now = datetime.now(timezone('Etc/GMT-7'))
    if now.hour < 10:
        with futures.ThreadPoolExecutor(max_workers=15) as mt:
            thread = [
                mt.submit(tgc_bloom.get_data, now - timedelta(days=1)),
                mt.submit(ao.get_data, (now - timedelta(days=1))),
                mt.submit(bl.get_data, (now - timedelta(days=1))),
                mt.submit(at.get_data, (now - timedelta(days=1))),
                mt.submit(atk.get_data, (now - timedelta(days=1))),
                mt.submit(jm.get_data, now - timedelta(days=1)),
                mt.submit(lemino.get_data, now - timedelta(days=1)),
                mt.submit(boo.get_data, now - timedelta(days=1)),
                mt.submit(atz.get_data, now - timedelta(days=1)),
                mt.submit(adore.get_data, now - timedelta(days=1), now),
                mt.submit(kakao.get_data, now - timedelta(days=1), now),
                mt.submit(sneaker.get_data, now - timedelta(days=1)),
                mt.submit(vans.get_data, now - timedelta(days=1)),
                mt.submit(aristino.get_data, now - timedelta(days=1)),
                mt.submit(elise.get_data, now - timedelta(days=1)),
                mt.submit(dchic.get_data, now - timedelta(days=1)),
                mt.submit(hoangphuc.get_data, now - timedelta(days=1)),
                # mt.submit(pnj.get_data),
            ]
            futures.as_completed(thread)
    elif now.hour == 10:
        # for i in range(1,24):
        with futures.ThreadPoolExecutor(max_workers=4) as mt:
            thread = [
                mt.submit(ato.get_data, now - timedelta(days=1), now - timedelta(days=1)),
                mt.submit(megane.get_data, now - timedelta(days=1)),
                mt.submit(matviet.get_data, now - timedelta(days=1)),
                mt.submit(routine.get_data),
            ]
            futures.as_completed(thread)
    elif now.hour == 12:
        # for i in range(1,24):
        with futures.ThreadPoolExecutor(max_workers=1) as mt:
            thread = [
                mt.submit(pnj.get_data)
            ]
            futures.as_completed(thread)


if __name__ == '__main__':
    import sys
    import warnings

    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from schedule.client_api.megane import MeganePrince
    from schedule.client_api.boo import Boo
    from schedule.client_api.lemino import Lemino
    from schedule.client_api.sneaker_buzz import SneakerBuzz
    from schedule.client_api.vans import Vans
    from schedule.client_api.ato import ATO
    from schedule.client_api.anta import Anta
    from schedule.client_api.antakids import AntaKids
    from schedule.client_api.atz import ATZ
    from schedule.client_api.balabala import Balabala
    from schedule.client_api.jm import JM
    from schedule.client_api.tgc_bloom import TGC_BLOOM
    from schedule.client_api.matviet import MatViet
    from schedule.client_api.hoangphuc import HoangPhuc
    from concurrent import futures
    from datetime import datetime, timedelta
    from pytz import timezone
    from schedule.client_api.aokang import AoKang
    from schedule.client_api.adore import Adore
    from schedule.client_api.kakao import Kakao
    from schedule.client_api.aristino import Aristino
    from schedule.client_api.elise import Elise
    from schedule.client_api.dchic import Dchic
    from schedule.client_api.routine_amhd import Routine
    from schedule.client_api.pnj_amhd import PNJ_AMHD
    warnings.filterwarnings('ignore')
    main()
