from PyQt5.QtCore import QCoreApplication

class Messages:
    """ To me this seems a bit like hack. This class has functions to get translated strings to be shown in UI. The
    reason for them being in functions is that apparently Qt translate will not work in multiple contexts if translations
    were saved in regular variables. With functions it seems to be ok. Better solutions are welcome. """

    @staticmethod
    def unknown_error():
        return QCoreApplication.translate("unknown_error", "Tuntematon virhe: ")

    @staticmethod
    def date_not_found_error():
        return QCoreApplication.translate("datenotfound_error", "Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                           "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.")

    @staticmethod
    def end_date_warning():
        return QCoreApplication.translate("enddate_warning", "Lopetus päivämäärä ei saa edeltää aloitus päivämäärää")

    @staticmethod
    def start_end_date_warning():
        return QCoreApplication.translate("startenddate_warning","Aloitus ja lopetuspäivämäärät eivät saa olla samoja")

    @staticmethod
    def set_apikey_message():
        return QCoreApplication.translate("setapikeymessage", "Tunnisteavainta ei ole maaritetty. Aseta se valikossa Tiedosto->Aseta tunnisteavain")

    @staticmethod
    def about_dialog():
        return QCoreApplication.translate("about_description", "Yksinkertainen sovellus ilmatieteenlaitoksen säähavaintodatan lataamiseen.\nJos ohjelma lakkaa toimimasta, voit ottaa yhteyttä\n\nTuomas Salmi, 2015\nhttp://tumetsu.github.io/Ilmatieteenlaitoksen-saadata-lataaja\nsalmi.tuomas@gmail.com")

    @staticmethod
    def set_apikey_dialog():
        return QCoreApplication.translate("setapikeyinstruction", "Käyttääksesi sovellusta tarvitset ilmatieteenlaitoksen avoimen datan tunnisteavaimen.\nMene osoitteeseen http://ilmatieteenlaitos.fi/avoin-data saadaksesi lisätietoa avaimen hankkimisesta.\n\n"
                                         "Kun olet rekisteröitynyt ja saanut tekstimuotoisen tunnisteavaimen, kopioi se tähän:")

    @staticmethod
    def save_weatherdata_csv():
        return QCoreApplication.translate("save_weather_data", "Tallenna säädata csv-muodossa:")

    @staticmethod
    def downloading_weatherdata():
        return QCoreApplication.translate("downloading_weatherdata","Ladataan säädataa...")

    @staticmethod
    def weatherstation_error():
        return QCoreApplication.translate("weatherstationnotfound_error", "Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta Tiedosto->Tietoa valikosta.\n\nVirheen kuvaus:\n")

    @staticmethod
    def request_failed_error():
        return QCoreApplication.translate("requestfailed_error", "Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen?\n\nIlmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta Tiedosto->Aseta tunnisteavain.")

    @staticmethod
    def query_limit_error():
        return QCoreApplication.translate("querylimit_error",
                                          "Ilmatieteenlaitoksen latausraja ylitetty.\nOlet tehnyt liikaa datapyyntöjä lyhyessä ajassa. Jatkaaksesi lataamista, odota {} sekuntia ennen seuraavaa datapyyntöä.")
