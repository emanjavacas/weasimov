from app import db, models

admin = models.User(username='admin', password='admin')
db.session.add(admin)
db.session.flush()
doc = models.Doc(user_id=admin.get_id())
db.session.add(doc)
db.session.commit()
