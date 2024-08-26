from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with, reqparse
from werkzeug.security import generate_password_hash
from datetime import date

from application import db
from influencers.models import influencer_login, influencer_requests, influencer_accepts, completed
from sponsors.models import sponsor_login, sponsor_accepts, sponsor_requests, Advertisements, Campaigns
from admin.models import flag_influencer, flag_sponsor

from api.validation import BusinessValidationError, NotFoundError

api_app = Blueprint('api_app', __name__)
api = Api(api_app)


create_influencer_parser = reqparse.RequestParser()
create_influencer_parser.add_argument('influencer_name', help="Full name is required.", required=True)
create_influencer_parser.add_argument('email', help="Email is required.", required=True)
create_influencer_parser.add_argument('password', help="Password is required.", required=True)

update_influencer_parser = reqparse.RequestParser()
update_influencer_parser.add_argument('about_me')

create_sponsor_parser = reqparse.RequestParser()
create_sponsor_parser.add_argument('sponsor_name', help="Full name is required.", required=True)
create_sponsor_parser.add_argument('email', help="Email is required.", required=True)
create_sponsor_parser.add_argument('password', help="Password is required.", required=True)

update_sponsor_parser = reqparse.RequestParser()
update_sponsor_parser.add_argument('about_me')

create_campaign_parser = reqparse.RequestParser()
create_campaign_parser.add_argument('campaign_name', help="campaign name is required.", required=True)
create_campaign_parser.add_argument('description', help="campaign description is required.", required=True)
create_campaign_parser.add_argument('start_date', type=int, help="start date is required.", required=True)
create_campaign_parser.add_argument('end_date', type=int, help="end date is required.", required=True)
create_campaign_parser.add_argument('budget', type=int, help="budget is required.", required=True)


update_campaign_parser = reqparse.RequestParser()
update_campaign_parser.add_argument('campaign_name')
update_campaign_parser.add_argument('description')
update_campaign_parser.add_argument('start_date')
update_campaign_parser.add_argument('end_date')
update_campaign_parser.add_argument('budget')

create_Advertisement_parser = reqparse.RequestParser()
create_Advertisement_parser.add_argument('ad_name', help="ad name is required.", required=True)
create_Advertisement_parser.add_argument('amount', help="amount is required.", required=True)
create_Advertisement_parser.add_argument('requirements', type=int, help="requirements is required.", required=True)

update_Advertisement_parser = reqparse.RequestParser()
update_Advertisement_parser.add_argument('ad_name')
update_Advertisement_parser.add_argument('amount')
update_Advertisement_parser.add_argument('requirements')


influencer_resource_fields = {
    'influencer_id': fields.Integer,
    'influencer_name': fields.String,
    'password': fields.String,
    'email': fields.String,
    'category': fields.String,
    'Instagram': fields.String,
    'twitter': fields.String,
    'youtube': fields.String,
    'profile_pic': fields.String,
}

class InfluencerAPI(Resource):
    @marshal_with(influencer_resource_fields)
    def get(self, influencer_id=None):
        print("hello")
        if influencer_id:
            influencer = influencer_login.query.filter_by(influencer_id=influencer_id).first()
            print(f"Fetching influencer by ID {influencer_id}: {influencer}")
            if not influencer:
                raise NotFoundError(status_code=404, error_code="USER_NOT_FOUND", error_message="Influencer not found")
            return influencer, 200
        else:
            influencers = influencer_login.query.all()
            print(f"Fetching all influencers: {influencers}")
            if not influencers:
                raise NotFoundError(status_code=404, error_code="NO_INFLUENCERS", error_message="No influencers found")
            return influencers, 200

    @marshal_with(influencer_resource_fields)
    def post(self):
        data = request.get_json()
        influencer_name = data.get("influencer_name")
        email = data.get("email")
        password = generate_password_hash(data.get("password"))
        category = data.get("category")
        Instagram = data.get("Instagram")
        twitter = data.get("twitter")
        youtube = data.get("youtube")
        profile_pic = data.get("profile_pic")

        if influencer_login.query.filter_by(email=email).first():
            raise BusinessValidationError(status_code=409, error_code="EMAIL_EXISTS", error_message="Email already exists")

        new_influencer = influencer_login(
            influencer_name=influencer_name,
            email=email,
            password=password,
            category=category,
            Instagram=Instagram,
            twitter=twitter,
            youtube=youtube,
            profile_pic=profile_pic
        )
        db.session.add(new_influencer)
        db.session.commit()
        return new_influencer, 201

    @marshal_with(influencer_resource_fields)
    def put(self, influencer_id):
        data = request.get_json()
        influencer = influencer_login.query.filter_by(influencer_id=influencer_id).first()
        if not influencer:
            raise NotFoundError(status_code=404, error_code="USER_NOT_FOUND", error_message="Influencer not found")

        influencer.influencer_name = data.get("influencer_name", influencer.influencer_name)
        influencer.email = data.get("email", influencer.email)
        influencer.category = data.get("category", influencer.category)
        influencer.Instagram = data.get("Instagram", influencer.Instagram)
        influencer.twitter = data.get("twitter", influencer.twitter)
        influencer.youtube = data.get("youtube", influencer.youtube)
        influencer.profile_pic = data.get("profile_pic", influencer.profile_pic)
        db.session.commit()
        return influencer, 200

    def delete(self, influencer_id):
        influencer = influencer_login.query.filter_by(influencer_id=influencer_id).first()
        if not influencer:
            raise NotFoundError(status_code=404, error_code="USER_NOT_FOUND", error_message="Influencer not found")

        db.session.delete(influencer)
        db.session.commit()
        return {"message": "Influencer deleted successfully"}, 200


