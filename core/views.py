from django.shortcuts import render
from .models import LeadershipTeam, Testimonial

def about_us(request):
    leadership_team = LeadershipTeam.objects.all()
    testimonials = Testimonial.objects.all()
    return render(request, 'about_us.html', {
        'leadership_team': leadership_team,
        'testimonials': testimonials
    })

def contact_us(request):
    return render(request, 'contact_us.html')

# Create your views here.
