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
    },
    "Are strong passwords required for all systems accessing client data?": {
        "why": "Weak passwords make systems easy targets for brute force or phishing attacks.",
        "exploit": "Unauthorized access through compromised passwords.",
        "impact": "Exposure of client session notes, PHI, and billing data.",
        "compliance": "HIPAA §164.308(a)(5)(ii)(D) – Password management.",
        "help": "I can implement secure password policies and train staff on credential hygiene."
    },
    "Is multi-factor authentication (MFA) used for systems like EHRs or cloud storage?": {
        "why": "MFA adds a second layer of protection in case a password is compromised.",
        "exploit": "Attackers can access sensitive systems using stolen credentials.",
        "impact": "Unauthorized access to client files, schedules, and messages.",
        "compliance": "HIPAA §164.312(d) – Person or entity authentication.",
        "help": "I can configure MFA across your platforms and help staff with onboarding."
    },
    "Are accounts for former staff disabled or removed promptly?": {
        "why": "Old accounts can be exploited by malicious insiders or attackers.",
        "exploit": "Former employees or hackers may use old credentials to breach systems.",
        "impact": "Unauthorized access to client data or disruption of services.",
        "compliance": "HIPAA §164.308(a)(3)(ii)(C) – Termination procedures.",
        "help": "I can implement automated account audits and deactivation policies."
    },
    "Do you have a written incident response plan in place (e.g., for ransomware or data breaches)?": {
        "why": "A response plan reduces chaos during crises and speeds up recovery.",
        "exploit": "Attackers take advantage of unprepared organizations, increasing damage.",
        "impact": "Delayed breach response, regulatory penalties, and reputational damage.",
        "compliance": "HIPAA §164.308(a)(6)(i) – Security incident procedures.",
        "help": "I can help create a customized, actionable incident response plan."
    },
    "Have staff been briefed on what to do in case of a data breach?": {
        "why": "Training ensures immediate, effective action during a breach.",
        "exploit": "Staff may panic or take wrong steps, worsening the incident.",
        "impact": "Breach escalation, loss of client trust, and non-compliance reporting delays.",
        "compliance": "HIPAA §164.530(b) – Workforce training.",
        "help": "I can develop quick-reference guides and lead training workshops."
    },
    "Do you know who to contact if there's a cybersecurity incident affecting client care?": {
        "why": "Knowing key contacts accelerates the incident response.",
        "exploit": "Delays in reporting or escalating incidents increase damage.",
        "impact": "Prolonged downtime and interrupted care delivery.",
        "compliance": "HIPAA §164.308(a)(6)(ii) – Response and reporting protocols.",
        "help": "I can map out escalation chains and create a contact matrix."
    },
    "Are staff computers and mobile devices protected with up-to-date security software?": {
        "why": "Antivirus and endpoint protection are essential to stop malware and phishing.",
        "exploit": "Attackers may exploit outdated systems to spread ransomware.",
        "impact": "Client data theft or system lockdowns that halt services.",
        "compliance": "HIPAA §164.308(a)(5)(ii)(B) – Malware protection.",
        "help": "I can deploy and manage real-time endpoint protection tools for all devices."
    },
    "Is your Wi-Fi secured with strong encryption (WPA2 or WPA3)?": {
        "why": "Encrypted Wi-Fi prevents unauthorized network access.",
        "exploit": "Hackers can intercept unencrypted traffic and access systems.",
        "impact": "Exposure of session notes, emails, and admin logins.",
        "compliance": "HIPAA §164.312(e)(1) – Protecting ePHI in transit.",
        "help": "I can assess and secure your network infrastructure."
    },
    "Is your mental health EHR or client management software updated regularly?": {
        "why": "Outdated software is a major entry point for attackers.",
        "exploit": "Vulnerabilities in unpatched systems may be used to breach data.",
        "impact": "Loss or exposure of client records and insurance claims.",
        "compliance": "HIPAA §164.308(a)(1)(ii)(B) – Security updates and patching.",
        "help": "I can create an update schedule and automate security patching."
    },
    "Do you have a way to maintain access to key client info during an outage?": {
        "why": "Continuity of care depends on accessing critical info during downtime.",
        "exploit": "Service disruptions may halt care if no backup process exists.",
        "impact": "Missed appointments, inability to access crisis notes or prescriptions.",
        "compliance": "HIPAA §164.308(a)(7)(ii)(C) – Emergency mode operation plan.",
        "help": "I can help develop an offline access strategy using encrypted backups."
    },
    "Is there a secure contact list of staff and emergency contacts available offline?": {
        "why": "Access to key people during a crisis is vital for coordination.",
        "exploit": "Inaccessible contact info slows down response efforts.",
        "impact": "Delayed mitigation and decision-making during emergencies.",
        "compliance": "HIPAA §164.308(a)(6)(i) – Incident response and communication.",
        "help": "I can build a digital and printed secure contact list with role-based access."
    },
    "Have roles and responsibilities been defined for crisis situations?": {
        "why": "Knowing who does what eliminates confusion under pressure.",
        "exploit": "Attackers can exploit disorganization to prolong breaches.",
        "impact": "Miscommunication leads to longer outages or noncompliance.",
        "compliance": "HIPAA §164.308(a)(5)(ii)(C) – Security responsibilities.",
        "help": "I can work with leadership to assign and document response roles."
    },
    "Have staff received cybersecurity and HIPAA compliance training in the last year?": {
        "why": "Ongoing training helps staff recognize and avoid threats.",
        "exploit": "Untrained staff may click malicious links or mishandle PHI.",
        "impact": "Human error is a leading cause of healthcare data breaches.",
        "compliance": "HIPAA §164.530(b) – Workforce training requirement.",
        "help": "I can create tailored annual refresher trainings and track completion."
    },
    "Are staff trained to recognize phishing attempts or social engineering?": {
        "why": "Phishing is the #1 way attackers get into healthcare systems.",
        "exploit": "A single click can expose entire client databases.",
        "impact": "Loss of sensitive data, trust, and compliance violations.",
        "compliance": "HIPAA §164.308(a)(5)(i) – Security awareness training.",
        "help": "I can run phishing simulations and awareness workshops."
    },
    "Is there a clear way for staff to report suspicious emails or activity?": {
        "why": "Fast reporting can stop attacks before they escalate.",
        "exploit": "If suspicious behavior goes unreported, attackers remain undetected.",
        "impact": "Longer time-to-detection increases data loss and liability.",
        "compliance": "HIPAA §164.308(a)(6)(ii) – Requires response and reporting procedures.",
        "help": "I can implement a simple reporting workflow with alerts and escalation."
    }
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
