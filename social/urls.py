from django.urls import path
from social import views

urlpatterns = [
    path('userreg/',views.userreg,name="userreg"),
    path('userlogin/',views.userlogin,name="userlogin"),
    path('logoutuser/',views.logoutuser,name="logoutuser"),
    path('',views.home,name="home"),
    path('upload', views.upload),
    path('like-post/<str:id>',views.likes,name='like-post'),
    path('#<str:id>',views.home_post),
    path('explore/',views.explore,name="explore"),
    path('profile/<str:id_user>',views.profile),
    path('delete/<str:id>', views.delete),
    path('search-results/', views.search_results, name='search_results'),
    path('follow', views.follow, name='follow'),
    path('view_post/<str:id>',views.view_post,name="view_post"),


]
