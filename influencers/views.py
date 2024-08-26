from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from werkzeug.security import generate_password_hash
import base64

from influencers.forms import signupForm, loginForm
from influencers.models import influencer_login, influencer_requests, influencer_accepts, completed
from sponsors.models import sponsor_login, Campaigns, Advertisements, sponsor_requests
from application import db
from influencers.decerators import login_required


influencers_app = Blueprint('influencers_app', __name__)


@influencers_app.route('/influencer')
def influencer():
    return render_template('influencers/influencer.html')


@influencers_app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = loginForm()
    if form.validate_on_submit():
        req = influencer_login.query.filter_by(influencer_name=form.influencer_name.data).first()
        session['influencer_id'] = req.influencer_id
        session['influencer_name'] = form.influencer_name.data
        return redirect(url_for('influencers_app.home'))
    return render_template('influencers/signin.html', form=form)


@influencers_app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = signupForm()
    if form.validate_on_submit():
        profile_pic_data = None
        if form.profile_pic.data:
            profile_pic_data = form.profile_pic.data.read()
        hashed_password = generate_password_hash(form.password.data)
        influencer = influencer_login(
            influencer_name=form.influencer_name.data,
            email=form.email.data,
            password=hashed_password,
            category=form.category.data,
            Instagram=form.Instagram.data,
            twitter=form.twitter.data,
            youtube=form.youtube.data,
            profile_pic=profile_pic_data
        )
        db.session.add(influencer)
        db.session.commit()
        return redirect(url_for('.signin'))
    return render_template('influencers/signup.html', form=form)


@influencers_app.route('/home', methods=['GET', 'POST'])
def home():
    if 'influencer_id' in session:
        influencer = influencer_login.query.get(session['influencer_id'])
        profile_pic = None
        if influencer.profile_pic:
            profile_pic = base64.b64encode(influencer.profile_pic).decode('utf-8')
    flash('Hello influencer...!')
    return render_template('influencers/home.html', influencer=influencer, profile_pic=profile_pic)


@influencers_app.route('/find', methods=['GET', 'POST'])
def find():
    form = signupForm()
    campaign = Campaigns.query.all()
    influencers = influencer_login.query.all()
    sponsors = sponsor_login.query.all()
    if request.method == 'POST':
        value = request.form.get('searched')
        session['search'] = value
        return redirect(url_for('.search'))
    profile_pic1 = []
    for sponsor in sponsors:
        if sponsor.profile_pic:
            profile_pic1.append(base64.b64encode(sponsor.profile_pic).decode('utf-8'))
    profile_pic = []
    for influencer in influencers:
        if influencer.profile_pic:
            profile_pic.append(base64.b64encode(influencer.profile_pic).decode('utf-8'))

    return render_template('influencers/find.html', campaign=campaign, influencers=influencers,
                           form=form, profile_pic=profile_pic, profile_pic1=profile_pic1)


@influencers_app.route('/stats', methods=['GET', 'POST'])
def stats():
    my_ads = influencer_accepts.query.filter_by(influencer_name=session.get('influencer_name')).all()
    acc_ads = completed.query.filter_by(influencer_name=session.get('influencer_name')).all()

    first = []
    campaign1 = []
    my_profile = []
    for my_ad in my_ads:
        temp = my_ad.ad_name
        first.append(Advertisements.query.filter_by(ad_name=temp).all())
        for ad in first:
            for a in ad:
                if a.images:
                    my_profile.append(base64.b64encode(a.images).decode('utf-8'))
        campaign = Campaigns.query.filter_by(campaign_id=my_ad.campaign_id).first()
        if campaign:
            campaign1.append(campaign.campaign_name)
        else:
            campaign1.append(None)

    second = []
    combined_completed = []
    my_profile1 = []
    for acc_ad in acc_ads:
        temp = acc_ad.ad_name
        ad_list = Advertisements.query.filter_by(ad_name=temp).all()
        campaign = Campaigns.query.filter_by(campaign_id=acc_ad.campaign_id).first()
        campaign_name = campaign.campaign_name if campaign else None
        second.append(ad_list)
        for ad in ad_list:
            combined_completed.append((ad, campaign_name))
            if ad.images:
                my_profile1.append(base64.b64encode(ad.images).decode('utf-8'))
    amount = sum(ad.amount for ad, _ in combined_completed)

    return render_template('influencers/stats.html', amount=amount, first=first, second=second,
                           combined_completed=combined_completed, arr1=my_profile, arr2=my_profile1)


@influencers_app.route('/ccampaign_details', methods=['GET', 'POST'])
@login_required
def ccampaign_details():
    if request.method == 'POST':
        session['campaign_id'] = request.form.get('campaign_id')
    else:
        campaign_id = request.args.get('campaign_id')
        if campaign_id:
            session['campaign_id'] = campaign_id
    details = Campaigns.query.filter_by(campaign_id=session['campaign_id']).first()
    ads = Advertisements.query.filter_by(campaign_id=session['campaign_id'])
    pics = []
    for ad in ads:
        if ad.images:
            pics.append(base64.b64encode(ad.images).decode('utf-8'))
    return render_template('influencers/campaign_details.html', details=details, ads=ads, pics=pics)


@influencers_app.route('/iinfluencer_details', methods=['GET', 'POST'])
@login_required
def iinfluencer_details():
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
    return render_template('influencers/influencer_details.html', profile_pic=profile_pic,
                           details=details)


