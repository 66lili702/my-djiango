from django.db import models

# Create your models here.
# from django.db import models


class LianJiaHouse(models.Model):
    # 基本信息（从爬虫代码中提取的字段）
    title = models.CharField('房源标题', max_length=200)
    total_price = models.FloatField('总价(万元)')
    unit_price = models.FloatField('单价(元/平米)')
    district = models.CharField('区域', max_length=50)
    area = models.FloatField('面积(平米)')
    layout = models.CharField('户型', max_length=20)

    # 从爬虫代码中提取的其他字段
    xiaoqu = models.CharField('小区', max_length=100, blank=True)
    floor = models.CharField('楼层', max_length=20, blank=True)
    orientation = models.CharField('朝向', max_length=10, blank=True)
    description = models.TextField('描述', blank=True)
    pic_url = models.URLField('图片链接', max_length=500, blank=True)

    # 系统字段
    crawl_time = models.DateTimeField('爬取时间', auto_now_add=True)
    source_url = models.URLField('源链接', max_length=500, blank=True)
    city = models.CharField('城市', max_length=20, default='北京')

    def __str__(self):
        return f"{self.title} - {self.total_price}万"

    class Meta:
        verbose_name = '链家房源'
        verbose_name_plural = '链家房源'
        db_table = 'lianjia_house'  # 指定MySQL表名
        indexes = [
            models.Index(fields=['district']),
            models.Index(fields=['unit_price']),
        ]