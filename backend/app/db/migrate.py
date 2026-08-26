"""Alembic-style SQL migration stubs (PHP-19).

Apply with: python -m app.db.migrate upgrade
Rollback drops tables via downgrade.
"""

from __future__ import annotations

import argparse

from app.db.models import Base
from app.db.session import init_db, make_engine


def upgrade(url: str | None = None) -> None:
    engine = make_engine(url)
    init_db(engine)


def downgrade(url: str | None = None) -> None:
    engine = make_engine(url)
    Base.metadata.drop_all(engine)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    parser.add_argument("--url", default=None)
    args = parser.parse_args()
    if args.action == "upgrade":
        upgrade(args.url)
        print("upgrade ok")
    else:
        downgrade(args.url)
        print("downgrade ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
