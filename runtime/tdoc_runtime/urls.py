"""HYB-01 process-health only. No documentary commands or public API."""
from django.http import JsonResponse
from django.urls import path
from tdoc_runtime.kernel import kernel_probe

def health(_request):
    return JsonResponse({"service": "baobab-trade-docs", "phase": "HYB-01", "provider_active": False, "kernel": kernel_probe()})

urlpatterns = [path("_internal/health", health)]
