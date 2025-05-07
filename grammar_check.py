from textblob import TextBlob

def grammar_score(text):
    blob = TextBlob(text)
    corrected_text = blob.correct()
    mistakes = []

    for word, correct_word in zip(blob.words, corrected_text.words):
        if word.lower() != correct_word.lower():
            mistakes.append((word, correct_word))

    score = (1 - len(mistakes) / len(blob.words)) * 100 if len(blob.words) > 0 else 0
    return round(score, 2), mistakes, str(corrected_text)

