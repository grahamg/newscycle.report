from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SubscriptionForm
from .models import UserSubscription, RSSFeed

@login_required
def subscriptions(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_feeds = form.cleaned_data['feeds']
            user = request.user
            # Remove existing subscriptions
            UserSubscription.objects.filter(user=user).delete()
            # Create new subscriptions
            for feed in selected_feeds:
                UserSubscription.objects.create(user=user, feed=feed)
            messages.success(request, 'Your feed subscriptions have been updated.')
            return redirect('index')
    else:
        # Pre-select feeds the user is already subscribed to
        user_feeds = UserSubscription.objects.filter(user=request.user).values_list('feed', flat=True)
        form = SubscriptionForm(initial={'feeds': user_feeds})

    return render(request, 'subscriptions.html', {'form': form})
