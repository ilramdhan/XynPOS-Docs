#!/usr/bin/env python3
"""
Generate a new golang-migrate migration file pair.
Usage: python scripts/gen_migration.py <description> [migrations-dir]
Example: python scripts/gen_migration.py add_batch_tracking_to_inventory
"""
import sys, os
from pathlib import Path
from datetime import datetime

def gen_migration(description: str, migrations_dir: str = "./migrations"):
    # Find next version number
    mdir = Path(migrations_dir)
    mdir.mkdir(parents=True, exist_ok=True)
    
    existing = sorted([f.name for f in mdir.glob("*.up.sql")])
    if existing:
        last_num = int(existing[-1].split('_')[0])
        next_num = last_num + 1
    else:
        next_num = 1
    
    version = str(next_num).zfill(6)
    safe_desc = description.lower().replace(' ', '_').replace('-', '_')
    
    up_file = mdir / f"{version}_{safe_desc}.up.sql"
    down_file = mdir / f"{version}_{safe_desc}.down.sql"
    
    up_content = f"""-- Migration: {version}_{safe_desc}
-- Created: {datetime.now().isoformat()}
-- Description: {description.replace('_', ' ')}

-- TODO: Write your UP migration here
-- Conventions:
--   - Use gen_random_uuid() for UUID defaults
--   - Use TIMESTAMPTZ for all datetime columns
--   - Add indexes for all FK columns
--   - Add NOT NULL where appropriate

BEGIN;

-- Example:
-- CREATE TABLE IF NOT EXISTS my_table (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
--     updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
--     deleted_at TIMESTAMPTZ
-- );
-- CREATE INDEX idx_my_table_name ON my_table(name);

COMMIT;
"""
    
    down_content = f"""-- Migration: {version}_{safe_desc} (DOWN)
-- Reverses: {version}_{safe_desc}.up.sql

BEGIN;

-- TODO: Write your DOWN migration here (must fully reverse the UP)
-- Example: DROP TABLE IF EXISTS my_table;

COMMIT;
"""
    
    up_file.write_text(up_content)
    down_file.write_text(down_content)
    
    print(f"✅ Created migration pair:")
    print(f"   UP:   {up_file}")
    print(f"   DOWN: {down_file}")
    print(f"\nRemember:")
    print(f"  - Test DOWN migration rolls back correctly")
    print(f"  - Run against ALL tenant schemas (not just one)")
    print(f"  - Never modify migrations already deployed to production")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <description> [migrations-dir]")
        sys.exit(1)
    gen_migration(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "./migrations")