sponsor_resource_fields = {
    'sponsor_id': fields.Integer,
    'sponsor_name': fields.String,
    'email': fields.String,
    'company_name': fields.String,
    'Industry': fields.String,
}

class SponsorAPI(Resource):
    @marshal_with(sponsor_resource_fields)
    def get(self, sponsor_id=None):
        if sponsor_id:
            sponsor = sponsor_login.query.filter_by(sponsor_id=sponsor_id).first()
            if not sponsor:
                raise NotFoundError(status_code=404, error_code="SPONSOR_NOT_FOUND", error_message="Sponsor not found")
            return sponsor, 200
        else:
            sponsors = sponsor_login.query.all()
            if not sponsors:
                raise NotFoundError(status_code=404, error_code="NO_SPONSORS", error_message="No sponsors found")
            return sponsors, 200

    @marshal_with(sponsor_resource_fields)
    def post(self):
        data = request.get_json()
        sponsor_name = data.get("sponsor_name")
        email = data.get("email")
        password = generate_password_hash(data.get("password"))
        company_name = data.get("company_name")
        Industry = data.get("Industry")

        if sponsor_login.query.filter_by(email=email).first():
            raise BusinessValidationError(status_code=409, error_code="EMAIL_EXISTS", error_message="Email already exists")

        new_sponsor = sponsor_login(sponsor_name=sponsor_name, email=email, password=password, company_name=company_name, Industry=Industry)
        db.session.add(new_sponsor)
        db.session.commit()
        return new_sponsor, 201

    @marshal_with(sponsor_resource_fields)
    def put(self, sponsor_id):
        data = request.get_json()
        sponsor = sponsor_login.query.filter_by(sponsor_id=sponsor_id).first()
        if not sponsor:
            raise NotFoundError(status_code=404, error_code="SPONSOR_NOT_FOUND", error_message="Sponsor not found")

        sponsor.sponsor_name = data.get("sponsor_name", sponsor.sponsor_name)
        sponsor.email = data.get("email", sponsor.email)
        sponsor.company_name = data.get("company_name", sponsor.company_name)
        sponsor.Industry = data.get("Industry", sponsor.Industry)
        db.session.commit()
        return sponsor, 200

    def delete(self, sponsor_id):
        sponsor = sponsor_login.query.filter_by(sponsor_id=sponsor_id).first()
        if not sponsor:
            raise NotFoundError(status_code=404, error_code="SPONSOR_NOT_FOUND", error_message="Sponsor not found")

        db.session.delete(sponsor)
        db.session.commit()
        return {"message": "Sponsor deleted successfully"}, 200


campaign_resource_fields = {
    'campaign_id': fields.Integer,
    'campaign_name': fields.String,
    'description': fields.String,
    'start_date': fields.String,
    'end_date': fields.String,
    'budget': fields.Integer,
    'visibility': fields.String,
    'goals': fields.String,
    'sponsor_name': fields.String,
}

