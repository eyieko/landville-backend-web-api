invalid_token = "eyJ0eXiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IkFoZWJ3YTEiLCJlbWFpbCI6ImNyeWNldHJ1bHlAZ21haWwuY29tIiwiZXhwIjoxNTUxNzc2Mzk0fQ.PFimaBvSaxR_cKwLmeRMod7LHkhNTcem22IXTrrg7Ko~5"
expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFhY3J5Y2VAZ21haWwuY29tIiwiZXhwIjoxNTU4NjQ5MjQ1fQ.dxRsbiCJyof-pFT1OqxLzd04HPBnGeuwJtebjqwbsIE~1"
valid_user_data = {
    "first_name": "Truly",
    "last_name": "Chryce",
    "email": "crycetruly@gmail.com",
    "password": "Eg0#Tc1Rd+",
    "confirmed_password": "Eg0#Tc1Rd+"
}

umatching_passwords_data = {
    "first_name": "Truly123",
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@cx"
}
invalid_email_data = {
    "first_name": "Truly",
    "last_name": "Chryce",
    "email": "crycgmail.com",
    "password": "Eg0#Tc1Rd+",
    "confirmed_password": "Eg0#Tc1Rd+"
}

weak_password_data = {
    "first_name": "Truly",
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456",
    "confirmed_password": "Eg0#Tc1Rd+"
}
number_in_first_name_data = {
    "first_name": "Truly123",
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}
number_in_lastname_name_data = {
    "first_name": "Truly",
    "last_name": "Chryce5",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}
space_in_lastname_data = {
    "first_name": "Truly",
    "last_name": "Chryce T",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}

space_in_firstname_data = {
    "first_name": "Truly T",
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}

missing_firstname_data = {
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}

missing_lastname_data = {
    "first_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}
empty_firstname_data = {
    "first_name": "",
    "last_name": "Chryce",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}


empty_last_name_data = {
    "first_name": "Chryce",
    "last_name": "",
    "email": "crycg@mail.com",
    "password": "123456!@c",
    "confirmed_password": "123456!@c"
}