@influencers_app.route('/search')
def search():
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
    return render_template('influencers/search.html', campaigns=campaigns, influencers=influencers,
                           lst1=lst1, lst2=lst2)


@influencers_app.route('/aad_details', methods=['GET', 'POST'])
def aad_details():
    if request.method == 'POST':
        ad_id = request.form.get('ad_id')
        temp = request.form.get('temp')
        influencer_id = session.get('influencer_id')

        if ad_id:
            session['ad_id'] = ad_id

        if ad_id and influencer_id:
            advertisement = Advertisements.query.filter_by(ad_id=ad_id).first()
            something = request.form.get('something')

            if something:
                if advertisement.status == 'pending':
                    existing_data = influencer_requests.query.filter_by(influencer_id=influencer_id, ad_id=ad_id,
                                                                        campaign_id=advertisement.campaign_id).first()

                    if not existing_data:
                        new_request = influencer_requests(
                            influencer_id=influencer_id,
                            ad_id=ad_id,
                            campaign_id=advertisement.campaign_id
                        )
                        try:
                            db.session.add(new_request)
                            db.session.commit()
                            flash("Request submitted successfully.", "success")
                        except Exception as e:
                            db.session.rollback()
                            flash("Error submitting request.", "error")

                        return redirect(url_for('.aad_details', ad_id=session['ad_id']))
                    else:
                        flash('You have already requested it...!', "error")
                        return redirect(url_for('.aad_details', ad_id=session.get('ad_id')))
                else:
                    flash('This advertisement is already taken by someone. Please check for other ads.', "error")
                    return redirect(url_for('.aad_details', ad_id=session.get('ad_id')))
            else:
                return redirect(url_for('.aad_details', ad_id=session.get('ad_id')))
        else:
            flash("Invalid session data.", "error")
            return redirect(url_for('.aad_details', ad_id=session.get('ad_id')))

    else:
        ad_id = request.args.get('ad_id') or session.get('ad_id')
        if not ad_id:
            flash("No Ad ID found in session.", "error")
            return redirect(url_for('influencers_app.search'))

        session['ad_id'] = ad_id

    details = Advertisements.query.filter_by(ad_id=ad_id).first()
    profile_pic = None
    if details and details.images:
        profile_pic = base64.b64encode(details.images).decode('utf-8')

    return render_template('influencers/ad_details.html', details=details, profile_pic=profile_pic)


@influencers_app.route('/requests', methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        selected_requests = request.form.getlist('selected_requests')
        if selected_requests:
            for req_id in selected_requests:
                try:
                    req_id = int(req_id)
                    req = sponsor_requests.query.filter_by(ad_id=req_id).first()
                    if req:
                        ad = Advertisements.query.filter_by(ad_id=req.ad_id).first()
                        if ad:
                            influencer_name = session.get('influencer_name')
                            new_accept = influencer_accepts(
                                influencer_name=influencer_name,
                                ad_name=ad.ad_name,
                                campaign_id=ad.campaign_id
                            )
                            db.session.add(new_accept)
                            db.session.delete(req)
                            db.session.commit()
                            flash('Request accepted successfully!', 'success')
                except Exception as e:
                    print(f"Error processing request_id {req_id}: {e}")
                    flash('An error occurred while processing your request.', 'danger')

        return redirect(url_for('influencers_app.requests'))

    req = sponsor_requests.query.all()
    ads = []
    profile_pic1 = []

    for i in req:
        influencer_ids = i.influencer_ids.split(',')
        if str(session.get('influencer_id')) in influencer_ids:
            ad = Advertisements.query.filter_by(ad_id=i.ad_id).first()
            if ad:
                ads.append(ad)
                if ad.images:
                    profile_pic1.append(base64.b64encode(ad.images).decode('utf-8'))

    return render_template('influencers/requests.html', req=ads, profile_pic1=profile_pic1)


@influencers_app.route('/my_ads', methods=['POST', 'GET'])
def my_ads():
    temp = influencer_accepts.query.filter_by(influencer_name=session['influencer_name']).all()
    arr = [ad.ad_name for ad in temp]
    arr1 = []
    arr2 = []

    for ad_name in arr:
        ads = Advertisements.query.filter_by(ad_name=ad_name).all()
        arr1.extend(ads)
        for ad in ads:
            if ad.images:
                arr2.append(base64.b64encode(ad.images).decode('utf-8'))

    if request.method == 'POST':
        complete = request.form.getlist('selected_requests')
        print("Selected requests:", complete)
        if complete:
            for req_id in complete:
                try:
                    req = influencer_accepts.query.filter_by(ad_name=req_id).first()
                    print("Processing request:", req_id)
                    if req:
                        ad = Advertisements.query.filter_by(ad_name=req.ad_name).first()
                        if ad:
                            influencer_name = session.get('influencer_name')
                            new_accept = completed(
                                influencer_name=influencer_name,
                                ad_name=ad.ad_name,
                                campaign_id=ad.campaign_id
                            )
                            db.session.add(new_accept)
                            db.session.delete(req)
                            db.session.commit()
                            flash('Processing the selected advertisements completed successfully...', 'success')
                        else:
                            flash(f"Advertisement not found for ad_name: {req.ad_name}", 'danger')
                    else:
                        flash(f"Request not found for ad_name: {req_id}", 'danger')
                except Exception as e:
                    flash(f"Error processing ad_name {req_id}: {e}", 'danger')

        return redirect(url_for('influencers_app.my_ads'))

    return render_template('influencers/my_ads.html', my_ads=arr1, arr2=arr2)
