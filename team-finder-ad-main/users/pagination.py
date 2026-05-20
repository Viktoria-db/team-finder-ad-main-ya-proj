from django.core.paginator import Paginator


def paginate_queryset(queryset, request, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def build_query_prefix(request, exclude=None):
    exclude = exclude or ("page",)
    parts = []
    for key, value in request.GET.items():
        if key in exclude or not value:
            continue
        parts.append(f"{key}={value}&")
    return "".join(parts)
