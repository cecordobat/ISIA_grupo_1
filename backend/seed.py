import sqlite3

c = sqlite3.connect('motor_dev.db')
c.execute("INSERT OR IGNORE INTO tabla_ciiu VALUES ('6201', 'Actividades de desarrollo de sistemas informáticos', 0.60, '2020-01-01');")
c.execute("INSERT OR IGNORE INTO tabla_ciiu VALUES ('6910', 'Actividades jurídicas', 0.60, '2020-01-01');")
c.execute("INSERT OR IGNORE INTO tabla_ciiu VALUES ('6920', 'Actividades de contabilidad y auditoría', 0.60, '2020-01-01');")
c.execute("INSERT OR IGNORE INTO tabla_ciiu VALUES ('7020', 'Actividades de consultoría de gestión', 0.60, '2020-01-01');")
c.commit()
print('CIIU Seeded')
