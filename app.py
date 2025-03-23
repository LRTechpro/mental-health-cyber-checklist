from flask import Flask, render_template, request, make_response
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

explanations = {
    "Do you regularly back up client records and scheduling data?": {
        "why": "Backups protect sensitive client data from loss due to ransomware, accidental deletion, or hardware failure.",
        "exploit": "Attackers could encrypt or delete data, leaving the organization without recovery options.",
        "impact": "Client records, appointments, and treatment history may be lost, disrupting care and trust.",
        "compliance": "HIPAA §164.308(a)(7)(ii)(A) – Requires data backup plans.",
        "help": "I can configure secure, automatic backups with audit trails and off-site storage options."
    },
    "Are backups stored in a secure, HIPAA-compliant location?": {
        "why": "Secure, compliant storage ensures backups aren't vulnerable to physical or digital threats.",
        "exploit": "An attacker or natural disaster could destroy on-site backups or access insecure cloud storage.",
        "impact": "Permanent loss of client data and potential data breaches.",
        "compliance": "HIPAA §164.308(a)(1)(ii)(A) – Risk mitigation through secure systems.",
        "help": "I can help transition to encrypted, HIPAA-compliant cloud solutions."
    },
    "Are backups tested regularly to ensure they can be restored?": {
        "why": "A backup that hasn’t been tested may fail when you need it most.",
        "exploit": "Data may be corrupted or incompatible during a restore, leaving the organization vulnerable.",
        "impact": "Loss of continuity of care, potential HIPAA violations, and client service disruption.",
        "compliance": "HIPAA §164.308(a)(7)(ii)(D) – Requires testing procedures.",
        "help": "I can implement a backup testing process and verify data integrity regularly."
    }
    # Additional explanation entries go here as needed...
}

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

        failed_questions = []
        for q in questions:
            if answers.get(q) != 'yes':
                details = explanations.get(q, {})
                failed_questions.append({
                    "question": q,
                    "explanation": details.get("why", "No explanation provided."),
                    "exploitation": details.get("exploit", "No data."),
                    "client_impact": details.get("impact", "No impact info."),
                    "compliance": details.get("compliance", "HIPAA impact unknown."),
                    "help": details.get("help", "I can assist with improving this area.")
                })

        return render_template('result.html', score=score, total=len(questions), level=level,
                               answers=answers, questions=questions, failed_questions=failed_questions)

    return render_template('index.html', questions=questions)

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

    failed_questions = []
    for q in questions:
        if answers.get(q) != 'yes':
            details = explanations.get(q, {})
            failed_questions.append({
                "question": q,
                "explanation": details.get("why", "No explanation provided."),
                "exploitation": details.get("exploit", "No data."),
                "client_impact": details.get("impact", "No impact info."),
                "compliance": details.get("compliance", "HIPAA impact unknown."),
                "help": details.get("help", "I can assist with improving this area.")
            })

    rendered = render_template("pdf_template.html", answers=answers, questions=questions,
                               score=score, level=level, failed_questions=failed_questions)
    pdf = BytesIO()
    pisa.CreatePDF(rendered, dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=cyber_posture_report.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
