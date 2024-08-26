from application import db

class flag_influencer(db.Model):
    __tablename__ = 'flag_influencer'
    flag_inf_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    influencer_name = db.Column(db.String(80),db.ForeignKey('influencer_login.influencer_name'), nullable=False, unique=True)


class flag_sponsor(db.Model):
    __tablename__ = 'flag_sponsor'
    flag_spon_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    sponsor_name = db.Column(db.String(80), db.ForeignKey('sponsor_login.sponsor_name'), nullable=False, unique=True)