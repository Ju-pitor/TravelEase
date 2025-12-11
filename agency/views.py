from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from app_admin.models import Destination
from travelers.models import User,PackageRating
from .forms import AgencyRegisterForm, TravelpackageForm
from travelers.forms import BookingForm
from django.contrib.auth.decorators import login_required
from .models import Travelpackage,AgencyProfile,Booking,ChatMessage
from travelers.models import TravelerProfile
from django.contrib import messages


def register_agency(request):
    if request.method == 'POST':
        form = AgencyRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = AgencyRegisterForm()
    return render(request, 'agency/register.html', {'form': form})


@login_required
def agency_dashboard(request):
     # Get the agency profile of the logged-in user
    agency_profile = get_object_or_404(AgencyProfile, user=request.user)
    
    # Get packages created by this agency
    packages = Travelpackage.objects.filter(agency=agency_profile)
    destinations = set(p.destination for p in packages)
    unique_dest_count = len(destinations)

    context = {
        'agency': agency_profile,
        'packages': packages,
        "unique_dest_count": unique_dest_count,
    }
    return render(request,'agency/dashboard.html',context)

@login_required
def add_package(request):
    agency_profile = get_object_or_404(AgencyProfile, user=request.user)
    
    if request.method == 'POST':
        form = TravelpackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save(commit=False)
            package.agency = agency_profile
            package.save()
            return redirect('agency_dashboard')
    else:
        form = TravelpackageForm()
    
    return render(request, 'agency/add_package.html', {'form': form})

@login_required
def edit_package(request, package_id):
    package = get_object_or_404(Travelpackage, id=package_id, agency__user=request.user)
    if request.method == 'POST':
        form = TravelpackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            return redirect('agency_dashboard')
    else:
        form = TravelpackageForm(instance=package)
    return render(request, 'agency/edit_package.html', {'form': form})


@login_required
def delete_package(request, package_id):
    package = get_object_or_404(Travelpackage, id=package_id, agency__user=request.user)
    if request.method == 'POST':
        package.delete()
        return redirect('agency_dashboard')
    return render(request, 'agency/delete_confirm.html', {'package': package})

def destination_packages(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    packages = (
                Travelpackage.objects.filter(destination=destination)
                .annotate(avg_rating=Avg('destination__ratings__rating'))
            )

    return render(request, 'agency/destination_packages.html', {
        'destination': destination,
        'packages': packages
    })


def package_detail(request, package_id):
    package = get_object_or_404(Travelpackage, id=package_id)
    avg_rating = PackageRating.objects.filter(package=package).aggregate(Avg('rating'))['rating__avg']
    return render(request, 'agency/package_detail.html', {
        'package': package,
        'avg_rating':avg_rating or 0,
        })

def agency_detail(request, agency_id):
    agency = get_object_or_404(AgencyProfile, id=agency_id)
    return render(request, 'agency/agency_detail.html', {'agency': agency})


@login_required
def manage_bookings(request):
    agency = AgencyProfile.objects.get(user=request.user)
    bookings = Booking.objects.filter(
        package__agency=agency,
    ).exclude(status__in=['Completed', 'Rejected']) 
    return render(request, 'agency/manage_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id, package__agency__user=request.user)
    if action.lower() == 'confirm':
        booking.status = 'Confirmed'
        message="booking confirmed successfully."
    elif action.lower() == 'reject':
        booking.status = 'Rejected'
        booking.rejected_at = timezone.now()
        message="booking rejected successfully."
    else:
        messages.error(request,"Invalid action")
        return redirect('manage_bookings')
    
    booking.save()
    messages.success(request,message)
    return redirect('manage_bookings')


@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    messages = ChatMessage.objects.filter(booking=booking).order_by('timestamp')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text.strip():
            ChatMessage.objects.create(
                booking=booking,
                sender=request.user,
                message=message_text
            )
        return redirect('chat', booking_id=booking.id)

    return render(request, 'chat.html', {'booking': booking, 'messages': messages})

@login_required
def agency_mark_completed(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        package__agency__user=request.user
    )

    booking.status = "Completed"
    booking.completed_at = timezone.now() 
    booking.save()

    # Notify traveler
    # notify(
    #     booking.traveler,
    #     f"Your trip: {booking.package.package_name} is completed!"
    # )

    messages.success(request, "Trip marked as completed.")
    return redirect('manage_bookings')


@login_required
def agency_view_receipt(request, id):
    booking = get_object_or_404(Booking, id=id)

    # Only the agency with this booking can view it
    if booking.agency != request.user.agencyprofile:
        messages.error(request, "Unauthorized access.")
        return redirect("agency_bookings")

    # Payment must be completed
    if booking.status != "Paid":
        messages.error(request, "Payment not completed. Receipt unavailable.")
        return redirect("agency_bookings")

    return render(request, "travelers/receipt.html", {"booking": booking})


@login_required
def agency_booking_history(request):
    history = Booking.objects.filter(
        package__agency__user=request.user,
        status__in=["Completed", "Rejected"]
    ).order_by("-completed_at", "-rejected_at")
    return render(request, "agency/history.html", {"history": history})


