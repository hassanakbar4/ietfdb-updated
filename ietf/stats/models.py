from django.db import models
from ietf.meeting.models import Meeting
from ietf.name.models import CountryName
from ietf.person.models import Person


class AffiliationAlias(models.Model):
    """Records that alias should be treated as name for statistical
    purposes."""

    alias = models.CharField(max_length=255, help_text="Note that aliases will be matched case-insensitive and both before and after some clean-up.", unique=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"{} -> {}".format(self.alias, self.name)

    def save(self, *args, **kwargs):
        self.alias = self.alias.lower()
        super(AffiliationAlias, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "affiliation aliases"

class AffiliationIgnoredEnding(models.Model):
    """Records that ending should be stripped from the affiliation for statistical purposes."""

    ending = models.CharField(max_length=255, help_text="Regexp with ending, e.g. 'Inc\\.?' - remember to escape .!")

    def __unicode__(self):
        return self.ending

class CountryAlias(models.Model):
    """Records that alias should be treated as country for statistical
    purposes."""

    alias = models.CharField(max_length=255, help_text="Note that lower-case aliases are matched case-insensitive while aliases with at least one uppercase letter is matched case-sensitive. So 'United States' is best entered as 'united states' so it both matches 'United States' and 'United states' and 'UNITED STATES', whereas 'US' is best entered as 'US' so it doesn't accidentally match an ordinary word like 'us'.")
    country = models.ForeignKey(CountryName, max_length=255)

    def __unicode__(self):
        return u"{} -> {}".format(self.alias, self.country.name)

    class Meta:
        verbose_name_plural = "country aliases"
    
class MeetingRegistration(models.Model):
    """Registration attendee records from the IETF registration system"""
    meeting = models.ForeignKey(Meeting)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    affiliation = models.CharField(blank=True, max_length=255)
    country_code = models.CharField(max_length=2)        # ISO 3166
    person = models.ForeignKey(Person, blank=True, null=True)
    
    def __unicode__(self):
        return u"{} {}".format(self.first_name, self.last_name)
