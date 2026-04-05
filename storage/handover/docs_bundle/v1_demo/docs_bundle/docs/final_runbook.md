# Final runbook

1. `python main.py verify-delivery --profile-id v1_demo`
2. `python main.py build-release-manifest --profile-id v1_demo`
3. `python main.py build-bom --profile-id v1_demo`
4. `python main.py build-demo-kit --profile-id v1_demo --output-dir tmp/demo_kit`
5. `python main.py build-handover-kit --profile-id v1_demo --output-dir tmp/handover_kit`
6. Optional: `python main.py package-final-release --profile-id v1_demo --output-file tmp/final.zip`
