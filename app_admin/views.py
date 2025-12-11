from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from travelers.models import TravelerProfile
from agency.models import AgencyProfile
from .models import Grievance,Destination
from .forms import AddAdminForm,DestinationForm
from travelers.forms  import TravelerRegisterForm
from agency.forms import AgencyRegisterForm
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User=get_user_model()

@login_required
def app_admin_dashboard(request):
    travelers = TravelerProfile.objects.select_related('user')
    agencies = AgencyProfile.objects.select_related('user')
    grievances = Grievance.objects.all().order_by('-id')
    destinations = Destination.objects.all()  # 👈 Add this line
    pending_count = Grievance.objects.filter(resolved=False).count()

    return render(request, 'app_admin/dashboard.html', {
        'travelers': travelers,
        'agencies': agencies,
        'grievances': grievances,
        'destinations': destinations,
        'pending_count': pending_count,  # 👈 Pass to template
    })



def is_app_admin(user):
    return user.is_authenticated and user.is_app_admin

# @user_passes_test(lambda u: u.is_authenticated and u.is_app_admin)
@login_required
def add_app_admin(request):
    if request.method == 'POST':
        form = AddAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app_admin_dashboard')
    else:
        form = AddAdminForm()
    return render(request, 'app_admin/add_admin.html', {'form': form})


def add_traveler(request):
    if request.method == 'POST':
        form = TravelerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_traveler = True
            user.save()
            # Create traveler profile
            TravelerProfile.objects.create(user=user)
            return redirect('app_admin_dashboard')
    else:
        form = TravelerRegisterForm()
    return render(request, 'travelers/register.html', {'form': form})

def add_agency(request):
    if request.method == 'POST':
        form = AgencyRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_agency = True
            user.save()
            # Create agency profile
            AgencyProfile.objects.create(user=user)
            return redirect('app_admin_dashboard')
    else:
        form = AgencyRegisterForm()
    return render(request, 'agency/register.html', {'form': form})

@login_required
def add_destination(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('app_admin_dashboard')
    else:
        form = DestinationForm()
    return render(request, 'app_admin/add_destination.html', {'form': form})




@login_required
def manage_destinations(request):
    destinations = Destination.objects.all()
    return render(request, 'app_admin/manage_destinations.html', {'destinations': destinations})


@login_required
def edit_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            return redirect('manage_destinations')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'app_admin/edit_destination.html', {'form': form, 'destination': destination})


@login_required
def delete_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        return redirect('manage_destinations')
    return render(request, 'app_admin/confirm_delete.html', {'destination': destination})

@login_required
def resolve_grievance(request, grievance_id):
    grievance = get_object_or_404(Grievance, id=grievance_id)
    grievance.resolved = True
    grievance.save()
    return redirect('app_admin_dashboard')

