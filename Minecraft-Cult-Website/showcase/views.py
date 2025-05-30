from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Build, Tag, Image
from .forms import BuildForm

import random

# Create your views here.
def showcase(request):
    # Display the searched and filtered builds
    searchQuery = request.GET.get('search', '')
    filter_string = request.GET.get('filters', '')

    filters = []
    for filter in filter_string.split(","):
        if filter != "":
            filters.append(filter)

    builds = Build.objects.filter(Q(title__icontains=searchQuery) | Q(creator__icontains=searchQuery) | Q(tags__name__icontains=searchQuery)).distinct()
    
    filter_query = Q()
    for filter in filters:
        filter_query |= Q(tags__name__iexact=filter)

    builds = builds.filter(filter_query).distinct()
    

    paginator = Paginator(builds, 12)
    page_number = request.GET.get('page')
    builds = paginator.get_page(page_number)
    
    tags = Tag.objects.all()    

    context = {'tags': tags, 'builds': builds, }
    return render(request, 'showcase.html', context)

def createBuild(request):
    if request.method == "POST":
        form = BuildForm(request.POST)
        if form.is_valid():
            build = form.save()

            #Process the images uploaded
            thumbnail = request.FILES['thumbnail']
            Image.objects.create(name=thumbnail.name , build=build, image=thumbnail, thumbnail=True)

            images = request.FILES.getlist('images') 
            for image in images:
                Image.objects.create(name=image.name, build=build, image=image, thumbnail=False)

            messages.success(request, 'Uploaded Build Successful! Please wait for approval.')
        else:
            messages.error(request, 'Upload Failed! Please refresh and try again', extra_tags='danger') 

    return redirect('showcase')

def buildDetails(request, id):
    # Display the specific build
    if id:
        builds = Build.objects.all()
        build = builds.filter(Q(id=id)).first()

        builds = list(builds)
        builds.remove(build)
        while len(builds) >= 6:
            builds.remove(random.choice(builds))

        random.shuffle(builds)


        context = {'build': build, 'builds': builds}
        return render(request, 'buildDetails.html', context)
    