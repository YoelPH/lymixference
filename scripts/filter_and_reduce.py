"""
Load CSV data containing lymphatic involvement of head and neck cancer patients
and keep only those with oral cavity tumors (i.e., specific ICD codes).
Further we reduce the ICD codes for all subsites except larynx to only numbers before the dot
The reason is a lack of data for other subsites. (Note for C32.2 we only have 15 patients as well! but split it according to Panos)
"""
import argparse
from pathlib import Path
from lyscripts.utils import load_yaml_params
import pandas as pd


ORAL_CAVITY_ICD_CODES = {
    "tongue": [
        "C02",
        "C02.0",
        "C02.1",
        "C02.2",
        "C02.3",
        "C02.4",
        "C02.8",
        "C02.9",
    ],
    "gums and cheeks": [
        "C03",
        "C03.0",
        "C03.1",
        "C03.9",
        "C06",
        "C06.0",
        "C06.1",
        "C06.2",
        "C06.8",
        "C06.9",
    ],
    "floor of mouth": [
        "C04",
        "C04.0",
        "C04.1",
        "C04.8",
        "C04.9",
    ],
    "palate": ["C05", "C05.0", "C05.1", "C05.2", "C05.8", "C05.9",],
    # "salivary glands": ["C08", "C08.0", "C08.1", "C08.9",],
}
OROPHARYNX_ICD_CODES = {
    "base of tongue": [
        "C01",
        "C01.0",
        "C01.1",
        "C01.2",
        "C01.8",
        "C01.9",
    ],
    "tonsil": [
        "C09",
        "C09.0",
        "C09.1",
        "C09.8",
        "C09.9",
    ],
    "general": [
        "C10",
        "C10.0",
        "C10.1",
        "C10.2",
        "C10.3",
        "C10.4",
        "C10.8",
        "C10.9",
    ],
}
HYPOPHARYNX_ICD_CODES = {
    "pyriform sinus": [
        "C12",
    ],
    "general": [
        "C13",
        "C13.0",
        "C13.1",
        "C13.2",
        "C13.8", #overlapping lesion of hypopharynx might not be optimal for mixture model
        "C13.9",
    ],
}
LARYNX_ICD_CODES = {
    "glottis": [
        "C32.0"
    ],
    "supraglottis": [
        "C32.1"
    ],
    "subglottis": [
        "C32.2"]
    #32.9 larynx unspecified, 32.8 overlapping lesions of larynx are not being used
    #C32 is also discarded as we do not know which sub-subsite it is from
}
#NOTE: Lip C00 has only one patient --> Discarded

icd_codes = []

# Add ICD codes from ORAL_CAVITY_ICD_CODES
for icd_list in ORAL_CAVITY_ICD_CODES.values():
    for icd in icd_list:
        icd_codes.append(icd)

# Add ICD codes from OROPHARYNX_ICD_CODES
for icd_list in OROPHARYNX_ICD_CODES.values():
    for icd in icd_list:
        icd_codes.append(icd)

# Add ICD codes from HYPOPHARYNX_ICD_CODES
for icd_list in HYPOPHARYNX_ICD_CODES.values():
    for icd in icd_list:
        icd_codes.append(icd)

# Add ICD codes from LARYNX_ICD_CODES
# for icd_list in LARYNX_ICD_CODES.values():
#     for icd in icd_list:
#         icd_codes.append(icd)

def _add_arguments(parser: argparse.ArgumentParser):
    """Add arguments to a ``subparsers`` instance and run its main function when chosen.

    This is called by the parent module that is called via the command line.
    """
    parser.add_argument(
        "-i", "--input", type=Path, required=True,
        help="Path to training data files"
    )

    parser.add_argument(
        "-p", "--params", default="./params.yaml", type=Path,
        help="Path to parameter file."
    )
    parser.add_argument("--output", type=Path, help="Output CSV file")

    parser.set_defaults(run_main=main)


def main(args: argparse.Namespace) -> None:
    
    params = load_yaml_params(args.params)
    args = parser.parse_args()
    patient_data = pd.read_csv(args.input, header=[0, 1, 2])
    is_relevant = patient_data["tumor", "1", "subsite"].isin(icd_codes)
    relevant_data = patient_data[is_relevant]
    #filter T0 and T1 glottis which have no involvement by definition
    glottis_selected_indices = (relevant_data['tumor']['1']['subsite'] == 'C32.0') & (relevant_data['tumor']['1']['t_stage'].isin([0, 1]))
    relevant_data = relevant_data.loc[~glottis_selected_indices]
    #filter empty patient(s)
    relevant_data = relevant_data.loc[~(relevant_data['max_llh']['ipsi'].isna().sum(axis = 1) == 16)]

    #reduce ICD codes
    relevant_data.loc[~(relevant_data['tumor']['1']['subsite'].str.startswith(('C32'))), ('tumor', '1', 'subsite')] = (
    relevant_data.loc[~(relevant_data['tumor']['1']['subsite'].str.startswith(('C32'))), ('tumor', '1', 'subsite')].str.replace(r'\..*', '', regex=True))
    
    #set LNL VI as False for Oropharynx and Oral Cavity patients (all patients have a None entry which will be marginalized over)
    icd_no_VI = ['C01','C02','C03','C04','C05','C06','C09','C10']
    relevant_data.loc[relevant_data[('tumor', '1', 'subsite')].isin(icd_no_VI),('max_llh', 'ipsi', 'VI')] = False
    
    relevant_data.to_csv(args.output, index=False)



    icd_df = pd.DataFrame(icd_codes, columns=['icd codes'])
    icd_df.to_csv(params['general']['data_folder'] + '/icds.csv', index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    _add_arguments(parser)

    args = parser.parse_args()
    args.run_main(args)

