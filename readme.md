Ilmatieteenlaitoksen säädata lataaja
==============================


Tämä on yksinkertainen graafisen käyttöliittymän tarjoava sovellus ilmatieteenlaitoksen säädatan lataamiseen Exceliin soveltuvassa muodossa. Ohjelma kehitettiin alunperin Lammin Biologisen aseman tarpeisiin.

Ohjelmalla voit ladata Ilmatieteenlaitoksen avoimen datan palvelusta eri sääasemien vuorokausi- ja reaaliaikakohtaista säädataa.

[Lataa asennettava ohjelma Windowsille tästä](http://example.com)

----------


Sovelluskehittäjille tiedoksi
-------------

Tämä sovellus kehitettiin alunperin varsin nopeasti kasaan käyttäen Python 3:sta ja PyQt5:sta.  Tästä syystä etenkin GUI-puolen koodia ei ole pahemmin siistitty.

Varsinainen API:n käsittely ja http-pyyntöjen käsittelykoodi on kuitenkin eroteltu "fmi"-etuliitteisiin tiedostoihin.

Saatan tulevaisuudessa siistiä koodia hieman, mutta varsinainen jatkokehitys omalta osaltani on epätodennäköistä. Forkkaus on kuitenkin tervetullutta, sillä tutkijapiireissä tuntuu olevan kysyntää avoimelle datalle.

----------


Requirements
--------------------

Alla sovelluksen vaatimat Python 3, paketit, jotka kannattanee asentaa pip:llä. Lisäksi tarvitset PyQt5:n.

    lxml==3.4.2
	numpy==1.8.2
	pandas==0.15.2
	py2exe==0.9.2.2
	python-dateutil==2.4.0
	pytz==2014.10

Ohjelman voi koota jaeltavaksi exe-tiedostoksi py2exe työkalulla ajamalla juurihakemistossa komennon

    python3 setup.py py2exe

Tämän jälkeen syntyneeseen dist hakemistoon on vielä kopioitava "platforms" kansio PyQT:n hakemistosta, joka omalla kohdallani löytyi polusta:

    C:\Python34\Lib\site-packages\PyQt5\plugins\platforms

Dist hakemiston voi sitten pakata käteväksi asennettavaksi ohjelmaksi vaikkapa [InnoSetupilla](http://www.jrsoftware.org/isinfo.php), johon löytyy skripti juurihakemistosta.

