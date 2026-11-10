"""Negative controls: each deliberately broken implementation must fail its gate."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import json

ROOT = Path(__file__).resolve().parent
mutations = [
 ('hide_renderer_loss', 'runtime.py', "if r.poll() is not None and not renderer_lost:", "if False:", 'test_01_renderer_loss_and_sensor_uncertainty'),
 ('disable_watchdog_timeout', 'runtime.py', "if gap > 0.6 or p.poll() is not None:", "if False:", 'test_02_primary_wedge_independent_watchdog'),
 ('refresh_duplicate', 'state.py', "if seq <= self.seq:\n", "if seq <= self.seq:\n            self.accepted_at = self.clock()\n", 'test_03_replays_cannot_reset_freshness'),
]
results=[]
for name, file, old, new, test in mutations:
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        for src in ROOT.glob('*.py'):
            shutil.copy(src,root/src.name)
        target=root/file
        code=target.read_text()
        assert code.count(old)==1
        target.write_text(code.replace(old,new))
        r=subprocess.run([sys.executable,'-m','unittest','-v','test_contract.Contract.'+test],cwd=root,capture_output=True,text=True,timeout=30)
        (ROOT/'evidence'/('negative-'+name+'.txt')).write_text(r.stdout+r.stderr+'\nEXIT_CODE='+str(r.returncode)+'\n')
        results.append(dict(mutation=name,exit_code=r.returncode,rejected=r.returncode!=0))
(ROOT/'evidence'/'negative-controls.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
if not all(x['rejected'] for x in results):
    sys.exit(1)
