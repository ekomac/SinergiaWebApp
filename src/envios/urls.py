# from django.urls import path
# from .views import (

# )

# app_name = 'orders'
# urlpatterns = [

#     # Order
#     path('create/', OrderCreateView.as_view(), name='order-create'),
#     path('<int:id>/', get_order_detail_view, name='order-detail'),
#     path('<int:id>/update/', OrderUpdateView.as_view(), name='order-update'),
#     path('<int:id>/delete/', OrderDeleteView.as_view(), name='order-delete'),
#     # Generate pdf report
#     path('<int:id>/print', generate_pdf_report, name="pdf-report"),

#     # Items
#     path('<int:id>/add-item/', ItemCreateView.as_view(),
#          name='order-add-item'),
#     path('<int:id>/delete-item/<int:item>', ItemDeleteView.as_view(),
#          name='order-delete-item'),
#     path('<int:id>/update-item/<int:item>', ItemUpdateView.as_view(),
#          name='order-update-item'),

#     # Fabrics
#     path('<int:id>/add-fabric/', FabricCreateView.as_view(),
#          name='order-add-fabric'),
#     path('<int:id>/delete-fabric/<int:fabric>', FabricDeleteView.as_view(),
#          name='order-delete-fabric'),
#     path('<int:id>/update-fabric/<int:fabric>', FabricUpdateView.as_view(),
#          name='order-update-fabric'),

#     # Payments
#     path('<int:id>/add-payment/', PaymentCreateView.as_view(),
#          name='order-add-payment'),
#     path('<int:id>/delete-payment/<int:payment>', PaymentDeleteView.as_view(),
#          name='order-delete-payment'),
#     path('<int:id>/update-payment/<int:payment>', PaymentUpdateView.as_view(),
#          name='order-update-payment'),


# ]
