from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from dbms.models import Sqlscripts, SqlOperationLog, DBServerConfig


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


class SqlOperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SqlOperationLog
        fields = "__all__"

    environment = serializers.CharField(max_length=20)
    database_name = serializers.CharField(max_length=50)
    operational_data = serializers.CharField()
    user = serializers.CharField(max_length=20)
    create_time = serializers.DateTimeField(read_only=True)
    status = serializers.IntegerField()
    error_info = serializers.CharField(max_length=255, default="Null")


class DBServerConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBServerConfig
        fields = "__all__"

    env_type_choice = (
        (0, "生产"),
        (1, "测试"),
        (2, "开发"),
        (3, "演示"),
        (4, "验收")
    )
    database_type_choice = (
        (0, "mysql"),
        (1, "sqlserver")
    )
    # client_name = serializers.CharField(max_length=50)
    db_env = serializers.CharField()
    db_ip = serializers.CharField(max_length=50)
    db_type = serializers.CharField(max_length=50)
    db_version = serializers.CharField(max_length=50, allow_blank=True)
    db_mark = serializers.CharField(max_length=200, allow_blank=True)
    db_name = serializers.CharField(max_length=50)
    db_username = serializers.CharField(max_length=32)
    db_password = serializers.CharField(max_length=128)
    db_port = serializers.CharField()
    create_user = serializers.CharField(max_length=20)

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     ret["db_env"] = instance.get_db_env_display()
    #     ret["db_type"] = instance.get_db_type_display()
    #     # ret['password'] = instance.get_password_display('password')  # 会显密码
    #     return ret

    def update(self, instance, validated_data):
        if "db_password" in validated_data:
            if instance.db_password == validated_data["db_password"]:
                instance.db_password = instance.get_password_display('db_password')
            else:
                instance.db_password = validated_data.get('db_password',instance.db_password)
        # instance.client_name = validated_data.get('client_name', instance.client_name)
        instance.db_env = validated_data.get('db_env', instance.db_env)
        instance.db_ip = validated_data.get('db_ip', instance.db_ip)
        instance.db_type = validated_data.get('db_type', instance.db_type)
        instance.db_version = validated_data.get('db_version', instance.db_version)
        instance.db_mark = validated_data.get('db_mark', instance.db_mark)
        instance.db_name = validated_data.get('db_name', instance.db_name)
        instance.db_username = validated_data.get('db_username', instance.db_username)
        instance.db_port = validated_data.get('db_port', instance.db_port)
        instance.create_user = validated_data.get('create_user', instance.create_user)
        instance.save()
        return instance

