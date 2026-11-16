"""Idempotent dev seed: the 8 supported product categories (real, from the project brief).
Ingredient/regulatory data is NOT seeded here: real data arrives in Milestones 4-5."""
import sys

from sqlalchemy import create_engine, text

from app.core.config import get_settings

CATEGORIES = [
    ("sunscreen", "Sunscreen", "sun"), ("moisturiser", "Moisturiser", "leave_on"),
    ("face-wash", "Face wash", "rinse_off"), ("serum", "Serum", "leave_on"),
    ("shampoo", "Shampoo", "rinse_off"), ("conditioner", "Conditioner", "rinse_off"),
    ("body-wash", "Body wash", "rinse_off"), ("makeup", "Makeup", "leave_on"),
]


def seed_categories(conn) -> int:  # type: ignore[no-untyped-def]
    for slug, name, usage in CATEGORIES:
        conn.execute(text("""insert into product_categories (slug, name, domain, usage_type)
                             values (:s, :n, 'cosmetics', :u) on conflict (slug) do nothing"""),
                     {"s": slug, "n": name, "u": usage})
    return len(CATEGORIES)


def main() -> None:
    engine = create_engine(get_settings().migration_database_url)
    with engine.begin() as conn:
        print(f"seeded {seed_categories(conn)} categories (idempotent)")


if __name__ == "__main__":
    sys.exit(main())
