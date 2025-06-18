from django.contrib import admin
from django.urls import path, include
from climate_app import views  # Import your app's views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path("api/disasters/", views.disaster_data_api, name="disaster_data_api"),
    path("climate-change/", views.climate_change_view, name="climate_change"), 
    #path('api/cyclones/', views.cyclone_data, name='cyclone_api'),  # Optional API endpoint
   # path('api/earthquakes/', views.earthquake_data, name='quake_api')  # Optional API endpoint
]