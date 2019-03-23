import simple_history

from django.contrib import admin

from ietf.review.models import (ReviewerSettings, ReviewSecretarySettings, UnavailablePeriod,
    ReviewWish, NextReviewerInTeam, ReviewRequest, ReviewTeamSettings )

class ReviewerSettingsAdmin(simple_history.admin.SimpleHistoryAdmin):
    def acronym(self, obj):
        return obj.team.acronym
    list_display = ['id', 'person', 'acronym', 'min_interval', 'filter_re', 'remind_days_before_deadline', ]
    list_filter = ["team"]
    search_fields = ["person__name"]
    ordering = ["-id"]
    raw_id_fields = ["team", "person"]

admin.site.register(ReviewerSettings, ReviewerSettingsAdmin)

class ReviewSecretarySettingsAdmin(admin.ModelAdmin):
    list_display = [u'id', 'team', 'person', 'remind_days_before_deadline', 'max_items_to_show_in_reviewer_list', 'days_to_show_in_reviewer_list']
    raw_id_fields = ['team', 'person']
admin.site.register(ReviewSecretarySettings, ReviewSecretarySettingsAdmin)

class UnavailablePeriodAdmin(admin.ModelAdmin):
    list_display = ["person", "team", "start_date", "end_date", "availability", "reason"]
    list_display_links = ["person"]
    list_filter = ["team"]
    date_hierarchy = "start_date"
    search_fields = ["person__name"]
    ordering = ["-id"]
    raw_id_fields = ["team", "person"]

admin.site.register(UnavailablePeriod, UnavailablePeriodAdmin)

class ReviewWishAdmin(admin.ModelAdmin):
    list_display = ["person", "team", "doc"]
    list_display_links = ["person"]
    list_filter = ["team"]
    search_fields = ["person__name"]
    ordering = ["-id"]
    raw_id_fields = ["team", "person", "doc"]

admin.site.register(ReviewWish, ReviewWishAdmin)

class NextReviewerInTeamAdmin(admin.ModelAdmin):
    list_display = ["team", "next_reviewer"]
    list_display_links = ["team"]
    ordering = ["team"]
    raw_id_fields = ["team", "next_reviewer"]

admin.site.register(NextReviewerInTeam, NextReviewerInTeamAdmin)

class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ["doc", "time", "type", "team", "deadline"]
    list_display_links = ["doc"]
    list_filter = ["team", "type", "state", "result"]
    ordering = ["-id"]
    raw_id_fields = ["doc", "team", "requested_by", "reviewer", "review"]
    date_hierarchy = "time"
    search_fields = ["doc__name", "reviewer__person__name"]

admin.site.register(ReviewRequest, ReviewRequestAdmin)

class ReviewTeamSettingsAdmin(admin.ModelAdmin):
    list_display = ["group", ] 
    search_fields = ["group__acronym", ]
    raw_id_fields = ["group", ]
    filter_horizontal = ["review_types", "review_results", "notify_ad_when"]

admin.site.register(ReviewTeamSettings, ReviewTeamSettingsAdmin)
