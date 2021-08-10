from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from dbms.models import Sqlscripts, SqlOperationLog, Accounts


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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = "__all__"

    """服务器登录账户表"""
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
    environment = serializers.CharField()
    host = serializers.CharField(max_length=50)
    database_type = serializers.CharField(read_only=True)
    database_version = serializers.CharField(max_length=50, read_only=True)
    function = serializers.CharField(max_length=200, read_only=True)
    database_name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=64)
    port = serializers.CharField()
    create_user = serializers.CharField(max_length=20)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["environment"] = instance.get_environment_display()
        ret["database_type"] = instance.get_database_type_display()
        # ret['password'] = instance.get_password_display('password')  # 会显密码
        return ret

    def update(self, instance, validated_data):
        if "password" in validated_data:
            if instance.password == validated_data["password"]:
                instance.password = instance.get_password_display('password')
            else:
                instance.password = validated_data.get('password',instance.password)
        # instance.client_name = validated_data.get('client_name', instance.client_name)
        instance.environment = validated_data.get('environment', instance.environment)
        instance.host = validated_data.get('host', instance.host)
        instance.database_type = validated_data.get('database_type', instance.database_type)
        instance.database_version = validated_data.get('database_version', instance.database_version)
        instance.function = validated_data.get('function', instance.function)
        instance.database_name = validated_data.get('database_name', instance.database_name)
        instance.username = validated_data.get('username', instance.username)
        instance.port = validated_data.get('port', instance.port)
        instance.create_user = validated_data.get('create_user', instance.create_user)
        instance.save()
        return instance

