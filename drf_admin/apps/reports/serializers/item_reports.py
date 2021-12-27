# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : item_reports.py
@create   : 2021/12/2 10:58
"""
from rest_framework import serializers, fields
from drf_admin.utils.serializers import MyBaseSerializer
from reports.models import ItemReports, Story, ToDo, Score, BugClass


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = ['item_reports']


class ToDoSerializer(serializers.ModelSerializer):
    item_reports = serializers.CharField(required=False)
    item_reports_id = serializers.CharField(required=False)

    class Meta:
        model = ToDo
        fields = "__all__"


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        exclude = ['item_reports']


class BugClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugClass
        exclude = ['item_reports']


class ItemReportsSerializer(MyBaseSerializer):
    type_choices = (
        (1, "教师pc端"),
        (2, "教师小程序端"),
        (3, "教师管理后台端"),
        (4, "学生pc端"),
        (5, "学生小程序端"),
        (6, "家长小程序端"),
    )
    type = fields.MultipleChoiceField(choices=type_choices)
    stories = StorySerializer(many=True, write_only=True)
    todos = ToDoSerializer(many=True, write_only=True)
    scores = ScoreSerializer(many=True, write_only=True)
    bug_classes = BugClassSerializer(many=True, write_only=True)

    class Meta:
        model = ItemReports
        fields = "__all__"

    def create(self, validated_data):
        stories_data = validated_data.pop("stories")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classes_data = validated_data.pop("bug_classes")
        item_report = ItemReports.objects.create(**validated_data)

        if stories_data:
            for story_data in stories_data:
                Story.objects.create(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                ToDo.objects.create(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                Score.objects.create(item_reports=item_report, **score_data)

        if bug_classes_data:
            for bug_class_data in bug_classes_data:
                BugClass.objects.create(item_reports=item_report, **bug_class_data)

        return item_report

    def update(self, instance, validated_data):
        stories_data = validated_data.pop("stories")
        todos_data = validated_data.pop("todos")
        scores_data = validated_data.pop("scores")
        bug_classes_data = validated_data.pop("bug_classes")
        item_report = super().update(instance, validated_data)

        # 删除要更新报告之前的故事和待办
        Story.objects.filter(item_reports=item_report).delete()
        ToDo.objects.filter(item_reports=item_report).delete()

        if stories_data:
            for story_data in stories_data:
                Story.objects.create(item_reports=item_report, **story_data)

        if todos_data:
            for todo_data in todos_data:
                if "item_reports_id" in todo_data:
                    if todo_data["item_reports_id"] and todo_data["item_reports_id"] != item_report.id:
                        ToDo.objects.filter(item_reports_id=todo_data["item_reports_id"]).update(**todo_data)
                    else:
                        ToDo.objects.create(item_reports=item_report, **todo_data)
                else:
                    ToDo.objects.create(item_reports=item_report, **todo_data)

        if scores_data:
            for score_data in scores_data:
                Score.objects.filter(item_reports=instance, item_reports_id=instance.id).update(**score_data)

        if bug_classes_data:
            for bug_class_data in bug_classes_data:
                BugClass.objects.filter(item_reports=instance, item_reports_id=instance.id).update(**bug_class_data)

        return instance

    # to_representation用于序列化返回时，添加字段
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["stories"] = Story.objects.filter(item_reports=instance.id).values()
        ret["todos"] = ToDo.objects.filter(item_reports=instance.id).values()
        ret["scores"] = Score.objects.filter(item_reports=instance.id).values()
        ret["bug_classes"] = BugClass.objects.filter(item_reports=instance.id).values()
        ret["todo_unsolved"] = ToDo.objects.filter(status=False).values()  # 返回未解决的待办
        return ret
