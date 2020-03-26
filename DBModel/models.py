from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from django.utils import timezone


class User(models.Model):
	email = models.EmailField(null=False, primary_key=True, unique=True)
	password = models.CharField(max_length=128)
	nickname = models.CharField(max_length=20)
	score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)


class Problem(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50, default="")
	theme = models.CharField(validators=[validate_comma_separated_integer_list], max_length=100, blank=True, default="")
	description = models.TextField(blank=True, default="")
	author = models.CharField(max_length=20, blank=True, default="anonymity")
	score = models.IntegerField(default=20)
	averageScore = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	answer = models.CharField(validators=[validate_comma_separated_integer_list], max_length=255, default="")
	file = models.FileField(upload_to='data', default="")


class Submission(models.Model):
	runId = models.AutoField(primary_key=True, default=10001)
	submitTime = models.DateTimeField(default=timezone.now)
	judgeStatus = models.BooleanField(default='0')
	proId = models.IntegerField(default=1000)
	author = models.CharField(max_length=20, default='')
	score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
