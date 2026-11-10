"""Run with system Python; avoids the Windows temporary venv launcher."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
for directory in (ROOT.parents[1] / 'work/venv/Lib/site-packages',
                  ROOT / '.venv/Lib/site-packages', ROOT / '.vision-deps'):
    if directory.is_dir():
        sys.path.insert(0, str(directory))
sys.path.insert(0, str(ROOT / 'backend'))

if __name__ == '__main__':
    try:
        import uvicorn
    except ImportError:
        raise SystemExit('Backend dependencies missing. Run: python -m pip install -r backend/requirements.txt')
    os.environ.setdefault('CAMPUS_TRANSIT_SEED', str(ROOT / 'data/transit.demo.json'))
    port = int(os.environ.get('CAMPUS_PORT', '8000'))
    print(f'Campus backend: http://127.0.0.1:{port}/docs', flush=True)
    uvicorn.run('app.main:app', host='127.0.0.1', port=port)
