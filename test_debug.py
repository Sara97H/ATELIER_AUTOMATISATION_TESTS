#!/usr/bin/env python3
import os
os.environ['IPSTACK_API_KEY'] = '7ead199380666b8913f0ecf608ff9996'

from tester.runner import TestRunner
import json

runner = TestRunner()
report = runner.run()

print('\n[DETAILED TEST RESULTS]\n')
for test in report['tests']:
    status_icon = '✅' if test['status'] == 'PASS' else '❌'
    print(f"{status_icon} {test['name']}")
    if test['details']:
        print(f"   ℹ️ {test['details']}")
    print(f"   ⏱️ {test['latency_ms']}ms\n")

print('[FULL REPORT]')
print(json.dumps(report, indent=2, ensure_ascii=False))
