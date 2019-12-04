import os
from io import BytesIO

import joblib
import matplotlib
import matplotlib.patheffects as path_effects
import numpy as np
import pandas as pd
import seaborn as sns
from flask import Flask, make_response, request
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from matplotlib.figure import Figure
from sklearn import preprocessing

matplotlib.use('SVG')

# Get current working dir
cwd = os.path.dirname(__file__)

# Load classifiers and scaler
malign_clf = joblib.load(os.path.join(cwd, '2019-10-16_cal_clfblrrf2.pkl'))
malign_scaler = joblib.load(os.path.join(cwd, '2019-10-10_malignancy_scaler.pkl'))
malign_valid_dist = joblib.load(os.path.join(cwd, '2019-10-16_malignancy_yscore_valid_dist.pkl'))
surv_clf = joblib.load(os.path.join(cwd, '2019-10-16_survival_cox_clf.pkl'))

app = Flask(__name__)


@app.route('/plot/malignancy'
           '/<int(min=0, max=120):age>'
           '/<int(min=1, max=200):tumour_size>'
          )
def malignancy_plot(age, tumour_size):

    # Scale age and tumour_size (note: output is numpy array)
    age_tumour_size = [[age] + [tumour_size]]
    age_tumour_size_scaled = malign_scaler.transform(age_tumour_size)

    # Create malignancy feature array
    malign_features = [age_tumour_size_scaled[0].tolist()]

    # Predict malignancy: 0 benign, 1 non-benign
    yscore_cal = malign_clf.predict_proba(malign_features)
    yscore_nonbenign = np.round(yscore_cal[0][1]*100, 1)
    ypred_cal = np.array(yscore_cal[:, 1] > 0.05, dtype=int)[0]  # threshold = 5%
    
    # Select title and title colour
    red = '#CC333F'
    blue = '#1693A7'
    if ypred_cal == 0:
        title = 'Benign'
        title_colour = blue
    elif ypred_cal == 1:
        title = 'Borderline malignancy / Malignant'
        title_colour = red

    ##### Plot Figure #####
    sns.set(font_scale=1.2)
    sns.set_style('white',{'axes.linewidth': 2.5, 'axes.edgecolor': '#D3D3D3'})

    # Create plot
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)

    # Draw plot
    sns.kdeplot(malign_valid_dist, color='orange', shade=True,
                gridsize=500, bw='silverman', ax=ax)
    ax.vlines(yscore_nonbenign, 0, 0.10, color='#D70E08', zorder=10)  # prediction
    txt = ax.text(yscore_nonbenign, 0.11, '   ' + str(yscore_nonbenign) + '%', color='#D70E08',
             zorder=10, horizontalalignment='center')  # prediction label
    txt.set_path_effects([path_effects.withStroke(linewidth=3, foreground='w')])  # label outline
    ax.vlines(5, 0, 0.25, color='#cccccc', zorder=10, linestyles='dashed')  # threshold (5%)
    ax.set_title('Prediction: ' + title, color=title_colour, fontsize=14)

    ax.set_ylabel('Probability density', labelpad=10)
    ax.set_xlabel('Probability (%)', labelpad=10)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 0.4)
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(2)
    sns.despine(ax=ax)
    fig.set_tight_layout(True)

    # Write plot to SVG
    canvas = FigureCanvas(fig)
    output = BytesIO()
    # canvas.print_svg('test.svg')  # For testing fig output locally
    canvas.print_svg(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/svg+xml'
    return response


@app.route('/plot/survival'
           '/<int(min=0, max=120):age>'
           '/<int(min=1, max=200):tumour_size>'
           '/<int(min=0, max=1):sex>'
           '/<int(min=0, max=2):race>'
           '/<int(min=0, max=2):laterality>'
           '/<int(min=0, max=3):site>'
           '/<int(min=0, max=2):insurance>'
           '/<int(min=0, max=3):tumour_behaviour>'
           '/<int(min=0, max=1):sx_nosx>'
           '/<int(min=0, max=1):sx_gtr>'
           '/<int(min=0, max=1):sx_str>'
           '/<int(min=0, max=1):sx_resection>'
           '/<int(min=0, max=1):sx_partial>'
           '/<int(min=0, max=1):sx_local>'
           '/<int(min=0, max=1):sx_radical>'
           '/<int(min=0, max=1):sx_other>'
          )
def survival_plot(age, tumour_size, sex, race, laterality, site, insurance, tumour_behaviour,
                    sx_nosx, sx_gtr, sx_str, sx_resection,
                    sx_partial, sx_local, sx_radical, sx_other):

    # Rescale age and tumour size by a factor of 10
    age_dict = {'age_at_diagnosis': float(age)/10.}
    tumour_size_dict = {'cs_tumor_size': float(tumour_size)/10.}

    # Onehot encode input features as a Pandas Series
    # Sex: 0=Male, 1=Female
    if sex == 0:
        sex_Female = 0
    elif sex == 1:
        sex_Female = 1
    sex_dict = {'sex_Female': sex_Female}

    # Race: 0=White, 1=Black, 2=Other
    if race == 0:
        race_jrecode_White = 1
        race_jrecode_Other = 0
    elif race == 1:
        race_jrecode_White = 0
        race_jrecode_Other = 0
    elif race == 2:
        race_jrecode_White = 0
        race_jrecode_Other = 1
    race_dict = {'race_jrecode_White': race_jrecode_White, 'race_jrecode_Other': race_jrecode_Other}

    # Site: 0=Cerebral m, 1=Spinal m, 2=Other, 3=Meninges NOS
    if site == 0:
        primary_site_jrecode_Meninges_NOS = 0
        primary_site_jrecode_Spinal_meninges = 0
        primary_site_jrecode_Other = 0
    elif site == 1:
        primary_site_jrecode_Meninges_NOS = 0
        primary_site_jrecode_Spinal_meninges = 1
        primary_site_jrecode_Other = 0
    elif site == 2:
        primary_site_jrecode_Meninges_NOS = 0
        primary_site_jrecode_Spinal_meninges = 0
        primary_site_jrecode_Other = 1
    elif site == 3:
        primary_site_jrecode_Meninges_NOS = 0
        primary_site_jrecode_Spinal_meninges = 0
        primary_site_jrecode_Other = 1
    site_dict = {'primary_site_jrecode_Meninges NOS': primary_site_jrecode_Meninges_NOS,
                 'primary_site_jrecode_Spinal meninges': primary_site_jrecode_Spinal_meninges,
                 'primary_site_jrecode_Other': primary_site_jrecode_Other}

    # Laterality: 0=Not bilateral, 1=Midline, 2=Bilateral
    if laterality == 0:
        laterality_jrecode_Bilateral = 0
        laterality_jrecode_Midline = 0
    elif laterality == 1:
        laterality_jrecode_Bilateral = 0
        laterality_jrecode_Midline = 1
    elif laterality == 2:
        laterality_jrecode_Bilateral = 1
        laterality_jrecode_Midline = 0
    laterality_dict = {'laterality_jrecode_Bilateral': laterality_jrecode_Bilateral,
                       'laterality_jrecode_Midline': laterality_jrecode_Midline}

    # Insurance: 0=Insured, 1=Uninsured, 2=Unknown
    if insurance == 0:
        insurance_jrecode_Uninsured = 0
        insurance_jrecode_Unknown = 0
    elif insurance == 1:
        insurance_jrecode_Uninsured = 1
        insurance_jrecode_Unknown = 0
    elif insurance == 2:
        insurance_jrecode_Uninsured = 0
        insurance_jrecode_Unknown = 1
    insurance_dict = {'insurance_jrecode_Uninsured': insurance_jrecode_Uninsured,
                      'insurance_jrecode_Unknown': insurance_jrecode_Unknown}

    # Tumour behaviour: 0=Unknown, 1=Benign m, 2=Borderline malignancy, 3=Malignant
    if tumour_behaviour == 0:
        behavior_code_Malignant = 0
        behavior_code_Borderline_malignancy = 0
    elif tumour_behaviour == 1:
        behavior_code_Malignant = 0
        behavior_code_Borderline_malignancy = 0
    elif tumour_behaviour == 2:
        behavior_code_Malignant = 0
        behavior_code_Borderline_malignancy = 1
    elif tumour_behaviour == 3:
        behavior_code_Malignant = 1
        behavior_code_Borderline_malignancy = 0
    tumour_behaviour_dict = {'behavior_code_Malignant': behavior_code_Malignant,
                             'behavior_code_Borderline malignancy': behavior_code_Borderline_malignancy}

    # Surgery
    no_sx_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    gtr_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 1}
    str_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 1, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    resection_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 1,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    partial_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 1,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    local_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 1,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    radical_dict = {'surgery_jrecode_Other surgery': 0, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 1, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    other_dict = {'surgery_jrecode_Other surgery': 1, 'surgery_jrecode_20: Local excision': 0,
    'surgery_jrecode_21: Subtotal resection (brain)': 0, 'surgery_jrecode_22: Resection (spinal cord or nerve)': 0,
    'surgery_jrecode_30: Radical': 0, 'surgery_jrecode_40: Partial resection of lobe': 0,
    'surgery_jrecode_55: Gross total resection (lobectomy)': 0}
    surgery_coding = {
        'nosx': ('No surgery', no_sx_dict),  # 0
        'gtr': ('Gross total resection (lobectomy)', gtr_dict),  # 6
        'str': ('Subtotal resection (brain)', str_dict),  # 2
        'resection': ('Resection (spinal cord or nerve)', resection_dict),  # 3
        'partial': ('Partial resection of lobe', partial_dict),  # 5
        'local': ('Local excision', local_dict),  # 1
        'radical': ('Radical', radical_dict),  # 4
        'other': ('Other surgery', other_dict),  # 7
    }
    # dict of sx key and 0 or 1 value indicating state of switch
    sx_args = {'nosx': sx_nosx,
               'gtr': sx_gtr,
               'str': sx_str,
               'resection': sx_resection,
               'partial': sx_partial,
               'local': sx_local,
               'radical': sx_radical,
               'other': sx_other}
    # list of tuples of (Title, sx feature array) for each surgery to plot
    sx_to_plot = []
    for sx_name, sx_bool in sx_args.items():
        if sx_bool == 1:
            sx_to_plot.append(surgery_coding[sx_name])

    # Reason no surgery dicts
    nosx_contraindicated_dict = {'surgery_status_jrecode_Not recommended, contraindicated': 1,
                                 'surgery_status_jrecode_Recommended but not performed, patient refused': 0,
                                 'surgery_status_jrecode_Recommended but not performed, unknown reason': 0}
    nosx_ptrefused_dict = {'surgery_status_jrecode_Not recommended, contraindicated': 0,
                           'surgery_status_jrecode_Recommended but not performed, patient refused': 1,
                           'surgery_status_jrecode_Recommended but not performed, unknown reason': 0}
    sxother_dict = {'surgery_status_jrecode_Not recommended, contraindicated': 0,
                           'surgery_status_jrecode_Recommended but not performed, patient refused': 0,
                           'surgery_status_jrecode_Recommended but not performed, unknown reason': 0}


    # list of tuples of (Title, complete feature array) for each surgery to plot
    feature_arrays_to_plot = []
    for sx in sx_to_plot:
        title = sx[0]
        sx_features = sx[1]

        if title == 'No surgery':
            title1 = 'No surgery (contraindicated)'
            # features1 = [[age] + [tumour_size] + sexvar + racevar +
            #               sitevar + lateralityvar + sx_features + [0, 1, 0]]
            features1 = {**age_dict, **tumour_size_dict, **tumour_behaviour_dict, **sex_dict, **race_dict,
                         **site_dict, **laterality_dict, **insurance_dict, **sx_features, **nosx_contraindicated_dict}
            title2 = 'No surgery (patient refused)'
            features2 = {**age_dict, **tumour_size_dict, **tumour_behaviour_dict, **sex_dict, **race_dict,
                         **site_dict, **laterality_dict, **insurance_dict, **sx_features, **nosx_ptrefused_dict}
            title3 = 'No surgery (not recommended)'
            features3 = {**age_dict, **tumour_size_dict, **tumour_behaviour_dict, **sex_dict, **race_dict,
                         **site_dict, **laterality_dict, **insurance_dict, **sx_features, **sxother_dict}
            feature_arrays_to_plot.append((title1, features1))
            feature_arrays_to_plot.append((title2, features2))
            feature_arrays_to_plot.append((title3, features3))
        else:
            features = {**age_dict, **tumour_size_dict, **tumour_behaviour_dict, **sex_dict, **race_dict,
                         **site_dict, **laterality_dict, **insurance_dict, **sx_features, **sxother_dict}
            feature_arrays_to_plot.append((title, features))

    # list of tuples of (Title, results)
    surv_preds_to_plot = []
    for sx in feature_arrays_to_plot:
        title = sx[0]
        features = sx[1]
        surv_pred = surv_clf.predict_survival_function(pd.Series(features, dtype=float)).T.values[0]
        surv_preds_to_plot.append((title, surv_pred))

    ###### Plot Figure #####
    sns.set(font_scale=1.2)
    sns.set_style('white',{'axes.linewidth': 2.5, 'axes.edgecolor': '#D3D3D3'})
    sns.set_palette('colorblind')
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)

    for title, surv_pred in surv_preds_to_plot:
        ax.step(np.arange(len(surv_pred)), surv_pred*100, where="post", label=title, lw=2)
    ax.legend(loc='lower left', borderaxespad=0.,  prop={'size': 12})

    ax.set_ylabel('Probability of survival (%)', size=15)
    ax.set_xlabel('Time (months)', size=15)
    ax.title.set_position([.5, 1.05])

    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(2)
    sns.despine(ax=ax)
    ax.yaxis.grid(color='#D3D3D3', linestyle='--')
    fig.set_tight_layout(True)


    ## Write plot to SVG
    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_svg(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/svg+xml'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
