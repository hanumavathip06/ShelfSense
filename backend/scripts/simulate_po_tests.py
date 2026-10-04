import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import SystemSetting
from scripts.po_generator import generate_pos

def set_setting(key, value):
    s = SystemSetting.query.get(key)
    if not s:
        s = SystemSetting(key=key, value=str(value))
        db.session.add(s)
    else:
        s.value = str(value)
    db.session.commit()

app = create_app()
with app.app_context():
    print("\\n=== RUNNING SIMULATION: T3 - Spend Limit ===")
    set_setting('DAILY_SPEND_LIMIT', '100.0') # Very low limit
    generate_pos(dry_run=True)
    
    print("\\n=== RUNNING SIMULATION: T5 - Global Killswitch ===")
    set_setting('GLOBAL_PO_KILLSWITCH', 'True')
    set_setting('DAILY_SPEND_LIMIT', '10000.0') # Restore
    generate_pos(dry_run=False) # Should force dry-run anyway
    
    set_setting('GLOBAL_PO_KILLSWITCH', 'False') # Clean up
