from PyQt5.QtCore import QCoreApplication

class Messages:


    def __init__(self):
        self.START_END_DATE_WARNING = QCoreApplication.translate("startenddate_warning","Aloitus ja lopetuspäivämäärät eivät saa olla samoja")
        self.END_DATE_WARNING = QCoreApplication.translate("enddate_warning", "Lopetus päivämäärä ei saa edeltää aloitus päivämäärää")
        self.DATE_NOT_FOUND_ERROR = QCoreApplication.translate("datenotfound_error", "Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                                   "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.\n\nVirheen kuvaus:\n")
        self.UNKNOWN_ERROR = QCoreApplication.translate("unknown_error", "Tuntematon virhe: ")
        self.SET_APIKEY_DIALOG = QCoreApplication.translate("setapikeyinstruction", "Käyttääksesi sovellusta tarvitset ilmatieteenlaitoksen avoimen datan tunnisteavaimen.\nMene osoitteeseen http://ilmatieteenlaitos.fi/avoin-data saadaksesi lisätietoa avaimen hankkimisesta.\n\n"
                                                     "Kun olet rekisteröitynyt ja saanut tekstimuotoisen tunnisteavaimen, kopioi se tähän:")
        self.ABOUT_DESCRIPTION = QCoreApplication.translate("about_description", "Yksinkertainen sovellus ilmatieteenlaitoksen säähavaintodatan lataamiseen.\nJos ohjelma lakkaa toimimasta, voit ottaa yhteyttä\n\nTuomas Salmi, 2015\nhttps://github.com/Tumetsu/Ilmatieteenlaitoksen-saadata-lataaja\nsalmi.tuomas@gmail.com")

