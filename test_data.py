from app import create_app, db
from app.models.test import Test, TestSection, Question, Answer, WritingCriteria
from datetime import datetime

def create_test_data():
    # Créer l'application et le contexte
    app = create_app()
    with app.app_context():
        # Créer un test
        test = Test(
            title="Test de niveau d'anglais",
            description="Test pour évaluer votre niveau d'anglais",
            level="B2",
            test_type="mixed",
            duration=60,
            is_active=True,
            user_role="client"
        )
        db.session.add(test)
        db.session.flush()

        # Créer une section QCM
        qcm_section = TestSection(
            test_id=test.id,
            title="Compréhension écrite",
            section_type="qcm",
            order=1,
            content="Répondez aux questions suivantes..."
        )
        db.session.add(qcm_section)
        db.session.flush()

        # Créer des questions QCM
        questions_data = [
            {
                "text": "What is the capital of France?",
                "answers": [
                    ("Paris", True),
                    ("London", False),
                    ("Berlin", False),
                    ("Madrid", False)
                ]
            },
            {
                "text": "Which of these is not a programming language?",
                "answers": [
                    ("Python", False),
                    ("Java", False),
                    ("Cobra", True),
                    ("Ruby", False)
                ]
            }
        ]

        for q_data in questions_data:
            question = Question(
                test_id=test.id,
                section_id=qcm_section.id,
                question_text=q_data["text"],
                question_type="qcm",
                points=10
            )
            db.session.add(question)
            db.session.flush()

            for ans_text, is_correct in q_data["answers"]:
                answer = Answer(
                    question_id=question.id,
                    answer_text=ans_text,
                    is_correct=is_correct
                )
                db.session.add(answer)

        # Créer une section d'écriture
        writing_section = TestSection(
            test_id=test.id,
            title="Expression écrite",
            section_type="writing",
            order=2,
            content="Rédigez un texte de 200-250 mots sur le sujet suivant..."
        )
        db.session.add(writing_section)
        db.session.flush()

        # Créer des critères d'évaluation pour l'écriture
        criteria = [
            ("Grammaire", "Utilisation correcte des structures grammaticales"),
            ("Vocabulaire", "Richesse et précision du vocabulaire"),
            ("Cohérence", "Organisation logique des idées"),
            ("Pertinence", "Adéquation avec le sujet demandé")
        ]

        for name, desc in criteria:
            criterion = WritingCriteria(
                section_id=writing_section.id,
                name=name,
                description=desc,
                max_points=25
            )
            db.session.add(criterion)

        # Sauvegarder tous les changements
        db.session.commit()
        print("Données de test créées avec succès!")

if __name__ == "__main__":
    create_test_data() 