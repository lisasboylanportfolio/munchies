import requests
import csv
import io
import re

from django import forms
from django.shortcuts import render, redirect

import urllib.request 

DEBUG=True
DEFAULT_RESTAURANT_IMG = 'img/default_restaurant_img'


class QueryForm(forms.Form):
    zipcode = forms.CharField(max_length=5)
    lat     = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    lon     = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    
class CategoryForm(forms.Form):
    category_id = forms.IntegerField(required=True)
    lat          = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    lon          = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
#    city         =  forms.CharField(max_length=60)
    zipcode      = forms.CharField(max_length=5)    
    
def index(request):

    if DEBUG:
      print("DEBUG:views.index()")
      
      # Process Get request
      form = QueryForm()
      context = {
        'form' : form,
      }
      return render(request, 'index.html', context)
       
#def get_business_image(name, address, city):
def get_business_image(name, address:
  if DEBUG:
    print("DEBUG:views.get_business_image()")    

  thumbnail=''
  subscription_key = "54438b3b2bc34bf5a93e464bd6ef59bb"
  search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
  #search_url= 'https://www.bing.com/images/search'
  #search_term = name + " " + address  + '&FORM=OIIARP'
  search_term = "Millie's Kitchen Lafayette CA" 
  headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
  params  = {"q": search_term, "license": "public", "imageType": "photo"}
  #url = 'https://www.bing.com/images/search?q=' + name + " " + address + '&FORM=OIIARP'  
  if DEBUG:
    print("DEBUG:views.get_business_image().url=", search_url, headers, params)  
  response = requests.get(search_url, headers=headers, params=params)
  response.raise_for_status()
  data = response.json()
  if DEBUG:
    print("DEBUG:views.get_business_image().data=", data)
    print("DEBUG:views.get_business_image().data.keys=", data.keys())
  
  # See if we can find a url (image) for the business
  if 'relatedSearches' in data.keys():
    not_found = True
    loop_cnt = 0
    if DEBUG:
      print("DEBUG:views.get_business_image().data.keys: has relatedSearches")
    # Loop until we thhink we found an img
    while not_found and loop_cnt < len(data['relatedSearches']):
      item = data['relatedSearches'][loop_cnt]
      loop_cnt += 1
      if DEBUG:
        print("DEBUG:views.get_business_image().item=", item)
        print("DEBUG:views.get_business_image().loop_cnt=", loop_cnt)         
        # Check to see if city is in text string
      if city in item['text']:
        if DEBUG:
          print("DEBUG:views.get_business_image().city in:", item['text'])               
        # get url for business image
        thumbnail = item['thumbnail']['thumbnailUrl']
        not_found = False
  else: # No img found
    thumbnail=DEFAULT_RESTAURANT_IMG

  if DEBUG:
    print("DEBUG:views.get_business_image().thumbnail=", thumbnail)            
  return thumbnail

  
def categories(request):

  if DEBUG:
    print("DEBUG:views.categories()")
    
  city=''
  lat=''
  lon=''
  collection_id=''
  position=''  # used to control carousel flow
  restaurant_id=''
  name=''
  address=''
  url=''
  city=''
  city_id=''
  zipcode=''
  cuisine=''
  user_rating=''
  num_votes=''
  average_cost_for_two=''      
      
  if request.method == 'GET':
    if DEBUG:
      print("DEBUG:views.categories().request", request)      
      # Create a form instance and populate it with data from the request
      form = QueryForm(request.GET)
      if form.is_valid():
        if DEBUG:
          print("DEBUG:views.index().if==valid")      
  
        # Create a new user  - TODO
        longitude = form.cleaned_data['lon']
        latitude  = form.cleaned_data['lat']
        zipcode   = form.cleaned_data['zipcode']

        if zipcode != None:
          # Get Latitude and longitude
          url="https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V04_01.aspx?apikey=8f308d2349cc420285c305e07ad4d049&version=4.01&zip=" + zipcode + "&allowTies=true"
          url_open = urllib.request.urlopen(url)
          csvfile = csv.reader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',')
          data = list(csvfile)
          if DEBUG:
            print("DEBUG:views.categories().data=", data)  
          for value in data:
            lat=value[3]
            lon=value[4]
            if DEBUG:
              print ("value=", value)    
              print("lat=", lat)
              print("lon=", lon)
            
        # Using lat and lon get nerby resuarants
        # Use Zomato Collections API w lon and lat to get collection_id, title, description
        url="https://developers.zomato.com/api/v2.1/collections?lat=" + lat + "&lon=" + lon + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
        if DEBUG:
         print("DEBUG:views.categories().url=", url)
        response=requests.get(url)
        data = response.json()
        collections=data['collections']
        categories=[]
        category={}
       
        for item in collections:
          
          collection_id  = item['collection']['collection_id']
          result_count   = item['collection']['res_count']
          collection_img = item['collection']['image_url']
          title          = item['collection']['title']
          description    = item['collection']['description']
          
          category={
            'collection_id'    : collection_id,
            'result_count'     : result_count,
            'imgage_url'       : collection_img,
            'title'            : title,
            'description'      : description,
          }
          categories.append(category)
          #if DEBUG:
          #  print("DEUG:views.index().collection=", categories)

        if categories != None:
          context={
            'categories': categories,  # list of dictionaries containing list of items we want)
                                        # Use: collection_id, title, description,image_url
                                        # so collections[0]['collection_id']
                                        # checkout display at: http://www.zoma.to/c-10799/1
          }
        else:
           print("FATAL ERROR: No categories returned:")
           exit()
         
        # Display the restaurants
        return render(request, 'categories.html', context)
  
