from backend import detect_genres

def test_one_genre():
    detect_genres("I like Action"),["Action"]

def test_multiple_genres():
    detect_genres("I like Action and Mystery"),["Action","Mystery"]

def test_no_genres():
    detect_genres("I like Interesting shows"),[]

