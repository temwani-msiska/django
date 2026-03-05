from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_fix_uuid_foreign_keys"),
        ("token_blacklist", "0013_alter_blacklistedtoken_options_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DELETE FROM token_blacklist_blacklistedtoken;",
                "DELETE FROM token_blacklist_outstandingtoken;",
                """
                DO $$
                DECLARE c record;
                BEGIN
                  FOR c IN
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'token_blacklist_outstandingtoken'::regclass
                      AND conkey = ARRAY[
                        (SELECT attnum FROM pg_attribute
                         WHERE attrelid = 'token_blacklist_outstandingtoken'::regclass
                           AND attname = 'user_id')
                      ]
                  LOOP
                    EXECUTE format('ALTER TABLE token_blacklist_outstandingtoken DROP CONSTRAINT %I', c.conname);
                  END LOOP;
                END $$;
                """,
                "ALTER TABLE token_blacklist_outstandingtoken ALTER COLUMN user_id TYPE uuid USING NULL::uuid;",
                "ALTER TABLE token_blacklist_outstandingtoken ADD CONSTRAINT token_blacklist_outstandingtoken_user_id_fk FOREIGN KEY (user_id) REFERENCES accounts_parentuser(id) DEFERRABLE INITIALLY DEFERRED;",
                "CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx ON token_blacklist_outstandingtoken(user_id);",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
