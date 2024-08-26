from application import db

class influencer_login(db.Model):
    __tablename__ = 'influencer_login'
    influencer_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    influencer_name = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    Instagram = db.Column(db.String(128))
    twitter = db.Column(db.String(128))
    youtube = db.Column(db.String(128))
    profile_pic = db.Column(db.BLOB)


class influencer_requests(db.Model):
    __tablename__ = 'influencer_requests'
    request_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer_login.influencer_id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('Advertisements.ad_id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaigns.campaign_id'), nullable=False)


class influencer_accepts(db.Model):
    __tablename__ = 'influencer_accepts'
    acc_id = db.Column(db.Integer, primary_key=True, nullable=False, unique = True)
    influencer_name = db.Column(db.String(80), db.ForeignKey('influencer_login.influencer_name'), nullable=False)
    ad_name = db.Column(db.String(80), db.ForeignKey('Advertisements.ad_name'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaigns.campaign_id') , nullable=False)


class completed(db.Model):
    __tablename__ = 'completed'
    comp_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    influencer_name = db.Column(db.String(80), db.ForeignKey('influencer_login.influencer_name'), nullable=False)
    ad_name = db.Column(db.String(80), db.ForeignKey('Advertisements.ad_name'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaigns.campaign_id'), nullable=False)
