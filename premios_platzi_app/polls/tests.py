import datetime

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from .models import Question

class QuestionModelTests(TestCase):
    
    def test_was_published_recently_with_future_questions(self):
        """was_published_recently return False for questions whose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quién es el mejor Course Director de PLatzi?", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


def create_question(question_text, days):
    """
    Create a question with the given "question_text", and published the given
    number of days offset to now (negative for questions published in the past,
    positive for questions that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_no_future_question_are_displayed(self):
        """If there are a question published in the future, this question won't be displayed"""
        response = self.client.get(reverse("polls:index"))
        time = timezone.now() + datetime.timedelta(days = 30)
        self.assertEqual(response.status_code, 200)
        future_question = Question.objects.create(question_text="¿Mejor página de Platzi?", pub_date=time)
        self.assertNotContains(response, future_question.question_text)
    
    def test_past_question_are_displayed(self):
        """If there are a question published in the past, this question will be displayed"""
        create_question("¿Es C++ lo mejor?",-10)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No polls are available.")
    
    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past questions are displayed
        """
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertNotContains(response, future_question.question_text)
        self.assertContains(response, past_question.question_text)


    def test_two_past_questions(self):
        """
        The question index page may display multiple questions. 
        """
        past_question1 = create_question("Past 1", days=-10)
        past_question2 = create_question("Past 2", days=-20)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with pub_date in the future return a 
        404 error not found
        """
        future_question = create_question(question_text="future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past 
        displays the question's text
        """
        past_question = create_question(question_text="past question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)