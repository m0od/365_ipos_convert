from os.path import dirname




def main():
    jm = JM()
    lemino = Lemino()
    atz = ATZ()
    kakao = Kakao()
    megane = MeganePrince()
    matviet = MatViet()
    ftp_routine = Routine()
    pnj = PNJ_AMHD()
    gabby = Gabby()
    jajang = JaJang()
    mail_breadtalk = BreadTalkAMHD()
    drive_laneige_amhd = LaneigeAMHD()
    drive_yanghao = YangHaoAMHD()
    wundertute_amhd = WundertuteAMHD()
    mulgati_amhd = MULGATI_AMHD()
    rabity_amhd = RABITY_AMHD()
    maison_charles_keith_amhd = CharlesKeithAMHD()
    maison_mlb_amhd = MLBAMHD()
    maison_pedro_amhd = PedroAMHD()
    acfc_typo = TYPO_AMHD()
    acfc_banana_amhd = BANANA_REPUBLIC_AMHD()
    acfc_tommy_amhd = TOMMY_AMHD()
    acfc_cotton_on_amhd = COTTON_ON_AMHD()
    acfc_mango_amhd = MANGO()
    acfc_levis_amhd = LEVIS()
    acfc_nike_amhd = NIKE_AMHD()
    acfc_fitflop_amhd = FITFLOP_AMHD()
    acfc_gap_kids_amhd = GAP_KIDS_AMHD()
    acfc_mothercare = MOTHERCARE()
    ftp_shooz_amhd =SHOOZ_AMHD()
    ftp_yves_roucher = YVES_ROCHER_AMHD()
    ftp_alfresco_amhd = ALFRESCO_AMHD()
    ftp_vera_jockey_amhd = VERA_JOCKEY_AMHD()
    ftp_timezone_amhd = TimeZoneAMHD()
    # ftp_nkid_amhd = NKID_AMHD()
    ftp_mc_donald_amhd = McDonaldAMHD()
    ftp_mr_dak_amhd = MR_DAK_AMHD()
    ftp_mazano_amhd = MAZANO_AMHD()
    ftp_innis_free_amhd = INNIS_FREE_AMHD()
    ftp_the_body_shop_amhd = TheBodyShopAMHD()
    ftp_dream_kids_amhd = DREAM_KIDS_AMHD()
    ftp_koi_amhd = KOIAMHD()
    ftp_converse_newera_amhd = ConverseNeweraAMHD()
    now = datetime.now(timezone('Etc/GMT-7'))
    if now.hour ==11:
        with futures.ThreadPoolExecutor(max_workers=19) as mt:
            thread = [
                mt.submit(INOCHI_AMHD().get_data),
                mt.submit(wundertute_amhd.get_data, now - timedelta(days=1), now),
                mt.submit(lemino.get_data, now - timedelta(days=1)),
                mt.submit(kakao.get_data, now - timedelta(days=1), now),
                mt.submit(gabby.get_data, now - timedelta(days=1), now),
                mt.submit(jajang.get_data, now - timedelta(days=1)),
                mt.submit(mulgati_amhd.get_data, now - timedelta(days=1)),
                mt.submit(rabity_amhd.get_data, now - timedelta(days=1), now)
            ]
            futures.as_completed(thread)
    elif now.hour == 1:
        with futures.ThreadPoolExecutor(max_workers=1) as mt:
            thread = [
                mt.submit(ftp_koi_amhd.get_data)
            ]
            futures.as_completed(thread)
    elif now.hour == 11:
        with futures.ThreadPoolExecutor(max_workers=2) as mt:
            thread = [
                mt.submit(mail_breadtalk.get_data),
                mt.submit(TasakiBBQAMHD().get_data)
            ]
            futures.as_completed(thread)
    elif now.hour == 10:
        with futures.ThreadPoolExecutor(max_workers=5) as mt:
            thread = [
                mt.submit(megane.get_data, now - timedelta(days=1)),
                mt.submit(matviet.get_data, now - timedelta(days=1)),
                mt.submit(SKECHERS_AMHD().get_data), #mail

            ]
            futures.as_completed(thread)
    elif now.hour == 12:
        with futures.ThreadPoolExecutor(max_workers=34) as mt:
            thread = [
                mt.submit(jm.get_data, now - timedelta(days=1)),
                mt.submit(atz.get_data, now - timedelta(days=1)),
                mt.submit(drive_laneige_amhd.get_data),
                mt.submit(drive_yanghao.get_data),
                mt.submit(maison_charles_keith_amhd.get_data),
                mt.submit(maison_mlb_amhd.get_data),
                mt.submit(maison_pedro_amhd.get_data),
                mt.submit(pnj.get_data),
                mt.submit(acfc_typo.get_data),
                mt.submit(acfc_banana_amhd.get_data),
                mt.submit(acfc_tommy_amhd.get_data),
                mt.submit(acfc_cotton_on_amhd.get_data),
                mt.submit(acfc_mango_amhd.get_data),
                mt.submit(acfc_levis_amhd.get_data),
                mt.submit(acfc_nike_amhd.get_data),
                mt.submit(acfc_fitflop_amhd.get_data),
                mt.submit(acfc_gap_kids_amhd.get_data),
                mt.submit(acfc_mothercare.get_data),
                mt.submit(ftp_routine.get_data),
                mt.submit(ftp_shooz_amhd.get_data),
                # mt.submit(ftp_yves_roucher.get_data),
                mt.submit(ftp_alfresco_amhd.get_data),
                mt.submit(ftp_vera_jockey_amhd.get_data),
                mt.submit(ftp_timezone_amhd.get_data),
                # mt.submit(ftp_nkid_amhd.get_data),
                mt.submit(ftp_mc_donald_amhd.get_data),
                mt.submit(ftp_mr_dak_amhd.get_data),
                mt.submit(ftp_mazano_amhd.get_data),
                mt.submit(ftp_innis_free_amhd.get_data),
                mt.submit(ftp_the_body_shop_amhd.get_data),
                mt.submit(ftp_dream_kids_amhd.get_data),
                mt.submit(ftp_converse_newera_amhd.get_data),
                mt.submit(KohnanAMHD().get_data), #FTP
                mt.submit(CON_CUNG_AMHD().get_data), #FTP
            ]
            futures.as_completed(thread)
    elif now.hour == 2:
        with futures.ThreadPoolExecutor(max_workers=1) as mt:
            thread = [
                mt.submit(ftp_mc_donald_amhd.get_data),
                # mt.submit(ftp_converse_newera_amhd.get_data),
            ]
            futures.as_completed(thread)
    # elif now.hour == 17:
    #     with futures.ThreadPoolExecutor(max_workers=3) as mt:
    #         thread = [
    #             mt.submit(boo.get_data, now - timedelta(days=3)),
    #             # mt.submit(boo.get_data, now - timedelta(days=4)),
    #             # mt.submit(boo.get_data, now - timedelta(days=5)),
    #             # mt.submit(boo.get_data, now - timedelta(days=6)),
    #             mt.submit(ftp_innis_free_amhd.get_data)
    #             # mt.submit(ftp_timezone_amhd.get_data),
    #             # mt.submit(acfc_typo.get_data),
    #             # mt.submit(acfc_banana_amhd.get_data),
    #             # mt.submit(acfc_tommy_amhd.get_data),
    #             # mt.submit(acfc_cotton_on_amhd.get_data),
    #             # mt.submit(acfc_mango_amhd.get_data),
    #             # mt.submit(acfc_levis_amhd.get_data),
    #             # mt.submit(acfc_nike_amhd.get_data),
    #             # mt.submit(acfc_fitflop_amhd.get_data),
    #             # mt.submit(acfc_gap_kids_amhd.get_data),
    #             # mt.submit(acfc_mothercare.get_data),
    #         ]
    #         futures.as_completed(thread)

