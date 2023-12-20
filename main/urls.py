from django.urls import path,include
from .views import *
from django.views.generic import TemplateView

app_name = 'main'  # Define the app_name or namespace for the app

urlpatterns = [
    path('home', home,name="home"),
    
    # INSIDE HOME TABS URL
    path('architecture/', TemplateView.as_view(template_name='Final/architecture.html'), name='architecture'),
    path('travelandtourism/', TemplateView.as_view(template_name='Final/travelandtourism.html'), name='travelandtourism'),
    path('Traditions/', TemplateView.as_view(template_name='Final/Traditions.html'), name='Traditions'),
    path('festivalsandcelebrations/', TemplateView.as_view(template_name='Final/festivalsandcelebrations.html'), name='festivalsandcelebrations'),
    path('literature/', TemplateView.as_view(template_name='Final/literature.html'), name='literature'),
    path('ArtsAndCrafts/', TemplateView.as_view(template_name='Final/ArtsAndCrafts.html'), name='ArtsAndCrafts'),
    path('SportsPage/', TemplateView.as_view(template_name='Final/SportsPage.html'), name='SportsPage'),
    path('yoga/', TemplateView.as_view(template_name='Final/yoga.html'), name='yoga'),
    path('ayurveda/', TemplateView.as_view(template_name='Final/ayurveda.html'), name='ayurveda'),
    path('Timeline/', TemplateView.as_view(template_name='Final/Timeline.html'), name='Timeline'),
    
    #INSIDE ARCHITECTURE PAGE URLS
    path('ramappa/', TemplateView.as_view(template_name='Final/ramappa.html'), name='ramappa'),
    path('chennakesava/', TemplateView.as_view(template_name='Final/chennakesava.html'), name='chennakesava'),
    path('baraImambara/', TemplateView.as_view(template_name='Final/baraImambara.html'), name='baraImambara'),
    path('daulathadab/', TemplateView.as_view(template_name='Final/daulathadab.html'), name='daulathadab'),
    path('kumbhalgarh_fort/', TemplateView.as_view(template_name='Final/kumbhalgarh fort.html'), name='kumbhalgarh-fort'),
    path('chittorgarh/', TemplateView.as_view(template_name='Final/chittorgarh.html'), name='chittorgarh'),
    path('National_museum/', TemplateView.as_view(template_name='Final/National_museum.html'), name='National_museum'),
    path('Indian_museum/', TemplateView.as_view(template_name='Final/Indian_museum.html'), name='Indian_museum'),
    path('gov_museum/', TemplateView.as_view(template_name='Final/gov_museum.html'), name='gov_museum'),
    path('chousath_mandir/', TemplateView.as_view(template_name='Final/chousath_mandir.html'), name='chousath_mandir'),
    path('brihadeswara/', TemplateView.as_view(template_name='Final/brihadeswara.html'), name='brihadeswara'),
    path('Vidhya_Shankara_Temple/', TemplateView.as_view(template_name='Final/Vidhya Shankara Temple.html'), name='Vidhya-Shankara-Temple'),
    
    #INSIDE TRAVEL&TOURISM PAGE URLS
    
    path('Kedarnath/', TemplateView.as_view(template_name='Final/Kedarnath.html'), name='Kedarnath'),
    path('Somnath/', TemplateView.as_view(template_name='Final/Somnath.html'), name='Somnath'),
    path('brihadeswara/', TemplateView.as_view(template_name='Final/brihadeswara.html'), name='brihadeswara'),
    path('Gurudwara/', TemplateView.as_view(template_name='Final/Gurudwara.html'), name='Gurudwara'),
    path('agra_fort/', TemplateView.as_view(template_name='Final/agra_fort.html'), name='agra_fort'),
    path('AjantaCaves/', TemplateView.as_view(template_name='Final/AjantaCaves.html'), name='AjantaCaves'),
    path('sanchi_stupa/', TemplateView.as_view(template_name='Final/sanchi_stupa.html'), name='sanchi_stupa'),
    path('Kaziranga_National_Park/', TemplateView.as_view(template_name='Final/Kaziranga National Park.html'), name='Kaziranga-National-Park'),
    path('Bandhavgarh_National_Park/', TemplateView.as_view(template_name='Final/Bandhavgarh_National_Park.html'), name='Bandhavgarh_National_Park'),
    path('Sundarbans_National_Park/', TemplateView.as_view(template_name='Final/Sundarbans National Park.html'), name='Sundarbans-National-Park'),
    path('Kanyakumari/', TemplateView.as_view(template_name='Final/Kanyakumari.html'), name='Kanyakumari'),
    path('Dharmshala/', TemplateView.as_view(template_name='Final/Dharmshala.html'), name='Dharmshala'),
    path('jaisalmer/', TemplateView.as_view(template_name='Final/jaisalmer.html'), name='jaisalmer'),
    
    #INSIDE FESTIVALS PAGE URLS
    path('diwali/', TemplateView.as_view(template_name='Final/diwali.html'), name='diwali'),
    path('ramzan/', TemplateView.as_view(template_name='Final/ramzan.html'), name='ramzan'),
    path('christmas/', TemplateView.as_view(template_name='Final/christmas.html'), name='christmas'),
    path('ugadi/', TemplateView.as_view(template_name='Final/ugadi.html'), name='ugadi'),
    path('gudipadwa/', TemplateView.as_view(template_name='Final/gudipadwa.html'), name='gudipadwa'),
    path('vishu/', TemplateView.as_view(template_name='Final/vishu.html'), name='vishu'),
    path('sankranti/', TemplateView.as_view(template_name='Final/sankranti.html'), name='sankranti'),
    path('onam/', TemplateView.as_view(template_name='Final/onam.html'), name='onam'),
    path('baisakhi/', TemplateView.as_view(template_name='Final/baisakhi.html'), name='baisakhi'),
    path('independenceday/', TemplateView.as_view(template_name='Final/independenceday.html'), name='independenceday'),
    path('republicday/', TemplateView.as_view(template_name='Final/republicday.html'), name='republicday'),
    path('constitutionday/', TemplateView.as_view(template_name='Final/constitutionday.html'), name='constitutionday'),
    path('teej/', TemplateView.as_view(template_name='Final/teej.html'), name='teej'),
    path('bonalu/', TemplateView.as_view(template_name='Final/bonalu.html'), name='bonalu'),
    path('mysoredasara/', TemplateView.as_view(template_name='Final/mysoredasara.html'), name='mysoredasara'),
    
    #INSIDE ARTS&CRAFTS PAGE URLS
    path('an_decorative/', TemplateView.as_view(template_name='Final/an decorative.html'), name='an-decorative'),
    path('an_performing.html/', TemplateView.as_view(template_name='Final/an performing.html'), name='an-performing'),
    path('an_handicrafts/', TemplateView.as_view(template_name='Final/an handicrafts.html'), name='an-handicrafts'),
    path('med_decorative/', TemplateView.as_view(template_name='Final/med decorative.html'), name='med-decorative'),
    path('med_performing/', TemplateView.as_view(template_name='Final/med performing.HTML'), name='med-performing'),
    path('med_handicrafts/', TemplateView.as_view(template_name='Final/med handicrafts.html'), name='med-handicrafts'),
    path('mod_decorative/', TemplateView.as_view(template_name='Final/mod decorative.html'), name='mod-decorative'),
    path('mod_performing/', TemplateView.as_view(template_name='Final/mod performing.html'), name='mod-performing'),
    path('mod_handicrafts/', TemplateView.as_view(template_name='Final/mod handicrafts.html'), name='mod-handicrafts'),
    
    #INSIDE SPORTS PAGE
    path('ancientcognitivesports/', TemplateView.as_view(template_name='Final/ancientcognitivesports.html'), name='ancientcognitivesports'),
    path('ancientphysicalsport/', TemplateView.as_view(template_name='Final/ancientphysicalsport.html'), name='ancientphysicalsport'),
    path('medievalcognitivesports/', TemplateView.as_view(template_name='Final/medievalcognitivesports.html'), name='medievalcognitivesports'),
    path('medievalphysicalsports/', TemplateView.as_view(template_name='Final/medievalphysicalsports.html'), name='medievalphysicalsports'),
    path('moderncognitivesport/', TemplateView.as_view(template_name='Final/moderncognitivesport.html'), name='moderncognitivesport'),
    path('modernphysicalsport/', TemplateView.as_view(template_name='Final/modernphysicalsport.html'), name='modernphysicalsport'),
    
    
  

   
]