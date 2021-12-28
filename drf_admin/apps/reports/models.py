from django.db import models
from drf_admin.utils.models import BaseModel
from multiselectfield import MultiSelectField
# Create your models here.


class ItemReports(BaseModel):
    type_choices = (
        (1, "教师pc端"),
        (2, "教师小程序端"),
        (3, "教师管理后台端"),
        (4, "学生pc端"),
        (5, "学生小程序端"),
        (6, "家长小程序端"),
    )
    name = models.CharField(max_length=50, unique=True, verbose_name="迭代名称")
    type = MultiSelectField(choices=type_choices, verbose_name="测试端类型")
    content = models.CharField(max_length=200, verbose_name="需求内容")
    domain_influence = models.CharField(null=True, blank=True, max_length=200, verbose_name="影响域")
    start_time = models.DateField(verbose_name="开始时间")
    end_time = models.DateField(verbose_name="上线时间")
    total_day = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="总工作日")
    rf_day = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="研发工作日")
    test_day = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="测试工作日")
    acceptance_day = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="验收工作日")
    group = models.IntegerField(verbose_name="研发组数")
    risk = models.CharField(null=True, blank=True, max_length=255, verbose_name="风险内容")
    legacy = models.CharField(null=True, blank=True, max_length=255, verbose_name="遗留问题")
    feel = models.TextField(null=True, blank=True, verbose_name="整体感受")

    class Meta:
        db_table = 'reports_item_reports'
        verbose_name = '果之迭代报告'
        verbose_name_plural = verbose_name


class Story(models.Model):
    content = models.CharField(max_length=255, verbose_name="用户故事")
    assess_length = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="评估时长")
    product_delays = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="需求导致延期")
    develop_delays = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="研发导致延期")
    smoking_by = models.BooleanField(verbose_name="冒烟是否通过")
    develop = models.CharField(max_length=50, verbose_name="研发人员")
    item_reports = models.ForeignKey("ItemReports", on_delete=models.CASCADE, verbose_name="迭代报告id")

    class Meta:
        db_table = "reports_story"
        verbose_name = "故事表"
        verbose_name_plural = verbose_name


class ToDo(models.Model):
    problem = models.CharField(max_length=255, verbose_name="问题描述")
    solution = models.CharField(blank=True, max_length=255, verbose_name="解决方案")
    principal = models.CharField(max_length=10, verbose_name="负责人")
    status = models.BooleanField(verbose_name="解决状态")
    remark = models.CharField(blank=True, max_length=255, verbose_name="备注")
    item_reports = models.ForeignKey("ItemReports", on_delete=models.CASCADE, verbose_name="迭代报告id")

    class Meta:
        db_table = "reports_to_do"
        verbose_name = "待办表"
        verbose_name_plural = verbose_name


class Score(models.Model):
    product_score = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="PM改动需求得分")
    rf_delay = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="故事交付延期得分")
    todo = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="冒烟通过率得分")
    unit_bug = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="单位bug数")
    finish_story_day = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="每天完成的故事点")
    total = models.DecimalField(default=False, max_digits=4, decimal_places=2, verbose_name="迭代得分")
    item_reports = models.OneToOneField("ItemReports", on_delete=models.CASCADE, verbose_name="迭代报告id")

    class Meta:
        db_table = "reports_score"
        verbose_name = "分值表"
        verbose_name_plural = verbose_name


class BugClass(models.Model):
    function_error = models.IntegerField(default=False, verbose_name="功能错误")
    function_optimize = models.IntegerField(default=False, verbose_name="功能优化")
    interface_optimize = models.IntegerField(default=False, verbose_name="界面优化")
    performance = models.IntegerField(default=False, verbose_name="性能优化")
    safety = models.IntegerField(default=False, verbose_name="安全问题")
    rd = models.IntegerField(default=False, verbose_name="后端bug")
    fe = models.IntegerField(default=False, verbose_name="前端bug")
    acceptance = models.CharField(blank=True, max_length=255, verbose_name="验收bug描述")
    item_reports = models.OneToOneField("ItemReports", on_delete=models.CASCADE, verbose_name="迭代报告id")

    class Meta:
        db_table = "reports_bug_class"
        verbose_name = "bug分类表"
        verbose_name_plural = verbose_name


class JiraVersion(BaseModel):
    name = models.CharField(blank=True, max_length=255, verbose_name="版本名称")
    description = models.CharField(null=True, blank=True, max_length=255, verbose_name="版本描述")
    released = models.BooleanField(blank=True, max_length=255, verbose_name="是否发布")
    start_date = models.DateField(null=True, verbose_name="开始时间")
    release_date = models.DateField(null=True, verbose_name="发布时间")

    class Meta:
        db_table = "reports_jira_version"
        verbose_name = "jira版本表"
        verbose_name_plural = verbose_name
