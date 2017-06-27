from app import db, models

admin = models.User(username='admin', password='admin')
db.session.add(admin)
db.session.commit()
