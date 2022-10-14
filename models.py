from app import db


class User(db.Model):
    __tablename__ = 'users'
    soinik_number = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.String(255))
    name = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    password = db.Column(db.String(255))
    total_firing_count = db.Column(db.Integer)
    vertical_error_count = db.Column(db.Integer)
    horizontal_error_count = db.Column(db.Integer)

    def __init__(self, soinik_number, rank, name, unit):
        self.soinik_number = soinik_number
        self.rank = rank
        self.name = name
        self.unit = unit
        self.photo = ''
        self.password = 'admin'
        self.total_firing_count = 0
        self.vertical_error_count = 0
        self.horizontal_error_count = 0

    def __repr__(self):
        return '<User (soinik_number=%r,name=%s)>' % (self.soinik_number,self.name)


class Record(db.Model):
    __tablename__ = 'records'
    soinik_number = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, primary_key=True)
    sub_label = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    firing_range = db.Column(db.String(255))
    grouping = db.Column(db.String(255))
    error = db.Column(db.String(255))

    def __init__(self, soinik_number, date, sub_label, file_name,firing_range,grouping,error):
        self.soinik_number = soinik_number
        self.date = date
        self.sub_label = sub_label
        self.file_name = file_name
        self.firing_range = firing_range
        self.grouping = grouping
        self.error = error

    def __repr__(self):
        return "<Record (soinik_number='%s', date='%s', sub_label='%s')>" % (
            self.soinik_number,
            self.date,
            self.sub_label,
        )
