from django.db import models
from django.utils.text import slugify

# Create your models here.
class CaseStudy(models.Model):
    title = models.TextField()
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to ='uploads/')
    content = models.TextField()
    highlight = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # 'So Marketing' becomes 'so-marketing'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"   

class OrgQuizTakers(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField()      
    consent = models.BooleanField(
        default=False,
        blank=True,
        null=True,
    )
    proceed = models.BooleanField(
        default=False,
        blank=True,
        null=True,
    )
    workplace_env = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    org_polices = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    leadership_app = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    training_and_dev = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    performance_management = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    workplace_culture = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    impact_assessment = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )
    future_planning = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Quiz Taker"
        verbose_name_plural = "Quiz Takers"
        ordering = ["-first_name"]

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"