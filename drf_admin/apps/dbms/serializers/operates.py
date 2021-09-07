from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from dbms.models import Sqlscripts, OperateLogs


class SqlscriptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sqlscripts
        fields = "__all__"

    type_choices = (
        (1, "sql"),
        (2, "shell")
    )
    name = serializers.CharField(max_length=50, allow_null=False)
    content = serializers.FileField()
    type = serializers.ChoiceField(choices=Sqlscripts.type_choices, allow_blank=False)
    creator = serializers.CharField(max_length=20)

    def validate(self, attrs):
        if not all([attrs["name"], attrs["content"]]):
            raise ValidationError({"detail": "存在为空的字段"})
        if attrs["type"] not in [1, 2]:
            raise ValidationError({"detail": "类型错误"})
        return attrs

    def create(self, validated_data):
        ret = Sqlscripts.objects.create(**validated_data)
        return ret

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.type = validated_data["type"]
        instance.content = validated_data["content"]
        instance.creator = validated_data["creator"]
        instance.save()
        return instance


class OperateLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperateLogs
        fields = "__all__"

    env = serializers.CharField(max_length=20)
    db_name = serializers.CharField(max_length=50)
    operate_sql = serializers.CharField()
    performer = serializers.CharField(max_length=20)
    create_time = serializers.DateTimeField(read_only=True)
    status = serializers.IntegerField()
    error_info = serializers.CharField(max_length=255, allow_blank=True)
    sprint = serializers.CharField(max_length=50, default=None, allow_blank=True, allow_null=True)
