# Generated by Django 2.2.17 on 2020-11-18 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0020_add_rescheduled_session_name'),
    ]

    def up(apps, schema_editor):
        DraftSubmissionStateName = apps.get_model('name', 'DraftSubmissionStateName')
        new_state_name = DraftSubmissionStateName.objects.create(
            slug='ad-appr',
            name='Awaiting AD Approval', 
            used=True,
        )
        new_state_name.next_states.add(DraftSubmissionStateName.objects.get(slug='posted'))
        new_state_name.next_states.add(DraftSubmissionStateName.objects.get(slug='cancel'))
        DraftSubmissionStateName.objects.get(slug='uploaded').next_states.add(new_state_name)

        # Order so the '-appr' states are together
        for slug, order in (
            ('confirmed', 0),
            ('uploaded', 1),
            ('auth', 2),
            ('aut-appr', 3),
            ('grp-appr', 4),
            ('ad-appr', 5),
            ('manual', 6),
            ('cancel', 7),
            ('posted', 8),
            ('waiting-for-draft', 9),
        ):
            state_name = DraftSubmissionStateName.objects.get(slug=slug)
            state_name.order = order
            state_name.save()

    def down(apps, schema_editor):
        DraftSubmissionStateName = apps.get_model('name', 'DraftSubmissionStateName')
        Submission = apps.get_model('submit', 'Submission')
        
        name_to_delete = DraftSubmissionStateName.objects.get(slug='ad-appr')
        
        # Refuse to migrate if there are any Submissions using the state we're about to remove
        assert(Submission.objects.filter(state=name_to_delete).count() == 0)
        
        DraftSubmissionStateName.objects.get(slug='uploaded').next_states.remove(name_to_delete)
        name_to_delete.delete()

        # restore original order
        for slug, order in (
            ('confirmed', 0),
            ('uploaded', 1),
            ('auth', 2),
            ('aut-appr', 3),
            ('grp-appr', 4),
            ('manual', 5),
            ('cancel', 6),
            ('posted', 7),
            ('waiting-for-draft', 8),
        ):
            state_name = DraftSubmissionStateName.objects.get(slug=slug)
            state_name.order = order
            state_name.save()

    operations = [
        migrations.RunPython(up, down),
    ]
