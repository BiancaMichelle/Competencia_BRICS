from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile
from .forms import UserForm, UserProfileForm

# Restricción: solo admin puede acceder
def admin_required(user):
    return user.is_staff or user.is_superuser

@user_passes_test(admin_required)
def user_list(request):
    users = User.objects.all()
    # Asegurarse de que todos los usuarios tengan UserProfile
    for u in users:
        UserProfile.objects.get_or_create(user=u)
    return render(request, "blockchain/admin/user_list.html", {"users": users})

@user_passes_test(admin_required)
def user_detail(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    profile, created = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=target_user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:user_detail', user_id=target_user.id)
    else:
        user_form = UserForm(instance=target_user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user': target_user,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'blockchain/admin/user_detail.html', context)

@user_passes_test(admin_required)
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect("users:user_list")
