import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename


def send_mail(toaddr, theme, text, files = None, user_id = 0): #onefit.chat@mail.ru : qazwsx123
	fromaddr = "azs_menu@mail.ru"
	mypass = "qazwsx123"
	 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = theme
	 
	msg.attach(MIMEText(text))

	server = smtplib.SMTP('smtp.mail.ru', 587)
	server.starttls()
	server.login(fromaddr, mypass)
	text = msg.as_string()
	try:
		server.sendmail(fromaddr, toaddr, text)
		server.quit()
		return True
	except:
		print("Mail send error")
		server.quit()
		if user_id != 0:
			return False