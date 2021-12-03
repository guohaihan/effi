# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : item_reports.py
@create   : 2021/12/2 10:58
"""
from rest_framework import serializers
from reports.models import ItemReports, Story, ToDo, Score, BugClass


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        # exclude = ['item_reports']
        fields = ["content", "assess_length", "product_delays", "develop_delays", "smoking_by", "rd", "fe"]
        # fields = "__all__"


class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        # exclude = ['item_reports']
        fields = ["problem", "solution", "principal", "status", "remark"]
        # fields = "__all__"


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        # exclude = ['item_reports']
        fields = ["product_score", "rf_delay", "todo", "unit_bug", "finish_story_day"]
        # fields = "__all__"


class BugClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugClass
        # exclude = ['item_reports']
        fields = ["function_error", "function_optimize", "interface_optimize", "performance", "safety", "rd", "fe"]
        # fields = "__all__"


class ItemReportsSerializer(serializers.ModelSerializer):
    storys = StorySerializer(many=True)
    todos = ToDoSerializer(many=True)
    scores = ScoreSerializer(many=True)
    bug_classs = BugClassSerializer(many=True)

    class Meta:
        model = ItemReports
        fields = "__all__"
        # exclude = ("type",)

    def create(self, validated_data):
        storys_data = validated_data.pop("storys")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classs_data = validated_data.pop("bug_classs")
        item_report = ItemReports.objects.create(**validated_data)

        if storys_data:
            for story_data in storys_data:
                # story_data["item_reports"] = item_report.id
                Story.objects.create(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                # todo_data["item_reports"] = item_report.id
                ToDo.objects.create(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                # score_data["item_reports"] = item_report.id
                Score.objects.create(item_reports=item_report, **score_data)

        if bug_classs_data:
            for bug_class_data in bug_classs_data:
                # bug_class_data["item_reports"] = item_report.id
                BugClass.objects.create(item_reports=item_report, **bug_class_data)

        return item_report

    def update(self, instance, validated_data):
        storys_data = validated_data.pop("storys")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classs_data = validated_data.pop("bug_class")
        item_report = ItemReports.objects.update(**validated_data)

        if storys_data:
            for story_data in storys_data:
                # story_data["item_reports"] = item_report.id
                Story.objects.update(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                # todo_data["item_reports"] = item_report.id
                ToDo.objects.update(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                # score_data["item_reports"] = item_report.id
                Score.objects.update(item_reports=item_report, **score_data)

        if bug_classs_data:
            for bug_class_data in bug_classs_data:
                # bug_class_data["item_reports"] = item_report.id
                BugClass.objects.update(item_reports=item_report, **bug_class_data)

        return item_report
