from django.urls import path

from authentication.views import (
    RegistrationAPIView, EmailVerificationView,
    ClientCreateView, GoogleAuthAPIView,
    FacebookAuthAPIView, TwitterAuthAPIView,
    LoginAPIView, PasswordResetView, ProfileView,
    AddReasonView, ClientReviewsView, ReviewDetailView,
    ReplyView, UserReviewsView, LogoutView,
    RetrieveUpdateDeleteClientView, ClientListView)

app_name = 'authentication'

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify/", EmailVerificationView.as_view(), name="verify"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('google/', GoogleAuthAPIView.as_view(), name='google'),
    path('facebook/', FacebookAuthAPIView.as_view(), name='facebook'),
    path('twitter/', TwitterAuthAPIView.as_view(), name='twitter'),
    path("client/", ClientCreateView.as_view(), name="client"),
    path("clients/", ClientListView.as_view(), name="clients"),
    path("client/<int:id>/", RetrieveUpdateDeleteClientView.as_view(),
         name="list-company"),
    path(
        "password-reset/", PasswordResetView.as_view(),
        name="password-reset"),
    path("admin/notes/", AddReasonView.as_view(), name='add-notes'),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('<int:client_id>/reviews/',
         ClientReviewsView.as_view(), name='add-reviews'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(),
         name='manage-reviews'),
    path('<int:client_id>/reviews/',
         ClientReviewsView.as_view(), name='add-reviews'),
    path(
        'reviews/<int:pk>/',
        ReviewDetailView.as_view(), name='manage-reviews'),
    path('<int:pk>/reply/', ReplyView.as_view(), name='replies'),
    path('reviewer/<int:reviewer_id>/',
         UserReviewsView.as_view(), name='user-reviews'),
    path('logout/', LogoutView.as_view(), name='logout')
]
