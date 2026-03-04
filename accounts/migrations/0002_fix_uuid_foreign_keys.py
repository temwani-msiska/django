from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DELETE FROM accounts_childprofile;",
                """
                DO $$
                DECLARE c record;
                BEGIN
                  FOR c IN
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'accounts_childprofile'::regclass
                      AND conkey = ARRAY[
                        (SELECT attnum FROM pg_attribute
                         WHERE attrelid = 'accounts_childprofile'::regclass
                           AND attname = 'parent_id')
                      ]
                  LOOP
                    EXECUTE format('ALTER TABLE accounts_childprofile DROP CONSTRAINT %I', c.conname);
                  END LOOP;
                END $$;
                """,
                "ALTER TABLE accounts_childprofile ALTER COLUMN parent_id TYPE uuid USING NULL::uuid;",
                "ALTER TABLE accounts_childprofile ADD CONSTRAINT accounts_childprofile_parent_id_fk FOREIGN KEY (parent_id) REFERENCES accounts_parentuser(id) DEFERRABLE INITIALLY DEFERRED;",
                "CREATE INDEX IF NOT EXISTS accounts_childprofile_parent_id_idx ON accounts_childprofile(parent_id);",
                """
                DO $$
                DECLARE c record;
                BEGIN
                  FOR c IN
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'django_admin_log'::regclass
                      AND conkey = ARRAY[
                        (SELECT attnum FROM pg_attribute
                         WHERE attrelid = 'django_admin_log'::regclass
                           AND attname = 'user_id')
                      ]
                  LOOP
                    EXECUTE format('ALTER TABLE django_admin_log DROP CONSTRAINT %I', c.conname);
                  END LOOP;
                END $$;
                """,
                "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE uuid USING NULL::uuid;",
                "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fk FOREIGN KEY (user_id) REFERENCES accounts_parentuser(id) DEFERRABLE INITIALLY DEFERRED;",
                "CREATE INDEX IF NOT EXISTS django_admin_log_user_id_idx ON django_admin_log(user_id);",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
