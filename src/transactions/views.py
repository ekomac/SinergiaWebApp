from django.shortcuts import render


def transaction_list_view(request):
    context = {}
    context['selected_tab'] = "transactions-tab"
    return render(request, "transactions/list.html", context)


def transaction_create_view(request):
    return render(request, "", {})


def transaction_edit_view(request):
    return render(request, "", {})


def transaction_detail_view(request):
    return render(request, "", {})


def transaction_delete_view(request):
    return render(request, "", {})
