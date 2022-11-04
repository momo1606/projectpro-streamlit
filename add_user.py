import streamlit_authenticator as stauth

import database as db

names = ['Ankani','Kedar','Shwetha','Mohammad','Divya']
usernames = ['ankani','kedar','shwetha','hassan','divya']
passwords = ['Dezyre123','Dezyre123','Dezyre123','Dezyre123','Dezyre123']
hashed_passwords = stauth.Hasher(passwords).generate()


for (username, name, hash_password) in zip(usernames, names, hashed_passwords):
    db.insert_user(username, name, hash_password)