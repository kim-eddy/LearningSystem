def analyze_student_performance(assessment, submitted_answers):
    """
    Compare submitted answers to correct ones, and return a dict of topic_id: score_percent.
    """
    correct_answers = assessment.answer.split(',')
    questions = assessment.questions.split('|')  
    topic_ids = [assessment.topic.id] * len(questions)  # If all questions are from one topic

    # If you have per-question topics, replace the above with the correct mapping

    topic_stats = {}
    for i, submitted in enumerate(submitted_answers):
        topic_id = topic_ids[i]
        is_correct = (
            i < len(correct_answers) and
            submitted.strip().lower() == correct_answers[i].strip().lower()
        )
        if topic_id not in topic_stats:
            topic_stats[topic_id] = {'correct': 0, 'total': 0}
        topic_stats[topic_id]['total'] += 1
        if is_correct:
            topic_stats[topic_id]['correct'] += 1

    # Calculate percent correct per topic
    topic_scores = {}
    for topic_id, stats in topic_stats.items():
        topic_scores[topic_id] = stats['correct'] / stats['total'] if stats['total'] else 0.0

    return topic_scores  # {topic_id: percent_correct, ...}
