from django.apps import AppConfig
from django.conf import settings

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # Import signals
        import users.signals

        # Ensure Google SocialApp exists
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        site = Site.objects.get(id=settings.SITE_ID)
        if not SocialApp.objects.filter(provider='google', sites=site).exists():
            app = SocialApp.objects.create(
                provider='google',
                name='Google Login',
                client_id=settings.GOOGLE_CLIENT_ID,
            )
            app.sites.add(site)
            app.save()
