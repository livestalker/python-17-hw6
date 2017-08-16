# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

from .forms import AskQuestionForm, AnswerForm
from .models import Question, Tag


class QuestionList(ListView):
    template_name = 'index.html'
    model = Question
    context_object_name = 'questions'

    def get_ordering(self):
        order = self.request.GET.get('order', 'created')
        # TODO if field name does not exists
        return '-' + order


class AskQuestionView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    # TODO remove query string ?next

    def get(self, request, *args, **kwargs):
        form = AskQuestionForm()
        return render(request, 'ask.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question = Question()
            question.title = form.cleaned_data.get('title')
            question.content = form.cleaned_data.get('content')
            question.author = request.user
            question.slug = slugify(question.title)
            question.save()
            for word in form.cleaned_data.get('tags'):
                # TODO if tag exist
                tag = Tag(word=word)
                tag.save()
                question.tags.add(tag)
            question.save()
            return redirect('index')
        return render(request, 'ask.html', {'form': form})


class QuestionView(View):
    @method_decorator(login_required)
    def get(self, request, *argc, **kwargs):
        slug = kwargs.get('slug')
        question = get_object_or_404(Question, slug=slug)
        answers = question.answers.all()
        form = AnswerForm()
        return render(request, 'question.html', {
            'question': question,
            'answers': answers,
            'form': form
        })

    def post(self, request, *argc, **kwargs):
        slug = kwargs.get('slug')
        question = get_object_or_404(Question, slug=slug)
        answers = question.answers.all()
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
        return render(request, 'question.html', {
            'question': question,
            'answers': answers,
            'form': form
        })