# Resource Class
class CampaignAPI(Resource):
    @marshal_with(campaign_resource_fields)
    def get(self, campaign_id=None):
        if campaign_id:
            campaign = Campaigns.query.filter_by(campaign_id=campaign_id).first()
            if not campaign:
                raise NotFoundError(status_code=404, error_code="CAMPAIGN_NOT_FOUND", error_message="Campaign not found")
            return campaign, 200
        else:
            campaigns = Campaigns.query.all()
            if not campaigns:
                raise NotFoundError(status_code=404, error_code="NO_CAMPAIGNS", error_message="No campaigns found")
            return campaigns, 200

    @marshal_with(campaign_resource_fields)
    def post(self):
        data = request.get_json()
        campaign_name = data.get("campaign_name")
        description = data.get("description")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        budget = data.get("budget")
        visibility = data.get("visibility")
        goals = data.get("goals")
        sponsor_name = data.get("sponsor_name")

        if not campaign_name or not description or not start_date or not end_date or not budget:
            raise BusinessValidationError(status_code=400, error_code="MISSING_FIELDS",
                                          error_message="All fields are required")

        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
        except ValueError:
            raise BusinessValidationError(status_code=400, error_code="INVALID_DATE_FORMAT",
                                          error_message="Date format must be ISO 8601")

        new_campaign = Campaigns(campaign_name=campaign_name, description=description, start_date=start_date, end_date=end_date, budget=budget, visibility=visibility, goals=goals, sponsor_name=sponsor_name)
        db.session.add(new_campaign)
        db.session.commit()
        return new_campaign, 201

    @marshal_with(campaign_resource_fields)
    def put(self, campaign_id):
        data = request.get_json()
        campaign = Campaigns.query.filter_by(campaign_id=campaign_id).first()
        if not campaign:
            raise NotFoundError(status_code=404, error_code="CAMPAIGN_NOT_FOUND", error_message="Campaign not found")

        campaign.campaign_name = data.get("campaign_name", campaign.campaign_name)
        campaign.description = data.get("description", campaign.description)
        campaign.start_date = data.get("start_date", campaign.start_date)
        campaign.end_date = data.get("end_date", campaign.end_date)
        campaign.budget = data.get("budget", campaign.budget)
        campaign.visibility = data.get("visibility", campaign.visibility)
        campaign.goals = data.get("goals", campaign.goals)
        campaign.sponsor_name = data.get("sponsor_name", campaign.sponsor_name)
        db.session.commit()
        return campaign, 200

    def delete(self, campaign_id):
        campaign = Campaigns.query.filter_by(campaign_id=campaign_id).first()
        if not campaign:
            raise NotFoundError(status_code=404, error_code="CAMPAIGN_NOT_FOUND", error_message="Campaign not found")

        db.session.delete(campaign)
        db.session.commit()
        return {"message": "Campaign deleted successfully"}, 200


advertisement_resource_fields = {
    'ad_id': fields.Integer,
    'campaign_id': fields.Integer,
    'ad_name': fields.String,
    'amount': fields.Integer,
    'requirements': fields.String,
    'status': fields.String,
}


class AdvertisementsAPI(Resource):
    @marshal_with(advertisement_resource_fields)
    def get(self, ad_id=None):
        if ad_id:
            advertisement = Advertisements.query.filter_by(ad_id=ad_id).first()
            if not advertisement:
                raise NotFoundError(status_code=404, error_code="AD_NOT_FOUND", error_message="Advertisement not found")
            return advertisement, 200
        else:
            advertisements = Advertisements.query.all()
            if not advertisements:
                raise NotFoundError(status_code=404, error_code="NO_ADVERTISEMENTS", error_message="No advertisements found")
            return advertisements, 200

    @marshal_with(advertisement_resource_fields)
    def post(self):
        data = request.get_json()
        campaign_id = data.get("campaign_id")
        ad_name = data.get("ad_name")
        amount = data.get("amount")
        requirements = data.get("requirements")
        status = data.get("status")

        if not campaign_id or not ad_name or not amount or not requirements or not status:
            raise BusinessValidationError(status_code=400, error_code="MISSING_FIELDS",
                                          error_message="All fields are required")

        new_advertisement = Advertisements(campaign_id=campaign_id, ad_name=ad_name, amount=amount, requirements=requirements, status=status)
        db.session.add(new_advertisement)
        db.session.commit()
        return new_advertisement, 201

    @marshal_with(advertisement_resource_fields)
    def put(self, ad_id):
        data = request.get_json()
        advertisement = Advertisements.query.filter_by(ad_id=ad_id).first()
        if not advertisement:
            raise NotFoundError(status_code=404, error_code="AD_NOT_FOUND", error_message="Advertisement not found")

        advertisement.campaign_id = data.get("campaign_id", advertisement.campaign_id)
        advertisement.ad_name = data.get("ad_name", advertisement.ad_name)
        advertisement.amount = data.get("amount", advertisement.amount)
        advertisement.requirements = data.get("requirements", advertisement.requirements)
        advertisement.status = data.get("status", advertisement.status)
        db.session.commit()
        return advertisement, 200

    def delete(self, ad_id):
        advertisement = Advertisements.query.filter_by(ad_id=ad_id).first()
        if not advertisement:
            raise NotFoundError(status_code=404, error_code="AD_NOT_FOUND", error_message="Advertisement not found")

        db.session.delete(advertisement)
        db.session.commit()
        return {"message": "Advertisement deleted successfully"}, 200


@api_app.route('/test')
def test():
    return "Test route is working!"


api.add_resource(InfluencerAPI, '/influencers', '/influencers/<int:influencer_id>')
api.add_resource(SponsorAPI, '/sponsors', '/sponsors/<int:sponsor_id>')
api.add_resource(CampaignAPI, '/campaigns', '/campaigns/<int:campaign_id>')
api.add_resource(AdvertisementsAPI, '/advertisements', '/advertisements/<int:ad_id>')