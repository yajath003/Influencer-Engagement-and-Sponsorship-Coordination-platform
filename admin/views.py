from flask import Blueprint, render_template, redirect, session, request,url_for, flash
import matplotlib.pyplot as plt
import io
import base64

from admin.forms import admin_login_form
from influencers.models import influencer_accepts, influencer_requests, influencer_login, completed
from sponsors.models import sponsor_login, sponsor_requests, sponsor_accepts, Campaigns, Advertisements
from admin.models import flag_sponsor, flag_influencer
from application import db

admin_app =Blueprint('admin_app', __name__)


@admin_app.route('/')
def index():
    return render_template('index.html')


@admin_app.route('/admin', methods=['POST', 'GET'])
def admin():
    form = admin_login_form()
    if form.validate_on_submit():
        return redirect(url_for('admin_app.admin_home'))
    return render_template('admin/admin.html', form=form)


@admin_app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():
    inf_count = influencer_login.query.count()
    spon_count = sponsor_login.query.count()
    ad_count = Advertisements.query.count()
    camp_count = Campaigns.query.count()
    influencers = influencer_login.query.all()
    sponsors = sponsor_login.query.all()
    complete = completed.query.count()

    labels = ['Influencers', 'Sponsors', 'Admins']
    sizes = [inf_count, spon_count, 1]
    colors = ['#FF6384', '#36A2EB', '#FFCE56']
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=70)
    ax.axis('equal')
    plt.title('STATS')
    img = io.BytesIO()
    fig.savefig(img, format='png', transparent=True)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    labels1 = ['Completed', 'Pending']
    sizes1 = [complete, abs(ad_count - complete)]
    colors1 = ['#FF6384', '#36A2EB']
    fig, ax = plt.subplots()
    ax.pie(sizes1, labels=labels1, colors=colors1, autopct='%1.1f%%', startangle=100)
    ax.axis('equal')
    plt.title('Advertisements')
    img1 = io.BytesIO()
    fig.savefig(img1, format='png', transparent=True)
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close(fig)

    influencers_table = []
    for influencer in influencers:
        inf_name = influencer.influencer_name
        category = influencer.category
        stat = flag_influencer.query.filter_by(influencer_name=inf_name).first()
        if stat:
            status = 'flagged'
        else:
            status = 'available'
        influencers_table.append((inf_name, category, status))
    sponsors_table = []
    for sponsor in sponsors:
        spon_name = sponsor.sponsor_name
        company = sponsor.company_name
        stat = flag_sponsor.query.filter_by(sponsor_name=spon_name).first()
        if stat:
            status = 'flagged'
        else:
            status = 'available'
        sponsors_table.append((spon_name, company, status))
    return render_template('admin/home.html', inf_count=inf_count, spon_count=spon_count,
                           ad_count=ad_count, camp_count=camp_count, influencers=influencers, sponsors=sponsors,
                           plot_url=plot_url, plot_url1=plot_url1, influencers_table=influencers_table,
                           sponsors_table=sponsors_table)


@admin_app.route('/flag', methods=['GET', 'POST'])
def flag():
    influencers = influencer_login.query.all()
    sponsors = sponsor_login.query.all()
    if request.method == 'POST':
        inf_list = request.form.getlist('inf')
        spon_list = request.form.getlist('spon')
        if inf_list:
            for i in inf_list:
                temp = flag_influencer.query.filter_by(influencer_name=i).count()
                if not temp:
                    flagged = flag_influencer(
                        influencer_name=i
                    )
                    db.session.add(flagged)
                    db.session.commit()
                else:
                    flash('The selected influencer is already flagged')
        if spon_list:
            for i in spon_list:
                temp = flag_sponsor.query.filter_by(sponsor_name=i).count()
                if not temp:
                    flagged = flag_sponsor(
                        sponsor_name=i
                    )
                    db.session.add(flagged)
                    db.session.commit()
                else:
                    flash('The selected sponsor is already flagged')
        flash('Selected members are flagged')
        return redirect(url_for('.flag'))
    return render_template('admin/flag.html', influencers=influencers, sponsors=sponsors)


@admin_app.route('/unflag', methods=['GET', 'POST'])
def unflag():
    influencers = flag_influencer.query.all()
    sponsors = flag_sponsor.query.all()
    if request.method == 'POST':
        inf_list = request.form.getlist('inf')
        spon_list = request.form.getlist('spon')
        if inf_list:
            for influencer_name in inf_list:
                influencer = flag_influencer.query.filter_by(influencer_name=influencer_name).first()
                if influencer:
                    db.session.delete(influencer)
        if spon_list:
            for sponsor_name in spon_list:
                sponsor = flag_sponsor.query.filter_by(sponsor_name=sponsor_name).first()
                if sponsor:
                    db.session.delete(sponsor)
        db.session.commit()
        flash('The selected members are unflagged')
        return redirect(url_for('.unflag'))
    return render_template('admin/unflag.html', influencers=influencers, sponsors=sponsors)
