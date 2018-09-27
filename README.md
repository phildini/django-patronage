# django-patreon
A django app for building patreon apps.

## Goal
To make it as easy as possible to build Django apps that reward the patrons of a Patreon creator with benefits that don't live on patreon.com

## Usage
1. `pipenv install https://github.com/phildini/django-patronage.git`
2. Add `patronage` to your `settings.INSTALLED_APPS`
3. Subclass `patronage.views.PatronageView`, and fill out the pieces needed. Look at what `PatronageView` does today, and see the reference examples below.

## References
- [Patron Box Office](https://github.com/phildini/patron-box-office) - the OG integration that inspired django-patronage. Needs to be updated to modern django-patronage conventions.
- [Patron Tube](https://github.com/phildini/patron-tube) - an integration for connecting Patreon tiers to Vimeo channels