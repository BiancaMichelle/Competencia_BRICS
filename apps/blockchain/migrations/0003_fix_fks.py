"""Fix foreign keys: ensure blockchain tables reference users_paciente.

This migration rebuilds affected tables in SQLite by creating a new table with
the correct foreign key, copying data, dropping the old table and renaming the
new table. It targets the tables that were incorrectly referencing
blockchain_paciente or its backup.

NOTE: This is a development migration. Backup your DB before running in
production.
"""

from django.db import migrations


def noop(apps, schema_editor):
    # placeholder for operations that just run SQL via RunSQL below
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('blockchain', '0002_remove_unique_together'),
        ('users', '0001_initial'),
    ]

    operations = [
        # Rebuild turno
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_turno (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_hora datetime NOT NULL, motivo TEXT NOT NULL, estado varchar(20) NOT NULL, observaciones TEXT, fecha_creacion datetime NOT NULL, paciente_id INTEGER NOT NULL, profesional_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE, FOREIGN KEY(profesional_id) REFERENCES users_profesional(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_turno (id, fecha_hora, motivo, estado, observaciones, fecha_creacion, paciente_id, profesional_id) SELECT id, fecha_hora, motivo, estado, observaciones, fecha_creacion, paciente_id, profesional_id FROM blockchain_turno;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_turno;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_turno RENAME TO blockchain_turno;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild tratamiento
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_tratamiento (id INTEGER PRIMARY KEY AUTOINCREMENT, descripcion TEXT NOT NULL, dosis varchar(100), frecuencia varchar(100), fecha_inicio date NOT NULL, fecha_fin date, observaciones TEXT, activo bool NOT NULL, medicamento_id INTEGER, paciente_id INTEGER NOT NULL, profesional_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE, FOREIGN KEY(profesional_id) REFERENCES users_profesional(id) ON DELETE CASCADE, FOREIGN KEY(medicamento_id) REFERENCES blockchain_medicamento(id) ON DELETE SET NULL);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_tratamiento (id, descripcion, dosis, frecuencia, fecha_inicio, fecha_fin, observaciones, activo, medicamento_id, paciente_id, profesional_id) SELECT id, descripcion, dosis, frecuencia, fecha_inicio, fecha_fin, observaciones, activo, medicamento_id, paciente_id, profesional_id FROM blockchain_tratamiento;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_tratamiento;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_tratamiento RENAME TO blockchain_tratamiento;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild pruebalaboratorio
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_pruebalaboratorio (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_prueba varchar(200) NOT NULL, fecha_realizacion date NOT NULL, resultados TEXT NOT NULL, valores_referencia TEXT, observaciones TEXT, archivo_resultado varchar(100), paciente_id INTEGER NOT NULL, profesional_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE, FOREIGN KEY(profesional_id) REFERENCES users_profesional(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_pruebalaboratorio (id, nombre_prueba, fecha_realizacion, resultados, valores_referencia, observaciones, archivo_resultado, paciente_id, profesional_id) SELECT id, nombre_prueba, fecha_realizacion, resultados, valores_referencia, observaciones, archivo_resultado, paciente_id, profesional_id FROM blockchain_pruebalaboratorio;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_pruebalaboratorio;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_pruebalaboratorio RENAME TO blockchain_pruebalaboratorio;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild condicionmedica
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_condicionmedica (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo varchar(200) NOT NULL, descripcion TEXT, fecha_diagnostico date NOT NULL, estado varchar(20) NOT NULL, paciente_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_condicionmedica (id, codigo, descripcion, fecha_diagnostico, estado, paciente_id) SELECT id, codigo, descripcion, fecha_diagnostico, estado, paciente_id FROM blockchain_condicionmedica;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_condicionmedica;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_condicionmedica RENAME TO blockchain_condicionmedica;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild cirugia
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_cirugia (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_cirugia varchar(200) NOT NULL, fecha_cirugia date NOT NULL, descripcion TEXT NOT NULL, complicaciones TEXT, estado varchar(20) NOT NULL, paciente_id INTEGER NOT NULL, profesional_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE, FOREIGN KEY(profesional_id) REFERENCES users_profesional(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_cirugia (id, nombre_cirugia, fecha_cirugia, descripcion, complicaciones, estado, paciente_id, profesional_id) SELECT id, nombre_cirugia, fecha_cirugia, descripcion, complicaciones, estado, paciente_id, profesional_id FROM blockchain_cirugia;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_cirugia;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_cirugia RENAME TO blockchain_cirugia;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild antecedente
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_antecedente (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo varchar(20) NOT NULL, descripcion TEXT NOT NULL, fecha_evento date, observaciones TEXT, paciente_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_antecedente (id, tipo, descripcion, fecha_evento, observaciones, paciente_id) SELECT id, tipo, descripcion, fecha_evento, observaciones, paciente_id FROM blockchain_antecedente;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_antecedente;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_antecedente RENAME TO blockchain_antecedente;", reverse_sql=migrations.RunSQL.noop),

        # Rebuild alergia
        migrations.RunSQL(sql="CREATE TABLE IF NOT EXISTS new_blockchain_alergia (id INTEGER PRIMARY KEY AUTOINCREMENT, sustancia varchar(100) NOT NULL, descripcion TEXT, severidad varchar(20) NOT NULL, fecha_diagnostico date NOT NULL, paciente_id INTEGER NOT NULL, FOREIGN KEY(paciente_id) REFERENCES users_paciente(id) ON DELETE CASCADE);", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="INSERT INTO new_blockchain_alergia (id, sustancia, descripcion, severidad, fecha_diagnostico, paciente_id) SELECT id, sustancia, descripcion, severidad, fecha_diagnostico, paciente_id FROM blockchain_alergia;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS blockchain_alergia;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="ALTER TABLE new_blockchain_alergia RENAME TO blockchain_alergia;", reverse_sql=migrations.RunSQL.noop),

        migrations.RunPython(noop),
    ]
