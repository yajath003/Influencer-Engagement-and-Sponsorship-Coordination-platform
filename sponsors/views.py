
from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from werkzeug.security import generate_password_hash
import base64

from sponsors.forms import signupForm, loginForm, CampaignsForm, AdvertisementForm, SearchForm
from sponsors.models import sponsor_login, Campaigns, Advertisements, sponsor_requests, sponsor_accepts
from influencers.models import influencer_login, influencer_requests, influencer_accepts, completed
from application import db

sponsors_app = Blueprint('sponsors_app', __name__)


@sponsors_app.route('/sponsor')
def sponsor():
    return render_template('sponsors/sponsor.html')


@sponsors_app.route('/ssignup', methods=['GET', 'POST'])
def ssignup():
    form = signupForm()
    if form.validate_on_submit():
        profile_pic_data = None
        if form.profile_pic.data:
            profile_pic_data = form.profile_pic.data.read()
            form.profile_pic.data.seek(0)
        hashed_password = generate_password_hash(form.password.data)
        sponsor = sponsor_login(
            sponsor_name=form.sponsor_name.data,
            email=form.email1.data,
            password=hashed_password,
            company_name=form.company_name.data,
            Industry=form.Industry.data,
            profile_pic=profile_pic_data
        )
        db.session.add(sponsor)
        db.session.commit()
        return redirect(url_for('.ssignin'))
    return render_template('sponsors/signup.html', form=form)


@sponsors_app.route('/ssignin', methods=['GET', 'POST'])
def ssignin():
    form = loginForm()
    if form.validate_on_submit():
        session['sponsor_name'] = form.sponsor_name.data
        return redirect(url_for('.hhome'))
    return render_template('sponsors/signin.html', form=form)


@sponsors_app.route('/hhome', methods=['GET', 'POST'])
def hhome():
    ads = Advertisements.query.all()
    ad_inf_names = {a.ad_name for a in influencer_accepts.query.all()}
    ad_spon_names = {a.ad_name for a in sponsor_accepts.query.all()}
    for ad in ads:
        if ad.ad_name in ad_inf_names or ad.ad_name in ad_spon_names:
            ad.status = 'accepted'
        db.session.commit()
    sponsor = sponsor_login.query.filter_by(sponsor_name=session.get('sponsor_name')).first()
    profile_pic = None
    if sponsor.profile_pic:
        profile_pic = base64.b64encode(sponsor.profile_pic).decode('utf-8')
    return render_template('sponsors/home.html', sponsor=sponsor, profile_pic=profile_pic)


@sponsors_app.route('/campaigns', methods=['GET', 'POST'])
def campaigns():
    campaign = Campaigns.query.filter_by(sponsor_name=session['sponsor_name'])
    sponsors = sponsor_login.query.filter_by(sponsor_name=session.get('sponsor_name'))
    if request.method == 'POST':
        value = request.form.get('searched')
        session['search'] = value
        return redirect(url_for('.search'))
    profile_pic = []
    for sponsor in sponsors:
        if sponsor.profile_pic:
            profile_pic.append(base64.b64encode(sponsor.profile_pic).decode('utf-8'))

    return render_template('sponsors/campaigns.html', campaign=campaign, profile_pic=profile_pic)


@sponsors_app.route('/ffind', methods=['GET', 'POST'])
def ffind():
    form = signupForm()
    campaign = Campaigns.query.all()
    influencers = influencer_login.query.all()

    if request.method == 'POST':
        value = request.form.get('searched')
        session['search'] = value
        return redirect(url_for('.ssearch'))

    profile_pic1 = []
    sponsors = sponsor_login.query.all()
    for sponsor in sponsors:
        if sponsor.profile_pic:
            profile_pic1.append(base64.b64encode(sponsor.profile_pic).decode('utf-8'))

    profile_pic = []
    for influencer in influencers:
        if influencer.profile_pic:
            profile_pic.append(base64.b64encode(influencer.profile_pic).decode('utf-8'))

    return render_template(
        'sponsors/find.html',
        form=form,
        campaign=campaign,
        influencers=influencers,
        profile_pic1=profile_pic1,
        profile_pic=profile_pic
    )


@sponsors_app.route('/sstats', methods=['GET', 'POST'])
def sstats():
    campaigns = Campaigns.query.filter_by(sponsor_name=session['sponsor_name']).all()
    campaign_ids = [campaign.campaign_id for campaign in campaigns]
    data_list1 = []
    data_list2 = []
    for id in campaign_ids:
        ads = influencer_accepts.query.filter_by(campaign_id=id).all()
        for ad in ads:
            campaign_name = Campaigns.query.filter_by(campaign_id=ad.campaign_id).first().campaign_name
            data_list1.append((ad.ad_name, campaign_name, ad.influencer_name, 'pending'))
        ads1 = completed.query.filter_by(campaign_id=id).all()
        for ad in ads1:
            campaign_name = Campaigns.query.filter_by(campaign_id=ad.campaign_id).first().campaign_name
            data_list1.append((ad.ad_name, campaign_name, ad.influencer_name, 'completed'))
    return render_template('sponsors/stats.html', data_list=data_list1)


