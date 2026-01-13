"""
Seed data for scenarios and sample students
"""
from database import Database

def seed_scenarios(db):
    """Add sample case study scenarios"""
    scenarios = [
        {
            'title': 'Customer Churn Prediction',
            'description': 'A telecommunications company wants to predict which customers are likely to cancel their service. You have historical data including usage patterns, customer service interactions, and demographics. Discuss how you would approach this problem, what models you might use, and what evaluation metrics are most important.',
            'category': 'Machine Learning',
            'difficulty': 'medium'
        },
        {
            'title': 'Image Classification Bias',
            'description': 'You built an image classification model that performs well overall (92% accuracy), but you discover it has significantly lower accuracy (75%) for certain demographic groups. Explain what might cause this, how you would investigate it, and what steps you would take to address it.',
            'category': 'AI Ethics',
            'difficulty': 'hard'
        },
        {
            'title': 'Real-time Fraud Detection',
            'description': 'Design a system to detect fraudulent credit card transactions in real-time. Consider the trade-offs between false positives and false negatives, latency requirements, and how you would handle concept drift as fraud patterns change over time.',
            'category': 'Machine Learning',
            'difficulty': 'hard'
        },
        {
            'title': 'A/B Test Analysis',
            'description': 'Your company ran an A/B test on a new website feature. Version A had 10,000 visitors with 800 conversions, Version B had 10,000 visitors with 850 conversions. Explain how you would determine if this difference is statistically significant and what factors you would consider before recommending a rollout.',
            'category': 'Statistics',
            'difficulty': 'easy'
        },
        {
            'title': 'Recommendation System Cold Start',
            'description': 'You are building a recommendation system for a music streaming service. Explain how you would handle the "cold start" problem for new users who have no listening history. What alternative data sources or strategies could you use?',
            'category': 'Machine Learning',
            'difficulty': 'medium'
        },
        {
            'title': 'Model Performance Degradation',
            'description': 'A production model that was achieving 85% accuracy six months ago is now performing at 70%. What could cause this degradation? How would you investigate the issue, and what solutions might you implement?',
            'category': 'MLOps',
            'difficulty': 'medium'
        },
        {
            'title': 'Time Series Forecasting',
            'description': 'You need to forecast daily sales for a retail store. The data shows weekly seasonality, holiday effects, and trends. Compare different approaches (ARIMA, Prophet, LSTM) and explain when you would use each one.',
            'category': 'Machine Learning',
            'difficulty': 'hard'
        },
        {
            'title': 'Feature Engineering',
            'description': 'You have a dataset with customer transaction data (date, amount, merchant category). You want to predict whether a customer will make a purchase next month. What features would you engineer from this raw data and why?',
            'category': 'Machine Learning',
            'difficulty': 'easy'
        },
        {
            'title': 'Model Interpretability',
            'description': 'A bank uses a machine learning model to approve or deny loan applications. Regulators require that decisions be explainable to customers. Compare different approaches to model interpretability (LIME, SHAP, etc.) and discuss the trade-offs.',
            'category': 'AI Ethics',
            'difficulty': 'medium'
        },
        {
            'title': 'Imbalanced Dataset',
            'description': 'You are building a medical diagnosis model where only 2% of cases are positive for a rare disease. Discuss the challenges this creates, evaluation metrics you would use, and techniques to handle the imbalance.',
            'category': 'Machine Learning',
            'difficulty': 'medium'
        }
    ]

    for scenario in scenarios:
        try:
            db.add_scenario(**scenario)
            print(f"Added scenario: {scenario['title']}")
        except Exception as e:
            print(f"Error adding scenario {scenario['title']}: {e}")


def seed_students(db):
    """Add sample students"""
    students = [
        {
            'student_id': 'S001',
            'name': 'Alice Chen',
            'email': 'alice.chen@university.edu',
            'project_title': 'Predicting Student Success Using Machine Learning',
            'project_description': 'Built a random forest classifier to predict student performance based on demographic and behavioral data. Achieved 83% accuracy using cross-validation.'
        },
        {
            'student_id': 'S002',
            'name': 'Bob Martinez',
            'email': 'bob.martinez@university.edu',
            'project_title': 'Sentiment Analysis of Social Media Posts',
            'project_description': 'Developed a BERT-based sentiment classifier for Twitter data. Compared performance with traditional approaches like Naive Bayes and SVM.'
        },
        {
            'student_id': 'S003',
            'name': 'Carol Williams',
            'email': 'carol.williams@university.edu',
            'project_title': 'Time Series Forecasting for Energy Consumption',
            'project_description': 'Applied LSTM networks and Prophet to forecast hourly electricity demand. Evaluated different window sizes and seasonality components.'
        }
    ]

    for student in students:
        try:
            db.add_student(**student)
            print(f"Added student: {student['name']}")
        except Exception as e:
            print(f"Error adding student {student['name']}: {e}")


if __name__ == '__main__':
    db = Database()
    print("Seeding scenarios...")
    seed_scenarios(db)
    print("\nSeeding students...")
    seed_students(db)
    print("\nSeeding complete!")