def restaurants(request):
  if DEBUG:
    print("DEBUG:views.restaurants()")    
  pass

def getChoices(request):
  if DEBUG:
    print("DEBUG:views.getChoices()")
    

  # Get the requested Collection
  if request.method == 'GET':
    if DEBUG:
      print("DEBUG:views.categories().if POST")
    try:
        collection_id = request.POST['collection_id']
        # TODO use flag
    except KeyError:
        print ('Where is my flag?')
        
    if DEBUG:
      print("DEBUG:views.categories().collection_id=")    
    # Get the restuarants from the specified category   
    # Use Search API to get final data
    # Create a form instance and populate it with data from the request
    #form = CategoryForm(request.POST)
    #if form.is_valid():    
    #  collection_id = form.cleaned_data(request['collection_id'])
#      lat           = form.cleaned_data(request['latitude'])
#      lon           = form.cleaned_data(request['longitude'])
#      city          = form.cleaned_data(request['city'])      
    
#    if DEBUG:  
#      print("DEBUG:views.restaurants().city=", city)    
    # Get a list of restaurants matching the category user choose
    # DEBUG : add city back
    #url = 'https://developers.zomato.com/api/v2.1/search?city=' +  '&lat=' + lat + "&lon=" + lon + "&collection_id=" + collection_id + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
    url = 'https://developers.zomato.com/api/v2.1/search?city=' +  '&lat=' + lat + "&lon=" + lon + "&collection_id=" + collection_id + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
    if DEBUG:  
      print("DEBUG:views.restaurants().url=", url)
    response=requests.get(url)
    data = response.json()
    num_restaurants = data['results_found']
    result_restaurants=data['restaurants']
    restaurants=[]
    restaurant={}
     
    # Get subset of restaurant properties
    for pos, item in enumerate(result_restaurants):
      if DEBUG:  
        print("DEBUG:views.restaurants().item=", item)
      slider_id = pos   # This is used to control carousel flow
      restaurant_id = item['restaurant']['id']
      name = item['restaurant']['name']
      address = item['restaurant']['location']['address']  #  street addr, city, zip
      #url = item['url']      #DEBUG: this probably wont work
      url =  get_business_image(name, re.sub(',','', address), city)      # remove ',' from address and the pass on
      if DEBUG:
        print("DEBUG:views.restaurants().url", url)          
#      city = item['restaurant']['location']['locality']
#      city_id = item['restaurant']['location']['city_id']  # Zomato assigned city id
      zipcode = item['restaurant']['location']['zipcode']
      cuisine = item['restaurant']['cuisines']
      user_rating = item['restaurant']['user_rating']['aggregate_rating']
      num_votes = item['restaurant']['user_rating']['votes']
      average_cost_for_two = item['restaurant']['average_cost_for_two']
    
      restaurant={
        'slider_id'     : position,  # used to control carousel flow
        'restaurant_id' : restaurant_id,
        'name'          : name,
        'address'       : address,
        'url'           : url,
#        'city'          : city,
#        'city_id'       : city_id,
        'zipcode'       : zipcode,
        'cuisine'       : cuisine,
        'user_rating'   : user_rating,
        'num_votes'     : num_votes,
        'average_cost'  : average_cost_for_two,    
      }
      restaurants.append(restaurant)
  
    print(restaurants)
    print("len restaurants=", len(restaurants))
    
    context={
      'restaurants':restaurants,   # A list of restaurants
    }
    # Display the restaurants
    return render(request, 'restaurants.html', context)


if __name__ == '__main__':
  restaurants()