from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from django.utils import timezone


class User(models.Model):
	email = models.EmailField(null=False, primary_key=True, unique=True)
	password = models.CharField(max_length=128)
	nickname = models.CharField(max_length=20)
	score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

	@staticmethod
	def get_ranklist(ranklistVolume):
		"""
		get specified volume of ranklist
		:param ranklistVolume: volume number of ranklist
		:return: ranklist
		"""
		# TODO(tdye): need to filter some attributes of User Object like password?
		return User.objects.all().order_by('-score')[(ranklistVolume - 1) * 20: ranklistVolume * 20]

	@staticmethod
	def get_ranklist_volumes():
		"""
		get how many volumes of ranklist in total
		:return: list of volumes like [1, 2, 3]
		"""
		return [(i + 1) for i in range(int(User.objects.count() / 20) + 1)]

	def signin(self):
		pass    # TODO(tdye): Object Oriented


class Problem(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50, default="")
	theme = models.CharField(validators=[validate_comma_separated_integer_list], max_length=100, blank=True, default="")
	description = models.TextField(blank=True, default="")
	author = models.CharField(max_length=20, blank=True, default="anonymity")
	score = models.IntegerField(default=20)
	averageScore = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	answer = models.CharField(validators=[validate_comma_separated_integer_list], max_length=255, default="")
	# TODO(tdye): 答案不能用逗号分开，假如答案本身就是逗号呢？

	@staticmethod
	def get_problem_list(volume):
		return Problem.objects.values('id', 'title', 'averageScore', 'score'). \
			       order_by('id')[(volume - 1) * 20: volume * 20]

	@staticmethod
	def get_problem_volumes():
		return [(i + 1) for i in range(int(Problem.objects.count() / 20) + 1)]

	@staticmethod
	def get_problem_by_id(id):
		problem = Problem.objects.values(
			'id', 'title', 'theme', 'author', 'description', 'answer', 'averageScore', 'score').filter(id=id)[0]
		problem['theme'] = problem['theme'].split(',')
		problem['blanksNums'] = [(i + 1) for i in range(len(problem['answer'].split(',')))]
		del (problem['answer'])
		return problem

	@staticmethod
	def get_problem_list_by_theme(theme, problemVolume):
		"""
		get specified them and volume problem list
		:param theme:
		:param problemVolume:
		:return:
		"""
		return Problem.objects.filter(theme__contains=theme).values('id', 'title', 'averageScore', 'score'). \
			       order_by('id')[(problemVolume - 1) * 20: problemVolume * 20]

	@staticmethod
	def get_problem_volumes_by_theme(theme):
		"""
		get specified theme problem volumes
		:param theme:
		:return: like [1, 2, ..., 10, ...]
		"""
		return [(i + 1) for i in range(int(Problem.objects.filter(theme__contains=theme).count() / 20) + 1)]

	@staticmethod
	def get_next_problem_id():
		return (Problem.objects.values('id').order_by('-id')[0])['id'] + 1


class Submission(models.Model):
	submissionId = models.AutoField(primary_key=True, default=10001)
	submitTime = models.DateTimeField(default=timezone.now)
	judgeStatus = models.BooleanField(default='0')
	proId = models.IntegerField(default=1000)
	answer = models.CharField(validators=[validate_comma_separated_integer_list], max_length=255, default="")
	author = models.CharField(max_length=20, default='')
	score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	@staticmethod
	def get_status_list(statusVolume):
		"""
		get specified volume of status list
		:param statusVolume:
		:return:
		"""
		return Submission.objects.all().order_by('-submissionId')[(statusVolume - 1) * 20: statusVolume * 20]

	@staticmethod
	def get_status_volumes():
		"""
		get how many volumes of status list in total
		:return:
		"""
		return [(i + 1) for i in range(int(Submission.objects.count() / 20) + 1)]


class Teacher(models.Model):
	email = models.EmailField(null=False, primary_key=True, unique=True)
	password = models.CharField(max_length=128)
	nickname = models.CharField(max_length=20)

	def signin(self):
		pass

	def upload(self, time, proId):
		email = self.email


class Upload(models.Model):
	email = models.EmailField()
	time = models.DateTimeField(default=timezone.now)
	proId = models.SmallIntegerField()

	class Meta:
		unique_together = ('email', 'proId')