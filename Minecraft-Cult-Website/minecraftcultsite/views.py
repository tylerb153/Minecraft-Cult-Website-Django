from django.shortcuts import render
import requests
from showcase.models import Build, Image

import datetime
import random

# Create your views here.
def home(request):
    # This updated and returns the featured build. it updates it if the date updated changes or there isn't one. it also checks if it's been accepted, unaccepted builds can't be featured. 
    featuredBuild = updateFeaturedBuild()

    # We are going to get the most recent build here for use in the recent build tile
    recentBuild = Build.objects.filter(accepted=True).last()
    images = getRandomImages()

    mapLink = "Offline"
    try:
        if requests.head("https://dynmap.theminecraftcult.com/", timeout=1).status_code == 200:
            mapLink = "https://dynmap.theminecraftcult.com/"
    except:
            mapLink = "Offline"

    
    context = {'recentBuild': recentBuild, 'featuredBuild': featuredBuild, 'images':images, 'mapLink': mapLink}
    return render(request, 'home.html', context=context)

def mapPage(request):
    dynmapLink = "https://dynmap.theminecraftcult.com/"
    bluemapLink = "https://bluemap.theminecraftcult.com/"
    dynmapLive = False
    bluemapLive = False
    try:
        if requests.head(dynmapLink, timeout=1).status_code == 200:
                dynmapLive = True
    except:
        pass
    try:
        if requests.get(bluemapLink, timeout=1, stream=True, headers={"Host": "bluemap.theminecraftcult.com", "User-Agent": "Mozilla/5.0"}).status_code < 400:
                bluemapLive = True
    except:
        pass
    
    queryString = request.META.get('QUERY_STRING', '')    

    return render(request, 'map.html', context={"dynmapLive": dynmapLive, "bluemapLive": bluemapLive, "dynmapLink": dynmapLink, "bluemapLink": bluemapLink, "queryString":queryString})


# Figure out if a new featured build needs to be selected in order to make sure it only change once per day
def updateFeaturedBuild():
    global dateUpdated

    # Here we set up the globals if they don't have a value already
    try:
        if dateUpdated:
            pass
    except:
        dateUpdated = None

    featuredBuilds = Build.objects.filter(featured=True)
    if dateUpdated != datetime.date.today() or len(featuredBuilds) == 0:
        dateUpdated = datetime.date.today()
        if len(featuredBuilds) > 0:
            for build in featuredBuilds:
                build.featured = False
                build.save()

        builds = list(Build.objects.filter(accepted=True))
        if builds != []:    
            featuredBuild = random.choice(builds)

            featuredBuild.featured = True
            featuredBuild.save()
            return featuredBuild
        else:
            return None

    return featuredBuilds.first()

def getRandomImages() -> list[Image]:
    builds = Build.objects.filter(accepted=True).prefetch_related('images')
    images = []
    for build in builds:
        images.extend(build.images.all())
    return random.sample(images, k=min(10, len(images)))

def getMapLink() -> str:
    try:
        if requests.head('https://map.tymler.com/', timeout=1).status_code == 200:
            mapLink = 'https://map.tymler.com/'
        elif requests.head('https://backupmap.tymler.com/', timeout=1).status_code == 200:
            mapLink = 'https://backupmap.tymler.com/'
        else:
            mapLink = "Offline"
    except:
        mapLink = "Offline"

    return mapLink