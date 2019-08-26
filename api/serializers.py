from rest_framework import serializers
from tests.models import Test, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['answer_text']


class QuestionSerializer(serializers.ModelSerializer):

    answer_set = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['question_text', 'correct_answer', 'answer_set']


class TestSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    question_set = QuestionSerializer(many=True)
    author = serializers.CharField(read_only=True)

    class Meta:
        model = Test
        fields = '__all__'

    def create(self, validated_data):

        question_set_data = validated_data.pop('question_set')

        test = Test.objects.create(**validated_data)

        try:
            test.author = self.context['request'].user
            test.save()
        except:
            pass

        for question in question_set_data:
            answer_set_data = question.pop('answer_set')
            created_question = Question.objects.create(test=test, **question)
            for answer in answer_set_data:
                Answer.objects.create(question=created_question, answer_text=answer['answer_text'])

        return test

    def update(self, instance, validated_data):

        question_set_data = validated_data.pop('question_set')
        questions = instance.question_set.all()
        questions = list(questions)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        for question_data in question_set_data:
            answer_set_data = question_data.pop('answer_set')
            question = questions.pop(0)
            question.question_text = question_data.get('question_text', question.question_text)
            question.correct_answer = question_data.get('correct_answer', question.correct_answer)

            answers_of_instance = question.answer_set.all()

            for answer in answers_of_instance:
                answer.answer_text = answer_set_data.pop(0).get('answer_text', answer.answer_text)
                answer.save()

            question.save()

        return instance
