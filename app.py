
from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_mail import Mail, Message
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)

questions = [
    "Do you regularly back up client records and scheduling data?",
    "Are backups stored in a secure, HIPAA-compliant location?",
    "Are backups tested regularly to ensure they can be restored?",
    "Are strong passwords required for all systems accessing client data?",
    "Is multi-factor authentication (MFA) used for systems like EHRs or cloud storage?",
    "Are accounts for former staff disabled or removed promptly?",
    "Do you have a written incident response plan in place (e.g., for ransomware or data breaches)?",
    "Have staff been briefed on what to do in case of a data breach?",
    "Do you know who to contact if there's a cybersecurity incident affecting client care?",
    "Are staff computers and mobile devices protected with up-to-date security software?",
    "Is your Wi-Fi secured with strong encryption (WPA2 or WPA3)?",
    "Is your mental health EHR or client management software updated regularly?",
    "Do you have a way to maintain access to key client info during an outage?",
    "Is there a secure contact list of staff and emergency contacts available offline?",
    "Have roles and responsibilities been defined for crisis situations?",
    "Have staff received cybersecurity and HIPAA compliance training in the last year?",
    "Are staff trained to recognize phishing attempts or social engineering?",
    "Is there a clear way for staff to report suspicious emails or activity?"
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/checklist', methods=['GET', 'POST'])
def checklist():
    if request.method == 'POST':
        answers = request.form
        score = sum(1 for q in questions if answers.get(q) == 'yes')

        if score >= 16:
            level = "LOW – Good posture and planning!"
        elif score >= 10:
            level = "MODERATE – Some gaps to close."
        else:
            level = "HIGH – Needs immediate attention!"

        # 🧠 Enhanced detail for each failed question
        failed_questions = []
        for q in questions:
            if answers.get(q) != 'yes':
                failed_questions.append({
                    "question": q,
                    "explanation": "This question was not passed. (Explanation placeholder)",
                    "exploitation": "Could be exploited by attackers. (Placeholder)",
                    "client_impact": "Might impact client safety or data.",
                    "compliance": "Possible HIPAA violation.",
                    "help": "I can help mitigate this risk."
                })

        return render_template('result.html', score=score, total=len(questions), level=level,
                               answers=answers, questions=questions, failed_questions=failed_questions)

    return render_template('index.html', questions=questions)
    if __name__ == '__main__':
    app.run(debug=True)



@app.route('/download', methods=['POST'])
def download():
    answers = request.form
    score = sum(1 for q in questions if answers.get(q) == 'yes')

    if score >= 16:
        level = "LOW – Good posture and planning!"
    elif score >= 10:
        level = "MODERATE – Some gaps to close."
    else:
        level = "HIGH – Needs immediate attention!"

    rendered = render_template("pdf_template.html", answers=answers, questions=questions, score=score, level=level)
    pdf = BytesIO()
    pisa.CreatePDF(rendered, dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=cyber_posture_report.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)