@sponsors_app.route('/new_campaign', methods=['GET', 'POST'])
def new_campaign():
    form = CampaignsForm()
    if form.validate_on_submit():
        campaign = Campaigns(
            campaign_name=form.campaign_name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            goals=form.goals.data,
            sponsor_name=session['sponsor_name']
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('.campaigns'))
    return render_template('sponsors/new_campaign.html', form=form)


@sponsors_app.route('/campaign_details', methods=['GET', 'POST'])
def campaign_details():
    if request.method == 'POST':
        session['campaign_id'] = request.form.get('campaign_id')
    else:
        campaign_id = request.args.get('campaign_id')
        if campaign_id:
            session['campaign_id'] = campaign_id

    campaign_id = session.get('campaign_id')
    if not campaign_id:
        return "Campaign ID not found", 400

    details = Campaigns.query.filter_by(campaign_id=campaign_id).first()
    if not details:
        return "Campaign not found", 404

    ads = Advertisements.query.filter_by(campaign_id=campaign_id).all()
    name = details.sponsor_name
    button = True if session.get('sponsor_name') == name else False
    profile_pic1 = [base64.b64encode(ad.images).decode('utf-8') for ad in ads if ad.images]

    return render_template('sponsors/campaign_details.html', details=details, ads=ads, button=button,
                           profile_pic1=profile_pic1)


@sponsors_app.route('/new_ad', methods=['GET', 'POST'])
def new_ad():
    form = AdvertisementForm()
    if form.validate_on_submit():
        profile_pic_data = None
        if form.images.data:
            profile_pic_data = form.images.data.read()
        ad = Advertisements(
            campaign_id=session.get('campaign_id'),
            amount=form.amount.data,
            requirements=form.requirements.data,
            status='pending',
            images=profile_pic_data,
            ad_name=form.ad_name.data
        )
        db.session.add(ad)
        db.session.commit()
        return redirect(url_for('sponsors_app.campaign_details', campaign_id=session.get('campaign_id')))
    return render_template('sponsors/new_ad.html', form=form)


@sponsors_app.route('/ad_details', methods=['GET', 'POST'])
def ad_details():
    if request.method == 'POST':
        session['ad_id'] = request.form.get('ad_id')
    else:
        ad_id = request.args.get('ad_id')
        if ad_id:
            session['ad_id'] = ad_id
    details = Advertisements.query.filter_by(ad_id=session['ad_id']).first()
    profile_pic = None
    if details.images:
        profile_pic = base64.b64encode(details.images).decode('utf-8')
    return render_template('sponsors/ad_details.html', details=details, profile_pic=profile_pic)


@sponsors_app.route('/influencer_details', methods=['GET', 'POST'])
def influencer_details():
    if request.method == 'POST':
        session['spon_influencer_id'] = request.form.get('influencer_id')
    else:
        influencer_id = request.args.get('influencer_id')
        if influencer_id:
            session['spon_influencer_id'] = influencer_id
    details = influencer_login.query.filter_by(influencer_id=session['spon_influencer_id']).first()
    profile_pic = None
    if details.profile_pic:
        profile_pic = base64.b64encode(details.profile_pic).decode('utf-8')
    return render_template('sponsors/influencer_details.html', details=details,
                           profile_pic=profile_pic)


@sponsors_app.route('/ssearch', methods=['GET', 'POST'])
def ssearch():
    search_value = session.get('search')
    lst1 = []
    lst2 = []
    if search_value:
        campaigns = (Campaigns.query.filter(Campaigns.campaign_name.ilike(f'%{search_value}%')).all()
                     or Campaigns.query.filter(Campaigns.sponsor_name.ilike(f'%{search_value}%')).all())
        for campaign in campaigns:
            camp_name = campaign.sponsor_name
            spon = sponsor_login.query.filter_by(sponsor_name=camp_name)
            for s in spon:
                if s.profile_pic:
                    lst2.append(base64.b64encode(s.profile_pic).decode('utf-8'))
        influencers = influencer_login.query.filter(influencer_login.influencer_name.ilike(f'%{search_value}%')).all()
        for influencer in influencers:
            if influencer.profile_pic:
                lst1.append(base64.b64encode(influencer.profile_pic).decode('utf-8'))
    else:
        campaigns = []
        influencers = []
    if (campaigns or influencers):
        flash('Yay something found...!')
    return render_template('sponsors/search.html', campaigns=campaigns, influencers=influencers,
                           lst1=lst1, lst2=lst2)


