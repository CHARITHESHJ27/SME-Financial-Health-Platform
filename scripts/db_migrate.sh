#!/bin/bash
# scripts/db_migrate.sh
# Run after containers are up: ./scripts/db_migrate.sh
set -e

echo "=== Finexri DB Migration ==="

cd "$(dirname "$0")/../backend"
source venv/bin/activate 2>/dev/null || true

python - <<'EOF'
import sys
sys.path.insert(0, '.')
from app.database import engine
from app.models.schemas import Base
from sqlalchemy import text

print("Creating tables...")
Base.metadata.create_all(bind=engine)

# Performance indexes
with engine.connect() as conn:
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_org        ON users(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_companies_org    ON companies(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_companies_name   ON companies(name);",
        "CREATE INDEX IF NOT EXISTS idx_assessments_co   ON financial_assessments(company_id);",
        "CREATE INDEX IF NOT EXISTS idx_assessments_date ON financial_assessments(assessment_date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_orgs_slug        ON organizations(slug);",
    ]
    for idx in indexes:
        try:
            conn.execute(text(idx))
            print(f"  ✓ {idx.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"  - skipped: {e}")
    conn.commit()

print("Migration complete.")
EOF
