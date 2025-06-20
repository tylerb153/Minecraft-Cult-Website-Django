from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Build, Tag, Image, BuildTag
from .forms import BuildForm

import random
import json

# Create your views here.
def showcase(request):
    # Display the searched and filtered builds
    searchQuery = request.GET.get('search', '')
    filter_string = request.GET.get('filters', '')

    builds = Build.objects.filter(Q(title__icontains=searchQuery) | Q(creator__icontains=searchQuery) | Q(tags__name__icontains=searchQuery)).distinct()

    for filter in filter_string.split(","):
        if filter != "":
            builds = builds.filter(tags__name__iexact=filter)

    builds = builds.filter(accepted=True)

    paginator = Paginator(builds, 12)
    page_number = request.GET.get('page')
    builds = paginator.get_page(page_number)
    
    tags = Tag.objects.filter(accepted=True)
    tags = list(tags.values_list("name", flat=True))

    context = {'tags': tags, 'builds': builds, }
    return render(request, 'showcase.html', context)

def createBuild(request):
    if request.method == "POST":
        form = BuildForm(request.POST)
        tags = Tag.objects.all()
        try:
            if form.is_valid():
                try:
                    build = form.save()
                except Exception as e:
                    raise Exception(f"Creating Build Failed!\n{e}")

                #Process the images uploaded
                try:
                    thumbnail = request.FILES['thumbnail']
                    Image.objects.create(name=thumbnail.name , build=build, image=thumbnail, thumbnail=True)

                    images = request.FILES.getlist('images') 
                    for image in images:
                        Image.objects.create(name=image.name, build=build, image=image, thumbnail=False)
                except Exception as e:
                    raise Exception(f"Image Processing Failed!\n{e}")

                #Process the tags
                try:
                    if request.POST['tagsInput'] != "":
                        for tag in json.loads(request.POST['tagsInput']):
                            tagName = ""
                            for word in tag["value"].split():
                                tagName += word.capitalize() + " "
                            tagName = tagName.strip()
                            existingTag = tags.filter(name__iexact=tagName)
                            if existingTag:
                                BuildTag.objects.create(tag=existingTag.first(), build=build)
                            else:
                                tag = Tag.objects.create(name=tagName)
                                BuildTag.objects.create(tag=tag, build=build)
                except Exception as e:
                    raise Exception(f"Creating tags Failed!\n{e}")



                messages.success(request, 'Uploaded Build Successful! Please wait for approval.')
            else:
                raise Exception("Build Upload Failed!")
        except:
            messages.error(request, 'Upload Failed! Please refresh and try again', extra_tags='danger') 

    return redirect('showcase')

def buildDetails(request, slug):
    # Display the specific build
    if slug:
        builds = Build.objects.all()
        build = builds.filter(Q(slug=slug)).first()

        builds = list(builds)
        builds.remove(build)
        while len(builds) >= 6:
            builds.remove(random.choice(builds))

        random.shuffle(builds)


        context = {'build': build, 'builds': builds}
        return render(request, 'buildDetails.html', context)
    