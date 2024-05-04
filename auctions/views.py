from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    active = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "list": active,
        "categories": allCategories
        
    })
    
def closeAuction(request, id):
    lD=Listing.objects.get(pk=id)
    lD.isActive = False
    lD.save()
    isListing = request.user in lD.watchlist.all()
    allComments = Comment.objects.filter(listing=lD)
    isOwner=request.user.username==lD.owner.username
    return render(request, "auctions/listing.html", {
        "lD": lD,
        "iL": isListing,
        "aC": allComments,
        "iO": isOwner,
        "update": True,
        "message": "Congratulation"
    })
    
def displayWatchList(request):
    currentUser=request.user
    list = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "list": list
    })
    
def addBid(request, id):
        newBid=request.POST['newBid']
        listingData=Listing.objects.get(pk=id)
        
        isListingInWatchList=request.user in listingData.watchlist.all()
        allComments=Comment.objects.filter(listing=listingData)
        isOwner=request.user.username==listingData.owner.username
        if int(newBid) > listingData.price.bid:
            updateBid=Bid(user=request.user, bid=int(newBid))
            updateBid.save()
            listingData.price=updateBid
            listingData.save()
            return render(request, "auctions/listing.html",{
                "lD":listingData,
                "message":"Bid was updated",
                "update":True,
                "iL":isListingInWatchList,
                "aC": allComments,
                "iO": isOwner
            })
        else:
            return render(request, "auctions/listing.html",{
                "lD":listingData,
                "message":"Bid was failed",
                "update":False,
                "iL":isListingInWatchList,
                "aC": allComments,
                "iO": isOwner
            })
    
def addComment(request, id):
    currentUser=request.user
    listingData=Listing.objects.get(pk=id)
    message = request.POST['newComment']
    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    
    newComment.save()
    
    return HttpResponseRedirect(reverse("listing", args=(id, )))
    
def removeWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def listing(request, id):
    listData = Listing.objects.get(pk=id)
    isListing = request.user in listData.watchlist.all()
    allComments = Comment.objects.filter(listing=listData)
    isOwner=request.user.username==listData.owner.username
    
    return render(request, "auctions/listing.html", {
        "lD": listData,
        "iL": isListing,
        "aC": allComments,
        "iO": isOwner
    })


def createListing(request):
    if request.method == 'GET':
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories": allCategories
        })
    else:
        title = request.POST['title']
        description = request.POST['description']
        imageurl = request.POST['imageurl']
        price = request.POST['price']
        category = request.POST['category']
        
        currentUser = request.user
        
        categoryData=Category.objects.get(categoryName=category)
        
        bid=Bid(bid=int(price), user=currentUser)
        bid.save()
        
        newListing = Listing(
            title=title, 
            description=description,
            imageURL=imageurl,
            price=bid,
            category=categoryData,
            owner=currentUser
        )
        newListing.save()
        
        return HttpResponseRedirect(reverse(index))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST['category']
        category = Category.objects.get(categoryName=categoryForm)
        active = Listing.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "list": active,
            "categories": allCategories
            
        })