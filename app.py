from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_mail import Mail, Message
import base64

app = Flask(__name__)
app.config.from_object('config.Config')

mail = Mail(app)
api = Api(app)

@app.route('/')
def index():
    return "Welcome to the Email API. Use the /send-email endpoint to send emails."

class SendEmail(Resource):
    def post(self):
        data = request.get_json()
        subject = data['subject']
        recipients = data['recipients']
        body = data['body']
        attachments = data.get('attachments', [])
        sender = app.config['MAIL_DEFAULT_SENDER']

        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        
        for attachment in attachments:
            try:
                filename = attachment['filename']
                content_type = attachment['content_type']
                data = base64.b64decode(attachment['data'])
                msg.attach(filename, content_type, data)
            except Exception as e:
                app.logger.error(f"Error decoding attachment: {str(e)}")
                return jsonify({"message": "Failed to decode attachment", "error": str(e)})

        try:
            mail.send(msg)
            return jsonify({"message": "Email sent successfully!", "status": 200})
        except Exception as e:
            return jsonify({"message": "Failed to send email", "error": str(e), "status": 500})

api.add_resource(SendEmail, '/send-email')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
