from os.path import dirname




def main():
    tgc = TGC()
    bloom = Bloom()
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
    ftp_routine = Routine()
    pnj = PNJ_AMHD()
    gabby = Gabby()
    jajang = JaJang()
    ftp_typo = TYPO_AMHD()
    ftp_banana_amhd = BANANA_REPUBLIC_AMHD()
    ftp_tommy_amhd = TOMMY_AMHD()
    ftp_cotton_on_amhd = COTTON_ON_AMHD()
    ftp_mango_amhd = MANGO()
    ftp_levis_amhd = LEVIS()
    ftp_nike_amhd = NIKE_AMHD()
    ftp_fitflop_amhd = FITFLOP_AMHD()
    ftp_gap_kids_amhd = GAP_KIDS_AMHD()
    ftp_mothercare = MOTHERCARE()
    ftp_shooz_amhd =SHOOZ_AMHD()
    ftp_yves_roucher = YVES_ROCHER_AMHD()
    ftp_alfresco_amhd = ALFRESCO_AMHD()
    ftp_vera_jockey_amhd = VERA_JOCKEY_AMHD()
    now = datetime.now(timezone('Etc/GMT-7'))
    if now.hour < 10:
        # print('abc')
        with futures.ThreadPoolExecutor(max_workers=17) as mt:
            thread = [
                mt.submit(tgc.get_data, now - timedelta(days=1)),
                mt.submit(bloom.get_data, now - timedelta(days=1)),
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
                # mt.submit(dchic.get_data, now - timedelta(days=1)),
                mt.submit(hoangphuc.get_data, now - timedelta(days=1)),
                mt.submit(gabby.get_data, now - timedelta(days=1), now),
                mt.submit(jajang.get_data, now - timedelta(days=1)),
            ]
            futures.as_completed(thread)
    elif now.hour == 10:
        # for i in range(1,24):
        with futures.ThreadPoolExecutor(max_workers=18) as mt:
            thread = [
                mt.submit(ato.get_data, now - timedelta(days=1), now - timedelta(days=1)),
                mt.submit(megane.get_data, now - timedelta(days=1)),
                mt.submit(matviet.get_data, now - timedelta(days=1)),
                mt.submit(ftp_routine.get_data),
                mt.submit(ftp_typo.get_data),
                mt.submit(ftp_banana_amhd.get_data),
                mt.submit(ftp_tommy_amhd.get_data),
                mt.submit(ftp_cotton_on_amhd.get_data),
                mt.submit(ftp_mango_amhd.get_data),
                mt.submit(ftp_levis_amhd.get_data),
                mt.submit(ftp_nike_amhd.get_data),
                mt.submit(ftp_fitflop_amhd.get_data),
                mt.submit(ftp_gap_kids_amhd.get_data),
                mt.submit(ftp_mothercare.get_data),
                mt.submit(ftp_shooz_amhd.get_data),
                mt.submit(ftp_yves_roucher.get_data),
                mt.submit(ftp_alfresco_amhd.get_data),
                mt.submit(ftp_vera_jockey_amhd.get_data),
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
    from schedule.client_api.tgc_amhd import TGC
    from schedule.client_api.bloom_amhd import Bloom
    from schedule.client_api.matviet import MatViet
    from schedule.client_api.hoangphuc import HoangPhuc
    from schedule.client_api.vera_jockey_amhd import VERA_JOCKEY_AMHD
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
    from schedule.client_api.gabby_amhd import Gabby
    from schedule.client_api.jajang_amhd import JaJang
    from schedule.client_api.typo_amhd import TYPO_AMHD
    from schedule.client_api.banana_republic_amhd import BANANA_REPUBLIC_AMHD
    from schedule.client_api.tommy_amhd import TOMMY_AMHD
    from schedule.client_api.cotton_on import COTTON_ON_AMHD
    from schedule.client_api.mango_amhd import MANGO
    from schedule.client_api.levis_amhd import LEVIS
    from schedule.client_api.nike_amhd import NIKE_AMHD
    from schedule.client_api.fitflop_amhd import FITFLOP_AMHD
    from schedule.client_api.gap_kids_amhd import GAP_KIDS_AMHD
    from schedule.client_api.mothercare_amhd import MOTHERCARE
    from schedule.client_api.shooz_amhd import SHOOZ_AMHD
    from schedule.client_api.yves_amhd import YVES_ROCHER_AMHD
    from schedule.client_api.alfresco_amhd import ALFRESCO_AMHD
    warnings.filterwarnings('ignore')
    main()
