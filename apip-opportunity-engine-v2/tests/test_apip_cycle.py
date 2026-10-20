import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.apip_cycle import choose_next, TERMINAL

class APIPCycleTests(unittest.TestCase):
    def test_first_run_selects_an_opportunity(self):
        idea, history = choose_next([])
        self.assertTrue(idea['id'])
        self.assertEqual(history, [])

    def test_unfinished_selection_is_not_skipped(self):
        idea, history = choose_next([{'opportunity_id':'LOCAL_MENU_REFRESH','status':'SELECTED'}])
        self.assertEqual(idea['id'],'LOCAL_MENU_REFRESH')
        self.assertEqual(len(history),1)

    def test_terminal_result_moves_to_another_untested_idea(self):
        idea, history = choose_next([{'opportunity_id':'LOCAL_MENU_REFRESH','status':'TESTED_NO_DEMAND'}])
        self.assertNotEqual(idea['id'],'LOCAL_MENU_REFRESH')

    def test_terminal_statuses_are_explicit(self):
        self.assertIn('TESTED_DEMAND',TERMINAL)
        self.assertIn('TESTED_NO_DEMAND',TERMINAL)

if __name__=='__main__': unittest.main()
