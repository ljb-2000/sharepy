#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, flash, send_file
from flask.ext.login import current_user, login_user, logout_user, login_required
from os import path
from sqlalchemy.orm.exc import NoResultFound

from sharepy.application import app
from sharepy.config import FILES_STORAGEDIR
from sharepy.database import session, User, File, FileToken
from sharepy.filehandling import get_unregistered_files, register_file
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
    unregistered = get_unregistered_files(current_user.login)
    return render_template('my/uploads.html', unregistered_files=unregistered)


@app.route('/my/register_file/')
@app.route('/my/register_file/<string:filename>')
@login_required
def my_register_file(filename=None):
    if filename:
        try:
            new_file = File(filename, current_user)
            register_file(current_user.login, filename, new_file.hashstring)
            session.add(new_file)
            session.commit()

            new_token = FileToken(new_file.id)
            session.add(new_token)
            session.commit()
        except OSError:
            session.rollback()
            flash(u"File '{}' not found in your upload dir.".format(filename),
                  "error")
    return redirect(url_for('my_uploads'))


@app.route('/dl/<string:tokenstring>')
@app.route('/dl/<string:tokenstring>/<string:filename>')
def download_token(tokenstring, filename=None):
    try:
        token = FileToken.q.filter(FileToken.identifier == tokenstring).one()
    except NoResultFound:
        flash(u"Token is invalid!", "error")
        return redirect(url_for('index'))

    if not filename:
        return redirect(url_for('download_token', tokenstring=tokenstring,
                                filename=token.file.name))

    return send_file(path.join(FILES_STORAGEDIR, token.file.hashstring),
                     as_attachment=True, attachment_filename=token.file.name)
