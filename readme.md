# Project deprecated
FMI has released their own web-tool for downloading the weather data: http://ilmatieteenlaitos.fi/havaintojen-lataus#!/ 
I recommend using that tool instead of this application.

## ATTENTION!
FMI has recently changed their catalogue-service API essentially breaking the 0.15 versions of the downloader. Meanwhile you can still use older 0.14 version to download daily and real time weather observations. Until the downloader is fixed,
please use [Downloader version 0.14.2](https://github.com/Tumetsu/FMI-weather-downloader/releases/tag/v0.14.2)

Ilmatieteenlaitoksen säädatan lataaja / FMI Weather Downloader [![TravisCI](https://travis-ci.org/Tumetsu/FMI-weather-downloader.svg?branch=master)](https://travis-ci.org/Tumetsu/FMI-weather-downloader)
==============================

[Webpage of the application with downloads & guides](http://tumetsu.github.io/FMI-weather-downloader/)

![screenshot](http://imgur.com/JXkV9Li.png)

Simple application to provide a graphical user interface to download weather data from [Finnish Meteorological Institute's open data service](https://ilmatieteenlaitos.fi/avoin-data). The application was originally developed for [Lammi Biological Station's](http://www.helsinki.fi/lammi/) needs.

For more information about the usage and downloads, head to the website of the application or go directly to [download page](https://github.com/Tumetsu/Ilmatieteenlaitoksen-saadata-lataaja/releases)

Please note that this application **is not made by FMI!** It only uses the open data service provided by FMI.


Material
---------
The data downloaded by this program is directly from FMI's server. User should follow the [license of the data described in FMI's service](http://ilmatieteenlaitos.fi/avoin-data-lisenssi). When using the data in your work, research etc. it is your responsibility to follow the guidelines and licenses of the FMI.
FMI-Downloader is licensed as GNU GPL 3.0 license as required by Qt/PyQt licenses.

Install for development
--------------------

First install `Python 3.5.3 (32bit)`  and `virtualenv` package for it. Then in project root run:
```
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
```

On Windows, you can package the app to runnable exe with `cx_Freeze` tool by running following command in project root
after installing cx_freeze 5.0.1 from PIP. 

    python setup_win_cx.py build
The build folder can be transformed into install setup with. [InnoSetup](http://www.jrsoftware.org/isinfo.php) There is a script for it which
can be run in root directory to create a install exe to the build/ directory on Windows.

Translations
--------------
Translations are done by *pylupdate5* and *lrelease* tools which come with PyQt distribution. To update .ts translation files
run `pylupdate5 fmidownloader.pro` on root directory after adding new phrases to the messages.py. Launch *Qt Linguist* to edit
.ts files in `translations` directory. Finally in `translations` directory run `lrelease *.ts` to generate qm-files. App should pick correct translations now.

### Note
Translations are bit screwed up now because of messages.py and honestly my inexperience with PyQt i18n. If I have time I might clean them but
for now rather focus on more pressing issues. At the moment after doing changes to translations in Linguist, you have to remove `type="obsolete"` from
mainwindow_fi.ts file.

Thanks
---------
Thank you to John Loehr from University of Helsinki for proof reading the English translations as well as getting the application submitted to University's software portal.
