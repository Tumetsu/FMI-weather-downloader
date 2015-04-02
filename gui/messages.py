from PyQt5.QtCore import QCoreApplication

class Messages:
    """ To me this seems a bit like hack. This class has functions to get translated strings to be shown in UI. The
    reason for them being in functions is that apparently Qt translate will not work in multiple contexts if translations
    were saved in regular variables. With functions it seems to be ok. Better solutions are welcome. """

    def unknown_error(self):
        return QCoreApplication.translate("unknown_error", "Tuntematon virhe: ")

    def date_not_found_error(self):
        return QCoreApplication.translate("datenotfound_error", "Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                           "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.\n\nVirheen kuvaus:\n")

    def end_date_warning(self):
        return QCoreApplication.translate("enddate_warning", "Lopetus päivämäärä ei saa edeltää aloitus päivämäärää")

    def start_end_date_warning(self):
        return QCoreApplication.translate("startenddate_warning","Aloitus ja lopetuspäivämäärät eivät saa olla samoja")

    def set_apikey_message(self):
        return QCoreApplication.translate("setapikeymessage", "Tunnisteavainta ei ole maaritetty. Aseta se valikossa Tiedosto->Aseta tunnisteavain")

    def about_dialog(self):
        return QCoreApplication.translate("about_description", "Yksinkertainen sovellus ilmatieteenlaitoksen säähavaintodatan lataamiseen.\nJos ohjelma lakkaa toimimasta, voit ottaa yhteyttä\n\nTuomas Salmi, 2015\nhttp://tumetsu.github.io/Ilmatieteenlaitoksen-saadata-lataaja\nsalmi.tuomas@gmail.com")

    def set_apikey_dialog(self):
        return QCoreApplication.translate("setapikeyinstruction", "Käyttääksesi sovellusta tarvitset ilmatieteenlaitoksen avoimen datan tunnisteavaimen.\nMene osoitteeseen http://ilmatieteenlaitos.fi/avoin-data saadaksesi lisätietoa avaimen hankkimisesta.\n\n"
                                         "Kun olet rekisteröitynyt ja saanut tekstimuotoisen tunnisteavaimen, kopioi se tähän:")

    def save_weatherdata_csv(self):
        return QCoreApplication.translate("save_weather_data", "Tallenna säädata csv-muodossa:")

    def downloading_weatherdata(self):
        return QCoreApplication.translate("downloading_weatherdata","Ladataan säädataa...")

    def weatherstation_error(self):
        return QCoreApplication.translate("weatherstationnotfound_error", "Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta Tiedosto->Tietoa valikosta.\n\nVirheen kuvaus:\n")

    def request_failed_error(self):
        return QCoreApplication.translate("requestfailed_error", "Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen?\n\nIlmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta Tiedosto->Aseta tunnisteavain.")


