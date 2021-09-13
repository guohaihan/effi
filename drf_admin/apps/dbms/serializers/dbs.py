from rest_framework import serializers
from dbms.models import DBServerConfig


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
    db_version = serializers.CharField(max_length=50, allow_blank=True, default=None, allow_null=True)
    db_mark = serializers.CharField(max_length=200, allow_blank=True, default=None, allow_null=True)
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

