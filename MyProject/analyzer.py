def analyze_student_performance(assessment, submitted_answers):
    """
    Compare submitted answers to correct ones, and identify weak topics.
    Returns a list of weak topic IDs.
    """

    correct_answers = assessment.answer.split(',')
    questions = assessment.questions.split('|')  
    weak_topic_ids = []

    total_questions = len(correct_answers)
    threshold = 0.6  # below 60% means weak topic

    correct_count = 0
    for i, submitted in enumerate(submitted_answers):
        if i < len(correct_answers) and submitted.strip().lower() == correct_answers[i].strip().lower():
            correct_count += 1

    score_percent = correct_count / total_questions

    if score_percent < threshold:
        # Consider the entire topic weak
        weak_topic_ids.append(assessment.topic.id)

    return weak_topic_ids
