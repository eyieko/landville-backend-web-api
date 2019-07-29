from django.urls import reverse
ACCOUNT_DETAIL_URL = reverse("transactions:all-accounts")
# url to access the GET transactions endpoint
USER_TRANSACTIONS_URL = reverse("transactions:transactions")
