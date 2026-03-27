import traceback
import logging
from .models import AuditLog, SystemError

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, description, level='INFO', extra_data=None, obj=None):
    from django.contrib.contenttypes.models import ContentType
    try:
        ct = None
        obj_id = None
        if obj:
            ct = ContentType.objects.get_for_model(obj)
            obj_id = obj.pk

        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            level=level,
            description=description,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
            endpoint=request.path,
            method=request.method,
            extra_data=extra_data or {},
            content_type=ct,
            object_id=obj_id,
        )
    except Exception as e:
        logger.error(f"Erreur log_action: {e}")


class AuditMiddleware:
    """Middleware qui capture les erreurs 5xx et les enregistre"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 500:
            try:
                SystemError.objects.create(
                    error_type='HTTP_500',
                    message=f"Erreur {response.status_code} sur {request.path}",
                    endpoint=request.path,
                    method=request.method,
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=get_client_ip(request),
                    severity='high',
                )
            except Exception:
                pass
        return response

    def process_exception(self, request, exception):
        try:
            SystemError.objects.create(
                error_type=type(exception).__name__,
                message=str(exception),
                traceback=traceback.format_exc(),
                endpoint=request.path,
                method=request.method,
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request),
                severity='high',
            )
        except Exception:
            pass
        return None
