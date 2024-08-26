from application import db
from sqlalchemy.orm import relationship
from sqlalchemy import LargeBinary

class sponsor_login(db.Model):
    __tablename__ = 'sponsor_login'
    sponsor_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    sponsor_name = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(80), nullable=False)
    Industry = db.Column(db.String(80), nullable=False)
    Campaigns = relationship('Campaigns', backref='sponsor', lazy=True)
    profile_pic = db.Column(db.LargeBinary)


class Campaigns(db.Model):
    __tablename__ = 'Campaigns'
    campaign_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    campaign_name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(200))
    start_date = db.Column(db.DATE, nullable=False)
    end_date = db.Column(db.DATE, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)
    goals = db.Column(db.String(200))
    sponsor_name = db.Column(db.String(80), db.ForeignKey('sponsor_login.sponsor_name'), nullable=False)


class Advertisements(db.Model):
    __tablename__ = 'Advertisements'
    ad_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaigns.campaign_id'), nullable=False)
    ad_name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    requirements = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    images = db.Column(db.LargeBinary)



class sponsor_requests(db.Model):
    __tablename__ = 'sponsor_requests'
    req_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('Advertisements.ad_id'), nullable=False)
    influencer_ids = db.Column(db.String(200), nullable=False)


class sponsor_accepts(db.Model):
    __tablename__ = 'sponsor_accepts'
    acc_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    ad_name = db.Column(db.String(80), db.ForeignKey('Advertisements.ad_name'), nullable=False)
    campaign_name = db.Column(db.String(80), db.ForeignKey('Campaigns.campaign_name'), nullable=False)
    influencer_name = db.Column(db.String(80), db.ForeignKey('influencer_login.influencer_name'), nullable=False)