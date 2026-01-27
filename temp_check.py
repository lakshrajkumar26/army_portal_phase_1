from questions.models import QuestionPaper, Question, TradePaperActivation
from reference.models import Trade
from exams.models import Shift

# Check DMV trade
try:
    dmv_trade = Trade.objects.filter(name__icontains='DMV').first()
    print('DMV Trade:', dmv_trade)
    if dmv_trade:
        print('DMV Trade ID:', dmv_trade.id)
        print('DMV Trade Name:', dmv_trade.name)
except Exception as e:
    print('Error finding DMV trade:', e)

# Check question papers for DMV
try:
    dmv_papers = QuestionPaper.objects.filter(trade__name__icontains='DMV')
    print('DMV Question Papers:', dmv_papers.count())
    for paper in dmv_papers:
        print('- Paper:', paper.title, 'ID:', paper.id)
        questions = paper.questions.count() if hasattr(paper, 'questions') else 0
        print('  Questions:', questions)
except Exception as e:
    print('Error checking DMV papers:', e)

# Check Trade Paper Activation
try:
    dmv_activations = TradePaperActivation.objects.filter(trade__name__icontains='DMV')
    print('DMV Trade Activations:', dmv_activations.count())
    for activation in dmv_activations:
        print('- Trade:', activation.trade.name, 'Active:', activation.is_active)
except Exception as e:
    print('Error checking activations:', e)

# Check all questions for DMV
try:
    if dmv_trade:
        dmv_questions = Question.objects.filter(trade=dmv_trade)
        print('Total DMV Questions:', dmv_questions.count())
        for q in dmv_questions[:5]:  # Show first 5
            print('- Q{}: {}...'.format(q.id, q.text[:50]))
except Exception as e:
    print('Error checking DMV questions:', e)

print("\nAll trades:")
for trade in Trade.objects.all():
    print(f"- {trade.name} (ID: {trade.id})")
