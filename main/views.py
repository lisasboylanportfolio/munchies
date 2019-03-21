import requests
import csv
import io
import re

from django import forms
from django.shortcuts import render, redirect

import urllib.request 

DEBUG=True
DEFAULT_RESTAURANT_IMG ="/img/default_restaurant.jpg"


class QueryForm(forms.Form):
    zipcode = forms.CharField(max_length=5)
    lat     = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    lon     = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    
class CategoryForm(forms.Form):
    category_id = forms.IntegerField(required=True)
    city        = forms.CharField(max_length=60)
    latitude    = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
    longitude   = forms.DecimalField(max_digits=9,decimal_places=6,initial=0.0)
  
def index(request):

  if DEBUG:
    print("DEBUG:views.index()")
    
    # Process Get request
    form = QueryForm()
    context = {
      'form' : form,
    }

    return render(request, 'index.html', context)
  
def get_business_image(name, address, city):
  if DEBUG:
    print("DEBUG:views.get_business_image()")    

  thumbnail=''
  subscription_key = "54438b3b2bc34bf5a93e464bd6ef59bb"
  search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
  #search_url= 'https://www.bing.com/images/search'
  #search_term = name + " " + address  + '&FORM=OIIARP'
  search_term = name + " " + address + " " + city 
  headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
  params  = {"q": search_term, "license": "public", "imageType": "photo"}
  #url = 'https://www.bing.com/images/search?q=' + name + " " + address + '&FORM=OIIARP'  
  if DEBUG:
    print("DEBUG:views.get_business_image().url=", search_url, headers, params)
    print("DEBUG:views.get_business_image().search_term=", search_term)      
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
  categories=[]
  category={}  
      
  if request.method == 'GET':
    if DEBUG:
      print("DEBUG:views.categories().request", request)      

    # Create a form instance and populate it with data from the request
    form = QueryForm(request.GET)
    if form.is_valid():
      if DEBUG:
        print("DEBUG:views.categories().if==valid")      

      # Get Form Data
      longitude = form.cleaned_data['lon']
      latitude  = form.cleaned_data['lat']
      zipcode   = form.cleaned_data['zipcode']

      if zipcode != None:   #NO lat or longitude specified, so get them
        # Get Latitude and longitude
        url="https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V04_01.aspx?apikey=8f308d2349cc420285c305e07ad4d049&version=4.01&zip=" + zipcode + "&allowTies=true"
        url_open = urllib.request.urlopen(url)
        csvfile = csv.reader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',')
        data = list(csvfile)
        if DEBUG:
          print("DEBUG:views.categories().data=", data)  
        for value in data:
          latitude=value[3]
          longitude=value[4]
          if DEBUG:
            print("DEBUG:views.categories().value=", value)    
            print("DEBUG:views.categories().lat=", latitude)
            print("DEBUG:views.categories().lon=", longitude)
          
            
      # Using lat and lon get nerby resuarants and city for lat and lon
      # Use Zomato Collections API w lon and lat to get collection_id, title, description
      url_categories="https://developers.zomato.com/api/v2.1/collections?lat=" + latitude + "&lon=" + longitude + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
      url_city ='https://developers.zomato.com/api/v2.1/geocode?lat=' + latitude + '&lon=' + longitude + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
      if DEBUG:
       print("DEBUG:views.categories().url_categories=", url_categories)
       print("DEBUG:views.categories().url_city=", url_city)         
      try:
         response=requests.get(url_city)
         data = response.json()
         city = data['location']['title']        # get city which correspondes to lat and lon
         if DEBUG:
          print("DEBUG:views.categories().city=", city)           
         response=requests.get(url_categories)
         data = response.json()
         collections=data['collections']
         
         # Get form data
         for item in collections:            
           collection_id  = item['collection']['collection_id']
           result_count   = item['collection']['res_count']
           collection_img = item['collection']['image_url']
           title          = item['collection']['title']
           description    = item['collection']['description']
           
           category={
             'collection_id'    : collection_id,
             'result_count'     : result_count,
             'image_url'        : collection_img,
             'title'            : title,
             'description'      : description,
             'city'             : city,
             'lat'              : latitude,
             'lon'              : longitude,
           }
           categories.append(category)
           #if DEBUG:
           #  print("DEUG:views.index().collection=", categories)
      except KeyError:
        print ('Where is my collection data?')
        
      if categories == None:
        print("FATAL ERROR: No categories returned:")
        exit()
      else:
       context={
         'categories': categories,  # list of dictionaries containing list of items we want)
                                     # Use: collection_id, title, description,image_url
                                     # so collections[0]['collection_id']
                                     # checkout display at: http://www.zoma.to/c-10799/1
       }
       # Display the categories
       return render(request, 'categories.html', context)
  else:
    print("No POST in categories()")

  
