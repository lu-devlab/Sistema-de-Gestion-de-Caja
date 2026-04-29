from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0003_remove_notificacion_id_notificacion_id_notificacion_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM pg_type
                    WHERE typname = 'tipo_notificacion_enum'
                ) THEN
                    ALTER TYPE tipo_notificacion_enum ADD VALUE IF NOT EXISTS 'APERTURA_REGISTRADA';
                END IF;
            END
            $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
