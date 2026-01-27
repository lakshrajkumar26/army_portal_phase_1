import os
import tempfile
from django.http import FileResponse, Http404
from results.models import CandidateAnswer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.pdfencrypt import StandardEncryption


def export_answers_pdf(request):
    try:
        answers = CandidateAnswer.objects.select_related("candidate", "paper", "question")

        if not answers.exists():
            raise Http404("No answers found.")

        # Candidate details (first record for naming)
        candidate = answers[0].candidate
        army_no = getattr(candidate, "army_no", candidate.user.username)
        candidate_name = candidate.user.get_full_name()

        # File name
        filename = f"{army_no}_answers.pdf"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        # PDF Encryption → user must enter password to open
        password = army_no  # 👉 you can use army_no, candidate_name, or set your own password
        enc = StandardEncryption(
            userPassword=password,     # required to open PDF
            ownerPassword="admin123",  # admin override password
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0
        )

        # Create PDF
        c = canvas.Canvas(tmp_path, pagesize=A4, encrypt=enc)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Candidate Answers Export")

        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Army No: {army_no}")
        c.drawString(1 * inch, height - 1.8 * inch, f"Name: {candidate_name}")
        c.drawString(1 * inch, height - 2.1 * inch, f"Category: {candidate.category}")
        c.drawString(1 * inch, height - 2.4 * inch, f"Paper: {answers[0].paper.title}")

        y = height - 3 * inch
        c.setFont("Helvetica", 11)

        for idx, ans in enumerate(answers, start=1):
            question_text = (ans.question.text[:80] + "...") if len(ans.question.text) > 80 else ans.question.text
            c.drawString(1 * inch, y, f"Q{idx}: {question_text}")
            y -= 0.3 * inch
            c.drawString(1.2 * inch, y, f"Answer: {ans.answer}")
            y -= 0.5 * inch

            if y < 1.5 * inch:  # new page
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 1 * inch

        c.save()

        # Return file
        return FileResponse(open(tmp_path, "rb"), as_attachment=True, filename=filename)

    except Exception as e:
        raise Http404(f"Error exporting candidate answers: {e}")
