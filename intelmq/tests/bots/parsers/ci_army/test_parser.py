# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import unittest

import intelmq.lib.test as test
from intelmq.bots.parsers.ci_army.parser import CIArmyParserBot


class TestCIArmyParserBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for CIArmyParserBot.
    """

    @classmethod
    def set_bot(self):
        self.bot_reference = CIArmyParserBot
        self.default_input_message = json.dumps({'__type': 'Report'})

if __name__ == '__main__':
    unittest.main()
