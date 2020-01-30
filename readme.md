# Meningioma.app

<img src="static/android-chrome-192x192.png?raw=true" align="left" height="110" width="110" hspace="10">

[Meningioma.app](https://meningioma.app/) is the companion app to our paper,
"Individual-patient prediction of meningioma malignancy and
survival using the Surveillance, Epidemiology, and End Results
database". We strongly encourage users to read the (open access)
paper to get a better understanding of the interpretation and
limitations of the models included in this app: https://www.nature.com/articles/s41746-020-0219-5.
The app provides predictions of tumour behaviour and
patient-specific survival estimates on the basis of a set of basic
clinical variables. The models presented here fall under the
"Development Stage" of
<a href="https://www.ncbi.nlm.nih.gov/pubmed/28230847">Woo et al.'s framework of levels of
evidence for predictive
biomarkers</a>
and therefore will require further prospective validation to
demonstrate true clinical utility. Our intention with the current
app release is to give readers the ability to evaluate and probe
these models for insights, whether with past historical cases,
current, or hypothetical patients. We do however emphasise that at
the current time the models should not be used to guide treatment
decisions. If you are interested in undertaking prospective
validation studies or have access to large datasets of imaging or
molecular markers on which you would like to apply similar
methods, please do not hesitate to contact us for potential
collaborations.

## Installation

[Meningioma.app](https://meningioma.app/) runs in the browser, but it can also be installed on IOS (iPhone/iPad) or Android devices (see help menu at top left). Note: The app is optimised for smartphones and an internet connection is always required. If you'd like to run your own instance or re-use part of this code for your own project, the server-side backend is a regular [Flask](https://github.com/pallets/flask) app running on Gunicorn/NGINX. The frontend is a progressive web app built with [Onsen UI](https://github.com/OnsenUI/OnsenUI).

## Screenshots

![meningioma.app](static/screenshot.png?raw=true)
