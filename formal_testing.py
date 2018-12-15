from preliminary_sizing import *
import unittest


class FormalTesting(unittest.TestCase):

    def test_mission(self):
        taxi = Phase("taxi", 3, 15, 30, 0, 3)
        takeoff = Phase("takeoff", 13.4, 15, 10, 0, 13.4)
        land = Phase("land", 0, 5, 30, -1, -13.4)
        land_duplicate = Phase("land", 0, 5, 30, -1, -13.4)

        mission1 = Mission(12.5)
        mission1.add_all_phases([taxi, takeoff, land, land_duplicate])
        self.assertEqual(len(mission1.unique_phases), 3)
        self.assertEqual(len(mission1.all_phases), 4)

        mission2 = Mission(13.5)
        mission2.add_all_phases([taxi, taxi, taxi])
        self.assertEqual(len(mission2.unique_phases), 1)
        self.assertEqual(len(mission2.all_phases), 3)

    def test_historical_trends(self):
        bowers_fly_baby_1b = SimilarPlane(441, 295)
        bushby_mm_1_85 = SimilarPlane(397, 261)
        cassutt_ii = SimilarPlane(363, 196)
        monnett_sonera_i = SimilarPlane(340, 200)
        mooney_mite = SimilarPlane(354, 229)
        pazmany_pl_2a = SimilarPlane(642, 397)
        pazmany_pl_4a = SimilarPlane(386, 262)
        quickie_q2 = SimilarPlane(454, 215)
        rutan_variviggen = SimilarPlane(771, 431)
        rutan_varieze = SimilarPlane(476, 254)
        rutan_longeze = SimilarPlane(601, 340)
        zenith_ch_200 = SimilarPlane(680, 400)
        pik_21 = SimilarPlane(320, 199)
        croses_eac_3 = SimilarPlane(260, 141)
        gatard_ag02 = SimilarPlane(280, 170)
        jodel_d92 = SimilarPlane(320, 191)
        jurca_mj_5ea2 = SimilarPlane(680, 430)
        piel_emeraude_cp320 = SimilarPlane(650, 410)
        piel_super_diamant = SimilarPlane(850, 520)
        pottier_p50 = SimilarPlane(400, 270)
        stelio_frati_falco_f8l = SimilarPlane(820, 550)
        nasa_gl_10 = SimilarPlane(26, 21)
        roskam_home_built = HistoricalTrend()
        roskam_home_built.add_similar_planes([bowers_fly_baby_1b, bushby_mm_1_85, cassutt_ii, monnett_sonera_i, mooney_mite,
                                         pazmany_pl_2a, pazmany_pl_4a, quickie_q2, rutan_variviggen, rutan_varieze,
                                         rutan_longeze, zenith_ch_200, pik_21, croses_eac_3, gatard_ag02, jodel_d92,
                                         jurca_mj_5ea2, piel_emeraude_cp320, piel_super_diamant, pottier_p50,
                                         stelio_frati_falco_f8l, nasa_gl_10])
        droan_empty_mass_guess = roskam_home_built.calculate_empty_mass_required(12.5)
        print(droan_empty_mass_guess)
        self.assertEqual(round(roskam_home_built.empty_mass_required), 10)


if __name__ == '__main__':
    unittest.main()
