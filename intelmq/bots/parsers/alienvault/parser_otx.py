# -*- coding: utf-8 -*-
"""
Events are gathered based on user subscriptions in AlienVault OTX
The data structure is described in detail here:
https://github.com/AlienVault-Labs/OTX-Python-SDK/blob/master/
howto_use_python_otx_api.ipynb
"""
from __future__ import unicode_literals

import json
import sys

from intelmq.lib import utils
from intelmq.lib.bot import Bot
from intelmq.lib.message import Event

HASHES = {
    'FileHash-SHA256': '$5$',
    'FileHash-SHA1': '$sha1$',
    'FileHash-MD5': '$1$'
}


class AlienVaultOTXParserBot(Bot):

    def process(self):
        report = self.receive_message()
        if report is None or not report.contains("raw"):
            self.acknowledge_message()
            return

        raw_report = utils.base64_decode(report.value("raw"))

        for pulse in json.loads(raw_report):
            additional = json.dumps({"author": pulse['author_name'],
                                     "pulse": pulse['name']},
                                    sort_keys=True)
            for indicator in pulse["indicators"]:
                event = Event(report)
                # hashes
                if indicator["type"] in HASHES.keys():
                    event.add('malware.hash', HASHES[indicator["type"]] +
                              indicator["indicator"])
                # fqdn
                if indicator["type"] in ['hostname', 'domain']:
                    event.add('source.fqdn',
                              indicator["indicator"], sanitize=True)
                # IP addresses
                elif indicator["type"] in ['IPv4', 'IPv6']:
                    event.add('source.ip',
                              indicator["indicator"], sanitize=True)
                # emails
                elif indicator["type"] == 'email':
                    event.add('source.account',
                              indicator["indicator"], sanitize=True)
                # URLs
                elif indicator["type"] in ['URL', 'URI']:
                    event.add('source.url',
                              indicator["indicator"], sanitize=True)
                # CIDR
                elif indicator["type"] in ['CIDR']:
                    event.add('source.network',
                              indicator["indicator"], sanitize=True)
                # FilePath, Mutex, CVE - TODO: process these IoCs as well
                else:
                    continue

                event.add('comment', pulse['description'])
                event.add('extra', additional, sanitize=True)
                event.add('classification.type', 'blacklist', sanitize=True)
                event.add('time.source', indicator["created"][:-4] + "+00:00",
                          sanitize=True)
                event.add("raw", json.dumps(indicator, sort_keys=True),
                          sanitize=True)
                self.send_message(event)
        self.acknowledge_message()

if __name__ == "__main__":
    bot = AlienVaultOTXParserBot(sys.argv[1])
    bot.start()
