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
        exclude = ['item_reports']


class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        exclude = ['item_reports']
        # fields = "__all__"


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        exclude = ['item_reports']


class BugClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugClass
        exclude = ['item_reports']


class ItemReportsSerializer(serializers.ModelSerializer):
    storys = StorySerializer(many=True, write_only=True)
    todos = ToDoSerializer(many=True, write_only=True)
    scores = ScoreSerializer(many=True, write_only=True)
    bug_classs = BugClassSerializer(many=True, write_only=True)

    class Meta:
        model = ItemReports
        # fields = "__all__"
        exclude = ("type",)

    def create(self, validated_data):
        storys_data = validated_data.pop("storys")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classs_data = validated_data.pop("bug_classs")
        item_report = ItemReports.objects.create(**validated_data)

        if storys_data:
            for story_data in storys_data:
                Story.objects.create(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                ToDo.objects.create(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                Score.objects.create(item_reports=item_report, **score_data)

        if bug_classs_data:
            for bug_class_data in bug_classs_data:
                BugClass.objects.create(item_reports=item_report, **bug_class_data)

        return item_report

    def update(self, instance, validated_data):
        storys_data = validated_data.pop("storys")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classs_data = validated_data.pop("bug_classs")
        item_report = super().update(instance, validated_data)

        # 删除之前的故事和待办
        Story.objects.filter(item_reports=item_report).delete()
        ToDo.objects.filter(item_reports=item_report).delete()

        if storys_data:
            for story_data in storys_data:
                Story.objects.create(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                ToDo.objects.create(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                Score.objects.filter(item_reports=instance, item_reports_id=instance.id).update(**score_data)

        if bug_classs_data:
            for bug_class_data in bug_classs_data:
                BugClass.objects.filter(item_reports=instance, item_reports_id=instance.id).update(**bug_class_data)

        return instance

    # to_representation用于序列化返回时，添加字段
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["storys"] = Story.objects.filter(item_reports=instance.id).values()
        ret["todos"] = ToDo.objects.filter(item_reports=instance.id).values()
        ret["scores"] = Score.objects.filter(item_reports=instance.id).values()
        ret["bug_classs"] = BugClass.objects.filter(item_reports=instance.id).values()
        ret["todo_unsolved"] = ToDo.objects.filter(status=False).values()  # 返回未解决的待办
        return ret
