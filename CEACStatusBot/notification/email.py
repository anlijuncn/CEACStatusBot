from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from .handle import NotificationHandle

class EmailNotificationHandle(NotificationHandle):
    def __init__(self,fromEmail:str,toEmail:str,emailPassword:str,hostAddress:str='') -> None:
        super().__init__()
        self.__fromEmail = fromEmail
        self.__toEmail = toEmail.split("|")
        self.__emailPassword = emailPassword
        self.__hostAddress = hostAddress or "smtp."+fromEmail.split("@")[1]
        if ':' in self.__hostAddress:
            [addr, port] = self.__hostAddress.split(':')
            self.__hostAddress = addr
            self.__hostPort = int(port)
        else:
            self.__hostPort = 0

    def send(self, result):
        # 标题与正文
        mail_title = '[CEACStatusBot] {} : {}'.format(
            result["application_num_origin"], result['status']
        )
        mail_content = str(result)
    
        # 构建邮件
        msg = MIMEMultipart()
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = self.__fromEmail
        msg["To"] = ",".join(self.__toEmail)   # 头部显示用逗号
        msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
    
        # 主机与端口兜底
        host = self.__hostAddress or "smtp.gmail.com"
        port = getattr(self, "_EmailNotificationHandle__hostPort", None) or 465
    
        try:
            with SMTP_SSL(host, port) as smtp:
                # 对于 Gmail：请使用 App Password
                login_resp = smtp.login(self.__fromEmail, self.__emailPassword)
                print("LOGIN:", login_resp)  # 可选：('235', b'2.7.0 Accepted') 类似
    
                # 第二个参数必须是收件人列表
                send_resp = smtp.sendmail(self.__fromEmail, self.__toEmail, msg.as_string())
                print("SENDMAIL:", send_resp)  # 通常为空字典 {} 表示成功
        except Exception as e:
            # 便于调试
            print("SMTP ERROR:", repr(e))
            raise
