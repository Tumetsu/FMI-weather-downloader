# Manual test plan
Eventually automatic test coverage is desirable to cover most of the application both in api and gui side of things but before that
goal is reached, some manual testing before each release is necessary. In this document is listed parts of the application manual tester should check
before each release. List is a guide line and a tool to remember to check most of important stuff before each release. As automatic testing coverage
improves, parts of this list may be removed.

Testing should be donw in freezed version of app to simulate better end user experience.

## Setup and menus
* Check that first time run works correctly when there is no existing application setting in the system.
	* You can clear QSettings by `.clear()` method.
* Verify that API-key can be set
* Verify that program notifies user of wrong api-key
* Verify that user can change language and translations change correctly
* Verify that About dialog displays everything correctly and links are working
* Verify that update dialog is run on start up by default and displays everything correctly
* Verify that app's version will be newer than previous release (required for update notifications to work)

## Download
* Download daily and realtime data from proper time spans from some stations
* Download daily and realtime data from time span where the beginning doesn't exist
* Download daily and realtime data from time span which contains no data and verify that a correct error message is shown
* Exceed query limit by doing long realtime queries and check that a proper error message is shown
* Verify that gui shows approriate error messages if invalid dates are set to date fields (red text in the bottom)
* Check that download and parsing progress bar has correct texts/translations
* Check that csv has data from expected range