if __name__ == '__main__':
    import sys
    import warnings

    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from schedule.AMHD.api.megane import MeganePrince
    from schedule.AMHD.api.lemino import Lemino
    from schedule.AMHD.nhanh.atz import ATZ
    from schedule.AMHD.nhanh.jm import JM
    from schedule.AMHD.api.matviet import MatViet
    from schedule.AMHD.xls.vera_jockey_amhd import VERA_JOCKEY_AMHD
    from concurrent import futures
    from datetime import datetime, timedelta
    from pytz import timezone
    from schedule.AMHD.kiotviet.kakao import Kakao
    from schedule.AMHD.xlsx.skechers_amhd import SKECHERS_AMHD
    from schedule.AMHD.xlsx.routine_amhd import Routine
    from schedule.AMHD.xlsx.pnj_amhd import PNJ_AMHD
    from schedule.AMHD.kiotviet.gabby_amhd import Gabby
    from schedule.AMHD.mmenu.jajang_amhd import JaJang
    from schedule.AMHD.acfc.typo_amhd import TYPO_AMHD
    from schedule.AMHD.acfc.banana_republic_amhd import BANANA_REPUBLIC_AMHD
    from schedule.AMHD.acfc.tommy_amhd import TOMMY_AMHD
    from schedule.AMHD.acfc.cotton_on import COTTON_ON_AMHD
    from schedule.AMHD.acfc.mango_amhd import MANGO
    from schedule.AMHD.acfc.levis_amhd import LEVIS
    from schedule.AMHD.acfc.nike_amhd import NIKE_AMHD
    from schedule.AMHD.acfc.fitflop_amhd import FITFLOP_AMHD
    from schedule.AMHD.acfc.gap_kids_amhd import GAP_KIDS_AMHD
    from schedule.AMHD.acfc.mothercare_amhd import MOTHERCARE
    from schedule.AMHD.xlsx.shooz_amhd import SHOOZ_AMHD
    from schedule.AMHD.xlsx.yves_amhd import YVES_ROCHER_AMHD
    from schedule.AMHD.xlsx.alfresco_amhd import ALFRESCO_AMHD
    from schedule.AMHD.txt.timezone_amhd import TimeZoneAMHD
    # from schedule.AMHD.ftp.txt.nkid_amhd import NKID_AMHD
    from schedule.AMHD.txt.mcdonald_amhd import McDonaldAMHD
    from schedule.AMHD.nhanh.mulgati_amhd import MULGATI_AMHD
    from schedule.AMHD.xlsx.mr_dak_amhd import MR_DAK_AMHD
    from schedule.AMHD.kiotviet.rabity_amhd import RABITY_AMHD
    from schedule.AMHD.xls.mazano_amhd import MAZANO_AMHD
    from schedule.AMHD.xlsx.innisfree_amhd import INNIS_FREE_AMHD
    from schedule.AMHD.txt.the_body_shop import TheBodyShopAMHD
    from schedule.AMHD.xls.dream_kid_amhd import DREAM_KIDS_AMHD
    from schedule.AMHD.fix_payment.charles_keith_amhd import CharlesKeithAMHD
    from schedule.AMHD.fix_payment.mlb_amhd import MLBAMHD
    from schedule.AMHD.fix_payment.pedro_amhd import PedroAMHD
    from schedule.AMHD.google_cloud.laneige_amhd import LaneigeAMHD
    from schedule.AMHD.kiotviet.wundertute_amhd import WundertuteAMHD
    from schedule.AMHD.xlsx.concung_amhd import CON_CUNG_AMHD
    from schedule.AMHD.google_cloud.yanghao_amhd import YangHaoAMHD
    from schedule.AMHD.gmail.breadtalk_amhd import BreadTalkAMHD
    from schedule.AMHD.csv.koi_amhd import KOIAMHD
    from schedule.AMHD.xls.converse_newera_amhd import ConverseNeweraAMHD
    from schedule.AMHD.csv.kohnan_amhd import KohnanAMHD
    from schedule.AMHD.xlsx.tasaki_bbq_amhd import TasakiBBQAMHD
    from schedule.AMHD.sapo.inochi_amhd import INOCHI_AMHD
    warnings.filterwarnings('ignore')
    main()
