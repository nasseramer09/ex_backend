from app import db

user_task_association = db.Table('user_task_association',
                                 db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                 db.Column('task_id', db.Integer, db.ForeignKey('tasks.id')))
class User(db.Model):
    __table__= 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname=db.Column(db.String(250), unique=False, nullable=False)
    sirtname=db.Column(db.String(250), unique=False, nullable=False)
    username = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200), unique=True, nullable = False)
    password = db.Column(db.String(200), nullable = False)
    role = db.Column(db.Enum('admin', 'staff', name='user_roles'), nullable=False)

    tasks = db.relationship(
        'Task',
        secondary = user_task_association,
        back_populates = 'users'
    )

    def _repr__(self):
        return f'<User {self.username}>'