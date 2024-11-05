import smtplib

EMAIL_HOST_USER = 'bholerampatidar4@gmail.com'
EMAIL_HOST_PASSWORD = 'ctzr eqmo zloy ygfo'

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    try:
        smtp.starttls()
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        smtp.sendmail("bholerampatidar4@gmail.com","bholerampatidar4@gmail.com","this is mail")
    except Exception as e:
        print(e)
    print("Login successful")