#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_user, logout_user, login_required
from sqlalchemy.orm.exc import NoResultFound

from sharepy.application import app
from sharepy.database import User
from forms import LoginForm


@app.route('/', methods=['GET', 'POST'])
def index():
    """For now, the landing page is also the login page.
    """
    if not current_user.is_anonymous():
        return redirect(url_for('my_home'))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.q.filter(User.login == form.username.data).one()
        except NoResultFound:
            flash(u"Invalid credentials", "error")
            return redirect(url_for('index'))

        if user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('my_home'))
        else:
            flash(u"Invalid credentials", "error")

    return render_template('index.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/my')
@login_required
def my_home():
    return render_template('my/home.html')


@app.route('/my/uploads')
@login_required
def my_uploads():
    return redirect(url_for('my_home'))
