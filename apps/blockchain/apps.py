from django.apps import AppConfig


class BlockchainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blockchain'

    def ready(self):
        # Import signals to ensure they are registered
        try:
            import apps.blockchain.signals  # noqa: F401
        except Exception:
            # avoid crashing on import during certain management commands
            pass
