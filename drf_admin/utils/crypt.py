# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : crypt.py
@create   : 2022/8/5 16:55
"""
import base64
from Crypto.Cipher import AES
from django.conf import settings


class BasePassword(object):
    """需要密码加解密的类"""
    @staticmethod
    def encrypt(row_password: str):
        """
        AES 加密登录密码
        :param row_password: 原明文密码
        :return: AES加密后密码
        """
        aes = AES.new(str.encode(settings.SECRET_KEY[4:20]), AES.MODE_ECB)
        bytes_row_password = str.encode(row_password)
        while len(bytes_row_password) % 16 != 0:
            bytes_row_password = bytes_row_password + b'\0'
        return str(base64.encodebytes(aes.encrypt(bytes_row_password)), encoding='utf8').replace('\n', '')

    def set_password(self, field_name, field_value):
        """加密密码并保存实例"""
        self.__setattr__(field_name, self.encrypt(field_value))

    def get_password_display(self, field_name):
        """
        AES 解密登录密码
        :return: 原明文密码
        """
        aes = AES.new(str.encode(settings.SECRET_KEY[4:20]), AES.MODE_ECB)
        return str(aes.decrypt(base64.decodebytes(bytes(field_name, encoding='utf8'))).rstrip(b'\0').decode("utf8"))