def restaurants(request):
  if DEBUG:
    print("DEBUG:views.restaurants()")    
      
  # Get the requested Collection
  if request.method == 'GET':
    if DEBUG:
      print("DEBUG:views.restaurants().if GET")

    try:         
       # Parse the request to get parameters
      if DEBUG:
       print("DEBUG:views.restaurants().request", request)
       param=f'{request}'
       param=list(f'{request}'.split("&")) # parse out variables assignments
       del param[0]                        #remove header:'<WSGIRequest: GET ' from reults, leaving only parameters
       tmp=param[-1].replace("'>", "")    # remove header garbage from last element
       param[-1]=tmp
       param=list_to_dict(param)
       if DEBUG:
        print("DEBUG:views.restaurants().param=",param)
        
      collection_id = param['collection_id']
      city          = param['city']
      latitude      = param['latitude']
      longitude     = param['longitude']
      if DEBUG:
          print("DEBUG:views.restaurants().collection_id=",collection_id)
          print("DEBUG:views.restaurants().collection_id=",city)
          print("DEBUG:views.restaurants().collection_id=",latitude)
          print("DEBUG:views.restaurants().collection_id=",longitude)                 
    except KeyError:
      print ('Where is my collection data?')

    # Get a list of restaurants matching the category user chose
    url = 'https://developers.zomato.com/api/v2.1/search?q=' + city + '&lat=' + latitude + "&lon=" + longitude + "&collection_id=" + collection_id + "&apikey=58c103ef995b6c9ca5d19c2a8e7a3e42"
    if DEBUG:  
      print("DEBUG:views.restaurants().url=", url)

    response=requests.get(url)
    data = response.json()
    num_restaurants = data['results_found']
    if DEBUG:
      print("DEBUG:views.restaurants().num_restaurants=", num_restaurants)
    results=data['restaurants']
    restaurants=[]
     
    # Get subset of restaurant properties
    for pos, item in enumerate(results):
      if DEBUG:
        print("DEBUG:views.restaurants().pos=", pos)        
        print("DEBUG:views.restaurants().item=", item)
      slider_id = pos   # This is used to control carousel flow
      restaurant_id = item['restaurant']['id']
      name = item['restaurant']['name']
      address = item['restaurant']['location']['address']  #  street addr, city, zip
      #url = item['url']      #DEBUG: this probably wont work
      url =  get_business_image(name, re.sub(',','', address), city)      # remove ',' from address and the pass on
      if DEBUG:
        print("DEBUG:views.restaurants().url", url)          
      city = item['restaurant']['location']['locality']
      city_id = item['restaurant']['location']['city_id']  # Zomato assigned city id
      zipcode = item['restaurant']['location']['zipcode']
      cuisine = item['restaurant']['cuisines']
      user_rating = item['restaurant']['user_rating']['aggregate_rating']
      num_votes = item['restaurant']['user_rating']['votes']
      average_cost_for_two = item['restaurant']['average_cost_for_two']
    
      restaurant={
        'slider_id'     : pos,  # used to control carousel flow
        'restaurant_id' : restaurant_id,
        'name'          : name,
        'address'       : address,
        'url'           : url,
        'city'          : city,
        'city_id'       : city_id,
        'zipcode'       : zipcode,
        'cuisine'       : cuisine,
        'user_rating'   : user_rating,
        'num_votes'     : num_votes,
        'average_cost'  : average_cost_for_two,    
      }
      restaurants.append(restaurant)
  
    print(restaurants)
    print("len restaurants=", len(restaurants))
 
#    context={
#      'restaurants':restaurants,   # A list of restaurants
#    }
    #EBUG
    context={
        'slider_id'     : "1",  # used to control carousel flow
        'restaurant_id' : "12345",
        'name'          : "millies",
        'address'       : "1234 e St",
        'url'           : "img/default_restaurant.jpg",
        'city'          : "Lafayette",
        'city_id'       : "789",
        'zipcode'       : "94549",
        'cuisine'       : "Fast Food",
        'user_rating'   : "3",
        'num_votes'     : "5",
        'average_cost'  : "$35",
    }
    # Display the restaurants
    return render(request, 'restaurants.html', context)


def getChoices(request):
  if DEBUG:
    print("DEBUG:views.getChoices()")
    if requests.method == 'POST':
    #save user restaurants
      redirect('/')
    elif request.method == 'GET':
    # Get user restaurants
      render(request, 'choices.html, context')
    
def list_to_dict(rlist):
  # convert a list with = seperated values to dict and strip white spaces
  return dict(map(lambda s : map(str.strip, s.split('=')), rlist))  

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


if __name__ == '__main__':
  restaurants()