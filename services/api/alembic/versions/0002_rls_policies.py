"""Row Level Security, grants and the auth.uid() shim.

Revision ID: 0002
Revises: 0001
"""
import os

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

APP_ROLE = os.environ.get("APP_DB_ROLE", "ll_app")  # on Supabase set to the API role

USER_OWNED = ["users", "user_preferences", "scans", "product_comparisons", "user_favourites"]
# child tables reached through scans
SCAN_CHILDREN = ["scan_images", "scan_ingredients", "scan_reports", "alternative_products"]
REFERENCE = ["product_categories", "ingredients", "ingredient_synonyms", "ingredient_functions",
             "ingredient_function_map", "ingredient_assessments", "ingredient_sources", "ingredient_regulations"]
ALL_RLS = (USER_OWNED + ["user_preference_items", "extracted_text"] + SCAN_CHILDREN + REFERENCE
           + ["products", "product_ingredients", "data_imports"])

OWN_COL = {"users": "id"}  # everything else uses user_id


def upgrade() -> None:
    # 1. auth.uid() shim. Supabase already provides it; only create when missing (local dev).
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("""
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
                     WHERE n.nspname = 'auth' AND p.proname = 'uid') THEN
        EXECUTE $f$
          CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $b$
            SELECT nullif(coalesce(nullif(current_setting('request.jwt.claim.sub', true), ''),
                   nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub'), '')::uuid
          $b$ $f$;
        COMMENT ON FUNCTION auth.uid() IS 'labellens-shim';
      END IF;
    END $$;""")

    for t in ALL_RLS:
        op.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY")

    # 2. policies
    for t in USER_OWNED:
        col = OWN_COL.get(t, "user_id")
        op.execute(f"CREATE POLICY {t}_owner ON {t} FOR ALL USING ({col} = auth.uid()) WITH CHECK ({col} = auth.uid())")
    op.execute("""CREATE POLICY user_preference_items_owner ON user_preference_items FOR ALL
      USING (EXISTS (SELECT 1 FROM user_preferences p WHERE p.id = preference_id AND p.user_id = auth.uid()))
      WITH CHECK (EXISTS (SELECT 1 FROM user_preferences p WHERE p.id = preference_id AND p.user_id = auth.uid()))""")
    for t in SCAN_CHILDREN:
        op.execute(f"""CREATE POLICY {t}_owner ON {t} FOR ALL
          USING (EXISTS (SELECT 1 FROM scans s WHERE s.id = scan_id AND s.user_id = auth.uid()))
          WITH CHECK (EXISTS (SELECT 1 FROM scans s WHERE s.id = scan_id AND s.user_id = auth.uid()))""")
    op.execute("""CREATE POLICY extracted_text_owner ON extracted_text FOR ALL
      USING (EXISTS (SELECT 1 FROM scan_images i JOIN scans s ON s.id = i.scan_id
                     WHERE i.id = scan_image_id AND s.user_id = auth.uid()))
      WITH CHECK (EXISTS (SELECT 1 FROM scan_images i JOIN scans s ON s.id = i.scan_id
                     WHERE i.id = scan_image_id AND s.user_id = auth.uid()))""")
    for t in REFERENCE:
        op.execute(f"CREATE POLICY {t}_read ON {t} FOR SELECT USING (true)")
    # catalogue: everyone reads; users may only add/edit their own *unverified community* rows
    op.execute("CREATE POLICY products_read ON products FOR SELECT USING (true)")
    op.execute("""CREATE POLICY products_insert ON products FOR INSERT
      WITH CHECK (verification_status = 'COMMUNITY_SUBMITTED' AND submitted_by = auth.uid())""")
    op.execute("""CREATE POLICY products_update ON products FOR UPDATE
      USING (submitted_by = auth.uid() AND verification_status <> 'VERIFIED')
      WITH CHECK (submitted_by = auth.uid() AND verification_status = 'COMMUNITY_SUBMITTED')""")
    op.execute("CREATE POLICY products_delete ON products FOR DELETE USING (submitted_by = auth.uid() AND verification_status <> 'VERIFIED')")
    op.execute("CREATE POLICY product_ingredients_read ON product_ingredients FOR SELECT USING (true)")
    op.execute("""CREATE POLICY product_ingredients_write ON product_ingredients FOR ALL
      USING (EXISTS (SELECT 1 FROM products p WHERE p.id = product_id AND p.submitted_by = auth.uid() AND p.verification_status <> 'VERIFIED'))
      WITH CHECK (EXISTS (SELECT 1 FROM products p WHERE p.id = product_id AND p.submitted_by = auth.uid() AND p.verification_status <> 'VERIFIED'))""")
    # data_imports: RLS on, no policy, no grant -> invisible to the API role.

    # 3. grants (only if the API role exists, e.g. not on a managed DB with another role name)
    rw = USER_OWNED + ["user_preference_items", "extracted_text"] + SCAN_CHILDREN + ["products", "product_ingredients"]
    op.execute(f"""
    DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
        GRANT USAGE ON SCHEMA public, auth TO {APP_ROLE};
        GRANT EXECUTE ON FUNCTION auth.uid() TO {APP_ROLE};
        GRANT SELECT, INSERT, UPDATE, DELETE ON {", ".join(rw)} TO {APP_ROLE};
        GRANT SELECT ON {", ".join(REFERENCE)} TO {APP_ROLE};
      END IF;
    END $$;""")


def downgrade() -> None:
    for t in ALL_RLS:
        op.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY")
    pols = {t: [f"{t}_owner"] for t in USER_OWNED + ["user_preference_items", "extracted_text"] + SCAN_CHILDREN}
    pols.update({t: [f"{t}_read"] for t in REFERENCE})
    pols["products"] = ["products_read", "products_insert", "products_update", "products_delete"]
    pols["product_ingredients"] = ["product_ingredients_read", "product_ingredients_write"]
    for t, names in pols.items():
        for n in names:
            op.execute(f"DROP POLICY IF EXISTS {n} ON {t}")
    op.execute(f"""
    DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
        REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {APP_ROLE};
      END IF;
    END $$;""")
    op.execute("""
    DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
                 WHERE n.nspname = 'auth' AND p.proname = 'uid'
                   AND obj_description(p.oid, 'pg_proc') = 'labellens-shim') THEN
        DROP FUNCTION auth.uid();
      END IF;
    END $$;""")