@sponsors_app.route('/request_influencers', methods=['GET', 'POST'])
def request_influencers():
    req = influencer_login.query.all()
    ad_id = request.args.get('ad_id') or request.form.get('ad_id')
    print(ad_id)
    if request.method == 'POST':
        selected_influencer_ids = request.form.getlist('influencer_id')
        if selected_influencer_ids:
            influencer_ids = ','.join(selected_influencer_ids)
            new_request = sponsor_requests(
                ad_id=ad_id,
                influencer_ids=influencer_ids
            )
            db.session.add(new_request)
            db.session.commit()
            flash("Request sent successfully.", "success")
        else:
            flash("No influencers selected.", "warning")
        return redirect(url_for('sponsors_app.campaign_details'))
    return render_template('sponsors/request_influencers.html', req=req, ad_id=ad_id)


@sponsors_app.route('/rrequests', methods=['GET', 'POST'])
def rrequests():
    sponsor_name = session.get('sponsor_name')
    campaigns = Campaigns.query.filter_by(sponsor_name=sponsor_name).all()
    campaign_ids = [campaign.campaign_id for campaign in campaigns]

    if campaign_ids:
        result = influencer_requests.query.filter(influencer_requests.campaign_id.in_(campaign_ids)).all()
    else:
        result = []

    final = []
    for i in result:
        inf_id = i.influencer_id
        inf_det = influencer_login.query.filter_by(influencer_id=inf_id).first()
        ad_id = i.ad_id
        ad_details = Advertisements.query.filter_by(ad_id=ad_id).first()
        camp_id = i.campaign_id
        camp_det = Campaigns.query.filter_by(campaign_id=camp_id).first()
        req_id = i.request_id
        if inf_det and ad_details and camp_det:
            final.append({
                'inf_name': inf_det.influencer_name,
                'ad_name': ad_details.ad_name,
                'campaign_name': camp_det.campaign_name,
                'request_id': req_id
            })

    if request.method == 'POST':
        selected_requests = request.form.getlist('selected_requests')
        print("Selected requests:", selected_requests)

        for req_id in selected_requests:
            req = influencer_requests.query.get(req_id)
            if req:
                inf_det = influencer_login.query.filter_by(influencer_id=req.influencer_id).first()
                ad_details = Advertisements.query.filter_by(ad_id=req.ad_id).first()
                camp_det = Campaigns.query.filter_by(campaign_id=req.campaign_id).first()
                if inf_det and ad_details and camp_det:
                    new_accept = sponsor_accepts(
                        ad_name=ad_details.ad_name,
                        campaign_name=camp_det.campaign_name,
                        influencer_name=inf_det.influencer_name
                    )
                    db.session.add(new_accept)
                    db.session.delete(req)
                    db.session.commit()

        return redirect(url_for('sponsors_app.rrequests'))

    return render_template('sponsors/requests.html', advertisements=final)


@sponsors_app.route('/dlt_campaign', methods=['GET', 'POST'])
def dlt_campaign():
    if request.method == 'POST':
        campaign_ids = request.form.getlist('campaign_ids')
        for camp in campaign_ids:
            ads = Advertisements.query.filter_by(campaign_id=camp)
            for ad in ads:
                db.session.delete(ad)
            campp = Campaigns.query.filter_by(campaign_id=camp)
            for cmp in campp:
                db.session.delete(cmp)
        db.session.commit()
        flash('The selected campaigns along with their ads are deleted successfully')
        return redirect(url_for('sponsors_app.dlt_campaign'))
    campaigns = Campaigns.query.filter_by(sponsor_name=session['sponsor_name']).all()
    return render_template('sponsors/dlt_campaign.html', campaigns=campaigns)


@sponsors_app.route('/dlt_ad', methods=['GET', 'POST'])
def dlt_ad():
    if request.method == 'POST':
        ad_ids = request.form.getlist('ad_ids')
        for ad in ad_ids:
            ads = Advertisements.query.filter_by(ad_id=ad)
            for a in ads:
                db.session.delete(a)
        db.session.commit()
        flash('The selected ads deleted successfully')
        return redirect(url_for('sponsors_app.dlt_ad'))
    campaigns = Campaigns.query.filter_by(sponsor_name=session['sponsor_name']).all()
    ads = []
    for camp in campaigns:
        ads.append(camp.campaign_id)
    advertisements = []
    for a in ads:
        advertisements.append(Advertisements.query.filter_by(campaign_id=a))
    return render_template('sponsors/dlt_ad.html', advertisements=advertisements)