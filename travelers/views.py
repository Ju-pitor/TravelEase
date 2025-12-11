from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from django.views.decorators.http import require_http_methods,require_GET
from .forms import TravelerRegisterForm,TravelPlanForm
from travelers.forms import BookingForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from app_admin.models import Grievance,Destination
from .models import TravelPlan, TravelerProfile,Wishlist,PackageRating,DestinationRating
from agency.models import Travelpackage,Booking
import random
from django.db.models import Avg
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.db.models import Q
from django.contrib.messages import get_messages

# Create your views here.
def home(request):
    destination_id = request.GET.get('destination', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    package_type = request.GET.get('type', '').strip()
    climate = request.GET.get('climate', '').strip()
    activity_type = request.GET.get('activity_type', '').strip()

    # Check if any filter is applied
    filters_applied = any([destination_id, min_price, max_price, package_type, climate, activity_type])

    # If no filters, show destination list
    if not filters_applied:
        destinations = Destination.objects.annotate(avg_rating=Avg('ratings__rating'))
        return render(request, 'home.html', {
            'destinations': destinations,
            'destinations_all': Destination.objects.all(),
        })

    # If filters exist, show filtered packages
    packages = Travelpackage.objects.all()

    if destination_id:
        packages = packages.filter(destination_id=destination_id)

    if min_price:
        packages = packages.filter(price__gte=min_price)

    if max_price:
        packages = packages.filter(price__lte=max_price)

    if package_type:
        packages = packages.filter(package_type=package_type)

    if climate:
        packages = packages.filter(climate=climate)

    if activity_type:
        packages = packages.filter(activity_type=activity_type)

    context = {
        'packages': packages,
        'destinations': Destination.objects.all(),
        'destination': destination_id,
        'min_price': min_price,
        'max_price': max_price,
        'selected_type': package_type,
        'selected_climate': climate,
        'selected_activity': activity_type,
    }

    return render(request, 'home.html', context)






def register_traveler(request):
    if request.method == 'POST':
        form = TravelerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = TravelerRegisterForm()
    return render(request, 'travelers/register.html', {'form': form})


@staff_member_required
def admin_register_traveler(request):
    """Allow staff to register a traveler using the same frontend registration template.

    This view is intended for admin/staff use only and reuses the existing
    TravelerRegisterForm and template so admins see the same form as public users.
    """
    if request.method == 'POST':
        form = TravelerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin/')
    else:
        form = TravelerRegisterForm()
    return render(request, 'travelers/register.html', {'form': form})


# common login
def common_login_view(request):
    storage = get_messages(request)
    for _ in storage:
        pass   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.is_traveler:
                return redirect('traveler_dashboard')
            elif user.is_agency:
                return redirect('agency_dashboard')
            elif user.is_app_admin:
                return redirect('app_admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


@login_required
def traveler_dashboard(request):
    traveler=request.user
    wishlist_items=Wishlist.objects.filter(traveler=traveler)
    traveler_profile = TravelerProfile.objects.get(user=request.user)
    travel_plans = TravelPlan.objects.filter(traveler=traveler_profile)
    bookings = Booking.objects.filter(traveler=request.user)
    packages = Travelpackage.objects.all()
    user_grievances = Grievance.objects.filter(user=request.user).order_by('-submitted_at')

    all_packages = list(Travelpackage.objects.all())
    random.shuffle(all_packages)
    packages = all_packages[:3]

    context= {
        'travel_plans':travel_plans,
        'wishlist_items':wishlist_items,
        'bookings': bookings,
        'packages': packages,
        'user_grievances': user_grievances,

    }

    return render(request, 'travelers/dashboard.html',context)
   




def logout_view(request):
    storage = get_messages(request)
    for _ in storage:
        pass
    
    logout(request)
    return redirect('home')


@login_required
def submit_grievance(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Grievance.objects.create(user=request.user, subject=subject, message=message)
        return redirect('traveler_dashboard')
    return render(request, 'travelers/submit_grievance.html')



# Add new travel plan
@login_required
def add_plan(request):
    traveler_profile = TravelerProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = TravelPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.traveler = traveler_profile
            plan.save()
            return redirect('traveler_dashboard')
    else:
        form = TravelPlanForm()
    return render(request, 'travelers/add_plan.html', {'form': form})

# Edit a travel plan
@login_required
def edit_plan(request, id):
    plan = get_object_or_404(TravelPlan, id=id, traveler__user=request.user)
    if request.method == 'POST':
        form = TravelPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('traveler_dashboard')
    else:
        form = TravelPlanForm(instance=plan)
    return render(request, 'travelers/edit_plan.html', {'form': form})

# Delete a travel plan
@login_required
def delete_plan(request, id):
    plan = get_object_or_404(TravelPlan, id=id, traveler__user=request.user)
    if request.method == 'POST':
        plan.delete()
        return redirect('traveler_dashboard')
    return render(request, 'travelers/confirm_delete.html', {'plan': plan})

def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    packages = Travelpackage.objects.filter(destination=destination)
    return render(request, 'destination_detail.html', {
        'destination': destination,
        'packages': packages
    })


@login_required
def traveler_bookings(request):
    bookings = Booking.objects.filter(traveler=request.user)
    return render(request, 'traveler/bookings.html', {'bookings': bookings})



@login_required
def add_to_wishlist(request, item_type, item_id):
    user = request.user

    if not hasattr(user, 'is_traveler') or not user.is_traveler:
        messages.error(request, "Only travelers can use the wishlist feature.")
        return redirect('home')

    # Create wishlist entry
    if item_type == 'destination':
        item = get_object_or_404(Destination, id=item_id)
        Wishlist.objects.get_or_create(traveler=user, destination=item)
        message = f"Added {item.name} to your wishlist!"
    elif item_type == 'package':
        item = get_object_or_404(Travelpackage, id=item_id)
        Wishlist.objects.get_or_create(traveler=user, package=item)
        message = f"Added {item.package_name} to your wishlist!"
    else:
        message = "Invalid item type."

    # If AJAX request, return JSON so client can handle without a redirect
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': message})

    # Otherwise use normal redirect + message for non-AJAX (fallback)
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, traveler=request.user)
    wishlist_item.delete()
    messages.info(request, "Removed from your wishlist.")
    return redirect('traveler_dashboard')

# travel_quizz to suggest places
# Updated questions with more options and better categorization
QUESTIONS = [
    {
        'id': 1,
        'text': "What type of weather do you prefer while traveling?",
        'options': ['Sunny beaches', 'Cold mountains', 'Rainy forests', 'Pleasant city weather', 'Desert heat', 'Mild & temperate'],
        'tags': {
            'Sunny beaches': ['beach', 'sunny', 'tropical', 'coastal', 'island'],
            'Cold mountains': ['mountain', 'cold', 'snow', 'hills', 'alpine'],
            'Rainy forests': ['forest', 'rain', 'green', 'nature', 'wildlife'],
            'Pleasant city weather': ['city', 'urban', 'pleasant', 'moderate'],
            'Desert heat': ['desert', 'hot', 'arid', 'sand'],
            'Mild & temperate': ['mild', 'temperate', 'spring', 'autumn']
        }
    },
    {
        'id': 2,
        'text': "What kind of activities do you enjoy?",
        'options': ['Adventure & hiking', 'Relaxation & spa', 'Cultural tours', 'Party & nightlife', 'Wildlife safari', 'Shopping & dining'],
        'tags': {
            'Adventure & hiking': ['adventure', 'hiking', 'trekking', 'rafting', 'biking', 'climbing'],
            'Relaxation & spa': ['relax', 'spa', 'yoga', 'meditation', 'wellness'],
            'Cultural tours': ['cultural', 'heritage', 'historical', 'museum', 'architecture'],
            'Party & nightlife': ['party', 'nightlife', 'clubbing', 'bars', 'entertainment'],
            'Wildlife safari': ['wildlife', 'safari', 'animals', 'jungle', 'nature'],
            'Shopping & dining': ['shopping', 'dining', 'food', 'restaurant', 'local cuisine']
        }
    },
    {
        'id': 3,
        'text': "What's your travel budget per person?",
        'options': ['Economy (< ₹10,000)', 'Mid-range (₹10,000 - ₹30,000)', 'Luxury (₹30,000 - ₹60,000)', 'Premium (> ₹60,000)'],
        'tags': {
            'Economy (< ₹10,000)': ['budget', 'economy', 'cheap', 'affordable'],
            'Mid-range (₹10,000 - ₹30,000)': ['midrange', 'moderate', 'standard'],
            'Luxury (₹30,000 - ₹60,000)': ['luxury', 'premium', 'deluxe', 'comfort'],
            'Premium (> ₹60,000)': ['premium', 'exclusive', 'high-end', 'luxurious']
        }
    },
    {
        'id': 4,
        'text': "Who do you prefer to travel with?",
        'options': ['Solo', 'Friends', 'Family', 'Partner', 'Group tour'],
        'tags': {
            'Solo': ['solo', 'independent', 'alone', 'self-discovery'],
            'Friends': ['friends', 'group', 'buddies', 'gang'],
            'Family': ['family', 'kids', 'children', 'parents'],
            'Partner': ['couple', 'romantic', 'honeymoon', 'partner'],
            'Group tour': ['group', 'tour', 'organized', 'guided']
        }
    },
    {
        'id': 5,
        'text': "How long is your ideal trip?",
        'options': ['Weekend getaway', '1 week', '2 weeks', 'A month or more'],
        'tags': {
            'Weekend getaway': ['weekend', 'short', 'quick', '2-3 days'],
            '1 week': ['week', '7 days', 'medium', 'extended'],
            '2 weeks': ['fortnight', '14 days', 'long', 'vacation'],
            'A month or more': ['month', 'long-term', 'extended', 'sabbatical']
        }
    },
    {
        'id': 6,
        'text': "What type of accommodation do you prefer?",
        'options': ['Budget hotel/hostel', 'Comfortable hotel', 'Luxury resort', 'Homestay/local stay'],
        'tags': {
            'Budget hotel/hostel': ['budget', 'hostel', 'cheap', 'basic'],
            'Comfortable hotel': ['hotel', 'comfort', 'standard', '3-star'],
            'Luxury resort': ['resort', 'luxury', '5-star', 'premium'],
            'Homestay/local stay': ['homestay', 'local', 'authentic', 'cultural']
        }
    },
    {
        'id': 7,
        'text': "What's your preferred pace of travel?",
        'options': ['Fast-paced (multiple places)', 'Moderate (mix of activities)', 'Slow & relaxed (one place)', 'Flexible (spontaneous)'],
        'tags': {
            'Fast-paced (multiple places)': ['fast', 'multi-city', 'exploration', 'itinerary'],
            'Moderate (mix of activities)': ['moderate', 'balanced', 'mix', 'varied'],
            'Slow & relaxed (one place)': ['slow', 'relaxed', 'chill', 'leisure'],
            'Flexible (spontaneous)': ['flexible', 'spontaneous', 'open', 'free']
        }
    }
]

@require_http_methods(["GET", "POST"])
def travel_quiz(request):
    if request.method == "POST":
        # Get all submitted answers
        submitted_answers = []
        for i in range(1, len(QUESTIONS) + 1):
            answer = request.POST.get(f'q{i}')
            if answer:
                submitted_answers.append(answer)
        
        # If no answers, redirect back
        if not submitted_answers:
            messages.warning(request, "Please answer at least one question!")
            return redirect('travel_quiz')
        
        # Start with all packages
        recommended_packages = Travelpackage.objects.all()
        
        # If we have very few packages, return them all
        if recommended_packages.count() < 5:
            return render(request, "travelers/recommendations.html", {
                "recommendations": recommended_packages,
                "answers": submitted_answers,
            })
        
        # Build a scoring system for better matching
        package_scores = {}
        
        # Process each answer and match with package attributes
        for answer in submitted_answers:
            # Find which question this answer belongs to
            for question in QUESTIONS:
                if answer in question['tags']:
                    # Get keywords for this answer
                    keywords = question['tags'][answer]
                    
                    # Score packages based on keyword matching
                    for package in recommended_packages:
                        if package.id not in package_scores:
                            package_scores[package.id] = 0
                        
                        # Check package name, destination, description, etc.
                        search_text = f"{package.package_name} {package.destination} {package.description or ''}".lower()
                        
                        # Add score for each matching keyword
                        for keyword in keywords:
                            if keyword in search_text:
                                package_scores[package.id] += 3  # High score for direct keyword match
                            elif any(kw in search_text for kw in keyword.split()):
                                package_scores[package.id] += 1  # Partial match
        
        # Budget-specific logic
        for answer in submitted_answers:
            if 'Economy' in answer:
                recommended_packages = recommended_packages.filter(price__lt=10000)
            elif 'Mid-range' in answer:
                recommended_packages = recommended_packages.filter(price__gte=10000, price__lte=30000)
            elif 'Luxury' in answer:
                recommended_packages = recommended_packages.filter(price__gt=30000, price__lte=60000)
            elif 'Premium' in answer:
                recommended_packages = recommended_packages.filter(price__gt=60000)
        
        # Weather-specific filtering
        weather_filters = Q()
        for answer in submitted_answers:
            answer_lower = answer.lower()
            if any(word in answer_lower for word in ['sunny', 'beach', 'tropical', 'coastal']):
                weather_filters |= Q(description__icontains='beach') | Q(destination__icontains='beach')
            if any(word in answer_lower for word in ['mountain', 'cold', 'snow', 'hills']):
                weather_filters |= Q(description__icontains='mountain') | Q(destination__icontains='mountain')
            if any(word in answer_lower for word in ['forest', 'rain', 'green', 'nature']):
                weather_filters |= Q(description__icontains='forest') | Q(destination__icontains='forest')
        
        if weather_filters:
            recommended_packages = recommended_packages.filter(weather_filters)
        
        # If we have scores, sort packages by score
        if package_scores:
            # Sort package IDs by score (descending)
            sorted_package_ids = sorted(package_scores.items(), key=lambda x: x[1], reverse=True)
            top_package_ids = [pid for pid, score in sorted_package_ids if score > 0][:10]  # Top 10
            
            if top_package_ids:
                # Get packages in score order
                id_order = {pid: idx for idx, pid in enumerate(top_package_ids)}
                final_packages = recommended_packages.filter(id__in=top_package_ids)
                # Convert to list and sort by the score order
                final_packages = list(final_packages)
                final_packages.sort(key=lambda x: id_order.get(x.id, 1000))
                recommended_packages = final_packages
        
        # If still no results, return some popular packages as fallback
        if not recommended_packages:
            recommended_packages = Travelpackage.objects.order_by('-rating', 'price')[:5]
        
        return render(request, "travelers/recommendations.html", {
            "recommendations": recommended_packages,
            "answers": submitted_answers,
        })

    # Pick 5 random questions (not 3) to ensure enough data for matching
    # Or use all questions but in random order
    random_questions = random.sample(QUESTIONS, min(5, len(QUESTIONS)))
    # You can also use all questions: random_questions = QUESTIONS.copy()
    # random.shuffle(random_questions)
    
    return render(request, "travelers/travel_quiz.html", {"questions": random_questions})

@login_required
def rate_package(request, id):
    package = get_object_or_404(Travelpackage, id=id)
    rating_value = int(request.POST.get('rating', 0))
    review_text = request.POST.get('review', '')

    PackageRating.objects.update_or_create(
        package=package,
        traveler=request.user,
        defaults={'rating': rating_value, 'review': review_text},
    )
    messages.success(request, "Your rating has been submitted!")
    return redirect('package_detail', package_id=package.id)


@login_required
def rate_destination(request, id):
    destination = get_object_or_404(Destination, id=id)

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review', '')

        DestinationRating.objects.update_or_create(
            destination=destination,
            traveler=request.user,
            defaults={'rating': rating_value, 'review': review_text},
        )

        messages.success(request, "Your rating has been submitted!")
    return redirect('destination_detail', pk=id)

    
@login_required
def book_package(request, package_id):
    package = get_object_or_404(Travelpackage, id=package_id)

    # ------ LIMIT: MAX 3 ACTIVE BOOKINGS ------
    active_bookings = Booking.objects.filter(
        traveler=request.user,
        status__in=['Pending', 'Confirmed']
    ).count()

    if active_bookings >= 3:
        messages.error(request, "You already have 3 active bookings. Please cancel or complete one before booking again.")
        return redirect('traveler_bookings')

    # -----------------------------------------

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            travel_date = form.cleaned_data['travel_date']
            today = timezone.now().date()

            # ------ ENFORCE: TRAVEL DATE MUST BE >= 3 DAYS AHEAD ------
            if (travel_date - today).days < 3:
                messages.error(request, "Booking must be done at least 3 days before the travel date.")
                return render(request, 'travelers/book_package.html', {"form": form, "package": package})
            # -----------------------------------------------------------

            booking = form.save(commit=False)
            booking.package = package
            booking.traveler = request.user
            booking.status = 'Pending'
            booking.save()

            messages.info(request, "Your booking request has been sent to the agency.")
            return redirect('traveler_bookings')

    else:
        form = BookingForm(initial={'package': package.id})

    return render(request, 'travelers/book_package.html', {"form": form, "package": package})



@login_required
def traveler_bookings(request):
    bookings = Booking.objects.filter(
        traveler=request.user,
        status__in=["Pending", "Confirmed", "Paid", "Checked-In"]
    )
    return render(request, 'travelers/traveler_bookings.html', {'bookings': bookings})

def view_packages(request):
    packages = Travelpackage.objects.all()
    return render(request, 'travelers/view_packages.html', {'packages': packages})


@login_required
@require_GET
def get_latest_booking_status(request):
    """
    Returns the latest booking statuses for the logged-in traveler.
    Called by AJAX to auto-update booking statuses.
    """
    bookings = Booking.objects.filter(traveler=request.user).select_related('package')
    data = [
        {
            'id': b.id,
            'package': b.package.package_name,
            'status': b.status,
            'booking_date': b.booking_date.strftime("%Y-%m-%d %H:%M"),
        }
        for b in bookings
    ]
    return JsonResponse({'bookings': data})


@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, traveler=request.user)

    # Calculate totals
    total_amount = booking.package.price * booking.number_of_people   # Decimal OK
    razorpay_amount = int(total_amount * 100)  # Convert to paise (INTEGER)

    # Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create order
    payment = client.order.create({
        'amount': razorpay_amount,      # ✅ INTEGER paise value
        'currency': 'INR',
        'payment_capture': '1'
    })

    booking.razorpay_order_id = payment['id']
    booking.save()

    context = {
        'booking': booking,
        'order_id': payment['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'total_amount': total_amount,       # For display
        'amount': razorpay_amount,          # For Razorpay script
        'currency': 'INR',
    }

    return render(request, 'travelers/payment.html', context)


@csrf_exempt
def payment_success(request):

    # Razorpay POST callback after payment
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")

    # Browser GET redirect from your JS
    else:
        booking_id = request.GET.get("id")

    # If nothing is received → prevent crash
    if not booking_id:
        return render(request, "travelers/payment_failed.html", {
            "error": "Payment completed but booking ID missing."
        })

    booking = get_object_or_404(Booking, id=booking_id)
    total_amount = booking.package.price * booking.number_of_people


    # Update payment status
    if booking.status != "Paid":
        booking.status = "Paid"
        booking.save()

    return render(request, "travelers/payment_success.html", {
        "booking": booking,
        "total_amount":total_amount
    })




@login_required
def view_receipt(request, id):
    booking = get_object_or_404(Booking, id=id, traveler=request.user)

    if booking.status != "Paid":
        messages.error(request, "Payment not completed. Receipt unavailable.")
        return redirect("my_bookings")
    total_amount = booking.package.price * booking.number_of_people 

    return render(request, "travelers/receipt.html", {
        "booking": booking,
        "total_amount": total_amount,
        })


    
@login_required
def check_in(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Only traveler should check in
    if request.user != booking.traveler:
        return HttpResponseForbidden("Not allowed")

    booking.status = "Checked-In"
    booking.save()

    # Notify agency
    # Notification.objects.create(
    #     user=booking.package.agency.user,
    #     message=f"{request.user.username} has Checked-In for {booking.package.package_name}"
    # )

    messages.success(request, "Check-In successful!")
    return redirect('traveler_bookings')

@login_required
def download_receipt(request, id):
    booking = get_object_or_404(Booking, id=id)

    # Only traveler OR the agency that owns the package can download
    if request.user != booking.traveler and request.user != booking.package.agency.user:
        return HttpResponseForbidden("Not allowed")

    # Only Paid bookings can get receipt
    if booking.status != "Paid":
        return HttpResponse("Payment not completed.")

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{booking.id}.pdf"'

    # Create PDF
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "Payment Receipt")

    # Content
    pdf.setFont("Helvetica", 12)
    y = height - 100

    pdf.drawString(50, y,        f"Receipt ID: RCPT{booking.id}")
    pdf.drawString(50, y - 20,   f"Package: {booking.package.package_name}")
    pdf.drawString(50, y - 40,   f"Traveler: {booking.traveler.username}")
    pdf.drawString(50, y - 60,   f"Agency: {booking.package.agency.agency_name}")
    pdf.drawString(50, y - 80,   f"Amount Paid: ₹{booking.package.price}")
    pdf.drawString(50, y - 100,  f"Status: {booking.status}")
    pdf.drawString(50, y - 120,  f"Booking Date: {booking.booking_date}")

    pdf.showPage()
    pdf.save()
    return response


@login_required
def booking_history(request):
    history = Booking.objects.filter(
        traveler=request.user,
        status__in=["Completed", "Rejected"]
    ).order_by("-id")

    completed = history.filter(status="Completed")
    rejected = history.filter(status="Rejected")

    return render(request, 'travelers/history.html', {
        'history': history,
        'completed':completed,
        'rejected':rejected
        })

def cancel_booking(request, id):
    booking = Booking.objects.get(id=id, traveler=request.user)

    if booking.status == "Confirmed" or booking.status == "Pending" or booking.status == "Paid":
        booking.status = "Cancelled"
        booking.save()
        messages.warning(request, "Booking canceled. No refund will be provided. Contact agency for help.")
    else:
        messages.info(request, "This booking cannot be canceled.")

    return redirect("traveler_bookings")
