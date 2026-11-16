"""Mint a LOCAL-DEV JWT signed with SUPABASE_JWT_SECRET so you can call the API with curl before
Supabase Auth is wired into the app. Never use this against production.
  python scripts/make_dev_token.py                # random new user
  python scripts/make_dev_token.py <user-uuid>    # stay the same user across calls
"""
import sys
import time
import uuid
from pathlib import Path

import jwt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # run from anywhere
from app.core.config import get_settings  # noqa: E402

s = get_settings()
sub = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())
print(jwt.encode({"sub": sub, "aud": s.jwt_audience, "role": "authenticated", "email": "dev@example.com",
                  "exp": int(time.time()) + 8 * 3600}, s.supabase_jwt_secret, algorithm="HS256"))
