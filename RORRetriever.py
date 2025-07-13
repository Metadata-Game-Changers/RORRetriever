import requests                     # for making web requests
import json                         # json reading and access
import pandas as pd                 # pandas for dataframe processing
from urllib.parse import quote      # URL encoding
import sys
import datetime
import argparse
import datetime
import logging
import os
import re

'''
usage: RORRetriever [-h] [-a [AFFILIATIONLIST [AFFILIATIONLIST ...]]] [-af AFFILIATIONFILENAME] [-ad AFFILIATIONDATA] [--noacronyms] [--max] [--details] [-o OUTPUTINTERVAL] [--loglevel {debug,info,warning}]
                    [--logto FILE]

search organization names and affiliations for RORs using the ROR Affiliation Strategy

optional arguments:
  -h, --help            show this help message and exit
  -a [AFFILIATIONLIST [AFFILIATIONLIST ...]], --affiliationList [AFFILIATIONLIST [AFFILIATIONLIST ...]]
                        a list of "affiliations in quotes"
  -af AFFILIATIONFILENAME, --affiliationFilename AFFILIATIONFILENAME
                        a file with one affiliation per line in current working directory
  -ad AFFILIATIONDATA, --affiliationData AFFILIATIONDATA
                        datafile (tsv, csv) with affiliations in cwd)
  --noacronyms          Exclude Acronym matches (default=False)
  --max                 Accept max score if no result chosen by ROR algorithm (more results and noise)
  --details             Show detailed response data (automatic for one ROR)
  -o OUTPUTINTERVAL, --outputInterval OUTPUTINTERVAL
                        For batch processing output results update interval default:20
  --loglevel {debug,info,warning}
                        Logging level
  --logto FILE          Log file (will overwrite if exists)
'''

def outputResults(tl: list,             # affiliation list input (list of dicts)
                  output: str,          # name of output file
                  cnt: int,             # number of RORs
                  writeHeader: bool):   # write header flag (true for first write)
    '''
        Create a dataframe from a list of dictionaries (tl) and output it to a file.
        Rows are output in sets with length = -o outputInterval. This prevents output
        from being lost if something goes wrong in long processing runs.
    '''
    #
    # The items that are defined in the dictionaries (in tl) will be used to create a dataframe
    # The columns that are defined depend on whether or nor RORs have been discovered. Defining the
    # complete set of columns here avoids an error caused by outputing data without all of the
    # columns defined. 
    #
    c_names = ['affiliation', 'searchString_Affiliation',
                   'ROR_Affiliation', 'organizationLookupName_Affiliation',
                   'country_Affiliation', 'match_Affiliation',
                   'chosen_Affiliation', 'score',
                   'numberOfResults_Affiliation', 'valid']

    df = pd.DataFrame(tl)                       # create the dataframe from the list of dicts

    if len(df.columns) < 9:                     # add columns if needed
        for c in ['searchString_Affiliation', 'ROR_Affiliation', 
                  'organizationLookupName_Affiliation', 'country_Affiliation',
                  'chosen_Affiliation']:
            df.insert(0, c, value='')           # insert empty text ('') row named c at position 0
        df.insert(0,'score',0)                  # insert empty numeric row for scores (default = 0)

    df.to_csv(output, sep='\t', index=False,                # output dataframe to tab delimited file
              encoding='utf-8', header=writeHeader,         # in append mode with header on first write
              mode = 'a', columns=c_names)

    lggr.info("{} new RORs written to {}".format(cnt,output))

def printResponse(df:pd.core.frame.DataFrame):
    '''
        Show response table on terminal with following fields:
        substring:      Search string (can be substring of complete affiliation)
        score:          Match score between 0 and 1 (1 is the best match chosen by algorithm)
        matchingType:   Method that found the match (provided by algorithm)
        chosen:         True for chosen ROR False for others
        organization:   Name of organization for ROR (should match substring)
        country:        Country of organization
    '''
    out_df = df[['substring','score','matching_type','chosen']]       
    out_df['ror'] = df['organization'].apply(lambda x: x['id'])
    out_df['organization'] = df['organization'].apply(lambda x: x['name'])
    out_df['country'] = df['organization'].apply(lambda x: x['country']['country_name'])
    pd.set_option('display.width', 1000)
    print(out_df.to_string(index=False))


def retrieveData(url:str                            # URL to search
                )->requests.models.Response:        # requests response
    '''
        read data for url, return response 
    '''
    lggr.debug(f"Retrieving Data URL: {URL}")

    try:
        response = requests.get(URL)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        lggr.warning(f'URL: {URL} Error: {err}')
        return None
    except requests.exceptions.ConnectionError as err:
        lggr.warning(f'URL: {URL} Error: {err}')
        return None
    except requests.exceptions.Timeout as err:
        lggr.warning(f'URL: {URL} Error: {err}')
        return None
    except requests.exceptions.TooManyRedirects as err:
        lggr.warning(f'URL: {URL} Error: {err}')
        return None
    except requests.exceptions.MissingSchema as err:
        lggr.warning(f'URL: {URL} Error: {err}')
        return None
    
    lggr.debug(f'Response length: {len(response.text)}')
    return response
#
# define command line options
# this also generates --help and error handling
#
commandLine = argparse.ArgumentParser(prog='RORRetriever',
                        description='search organization names and affiliations for RORs using the ROR Affiliation Strategy'
)
commandLine.add_argument('-a', "--affiliationList", nargs="*", type=str,
                        help='a list of "affiliations in quotes"',
)
commandLine.add_argument('-af', "--affiliationFilename",
                        type=str,
                        help='a file with one affiliation per line in current working directory',
)
commandLine.add_argument('-ac', "--affiliationColumn",
                        type=str,
                        help='name of affiliation column',
)
commandLine.add_argument('-ad', "--affiliationData",
                        type=str,
                        help='datafile (tsv, csv) with affiliations in cwd)',
)
commandLine.add_argument('--noacronyms', dest='noAcronyms', 
                        default=False, action='store_true',
                        help='Exclude Acronym matches (default=False)'
)
commandLine.add_argument('--max', dest='matchMax', 
                        default=False, action='store_true',
                        help='Accept max score if no result chosen by ROR algorithm (more results and noise)'
)
commandLine.add_argument('--details', dest='showDetails', 
                        default=False, action='store_true',
                        help='Show detailed response data (automatic for one ROR)'
)
commandLine.add_argument('-o', '--outputInterval', 
                        help='For batch processing output results update interval default:20',
                        type=int, default=20
)
commandLine.add_argument('--loglevel', default='info',
                    choices=['debug', 'info', 'warning'],
                    help='Logging level'
)
commandLine.add_argument('--logto', metavar='FILE',
                    help='Log file (will overwrite if exists)'
)
args = commandLine.parse_args()
#
# create logs
#
if args.logto:
    # Log to file
    logging.basicConfig(
        filename=args.logto, filemode='a',
        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        level=args.loglevel.upper(),
        datefmt='%Y-%m-%d %H:%M:%S')
else:
    # Log to stderr (default)
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        level=args.loglevel.upper(),
        datefmt='%Y-%m-%d %H:%M:%S')
        
lggr = logging.getLogger('RORRetriever')
#
# initialize affiliation input list
# 
input_l = []

if args.affiliationList:                   # a single affiliation is being retrieved
    input_l = args.affiliationList

if args.affiliationFilename:
    lggr.info(f'Searching {args.affiliationFilename} for affiliations with Affiliation Strategy')
    with open(args.affiliationFilename, 'r') as file:   # a file of affiliations one/line
        input_l = file.readlines()

if args.affiliationData:                            # affiliations in data file (tsv or csv)
                                                    # column named Affiliation/affiliation
    if '.csv' in args.affiliationData:                          # use extension to infer delimiter
        delimiter = ','
    elif '.tsv' in args.affiliationData:
        delimiter = '\t'
    data_df = pd.read_csv(args.affiliationData,sep=delimiter,encoding='utf-8')

    if args.affiliationData:
        columnName = args.affiliationColumn
        lggr.info(f'Affiliations in {args.affiliationColumn}')

    if 'Affiliation' in data_df.columns:
        columnName = 'Affiliation'
    elif 'affiliation' in data_df.columns:
        columnName = 'affiliation'
    else:
        lggr.warning(f'Affiliation or affiliation column must exist in data')
    
    input_l = data_df[columnName].unique().tolist()

lggr.info(f'{len(input_l)} Input Affiliations')

if args.matchMax:
    lggr.info(f'************** Best match is being found (may not be chosen by algorithm, score < 1.0)')

if args.noAcronyms:
    lggr.info(f'************** Acronyms are not being considered in the results.')

lggr.debug(f'Affiliation List: {input_l}')

current_time = datetime.datetime.now()
timestamp = "%i%0.2d%0.2d_%0.2d" % \
    (current_time.year, current_time.month, current_time.day, 
    current_time.hour)
#
# define output file name
#
outputFileName = 'AffiliationAPI_RORData__'+ timestamp +'.tsv'
writeHeader = True
#
# Create a list of dictionaries to create a dataframe from
#
ror_list = []
newRORCount = 0
#
# loop through affiliations in input_l
#
for i, affiliation in enumerate(input_l):       # loop affiliations in input_l
    if type(affiliation) != str:                # skip non-strings (NaN)
        continue
    affiliation = affiliation.replace('\n','').strip()

    if (i % args.outputInterval == 0) & (len(ror_list) > 0):              # output current results
        lggr.info("{} processed affiliation: {}".format(i,affiliation))
        outputResults(ror_list, outputFileName,newRORCount,writeHeader)
        writeHeader = False
        ror_list = []

    URL = 'https://api.ror.org/organizations?affiliation=' + quote(affiliation.encode('utf-8'))
    r = retrieveData(URL)

    if (r is None) or (r.status_code != 200):
        lggr.warning('****************** HTTP Error: {URL}')
        continue
    #
    # convert response to json
    #
    response = r.json()
    response_df = pd.DataFrame(response.get('items'))           # create response dataframe

    if (response['number_of_results'] == 0):                    # ROR search had no results
        ror_list.append({'affiliation':affiliation,             # set affiliation, numberOfResults, and match = 'No Result'
                    'numberOfResults_Affiliation':0,
                    'match_Affiliation':'No Result',
                    'valid':False})
        continue                                                # next affiliation

    acronymCount = len(response_df[response_df['matching_type']=='ACRONYM'])                # count Acronyms
    if (acronymCount == response['number_of_results']) and (args.noAcronyms is True):       # search result is all acronyms:
        ror_list.append({'affiliation':affiliation,              # set affiliation, numberOfResults, and match = 'No Result'
                    'numberOfResults_Affiliation':0,
                    'match_Affiliation':'No Result',
                    'valid':False})
        continue                                                # next affiliation

    if (len(input_l) == 1) or args.showDetails:                # if only one affiliation is being tested    
        printResponse(response_df)                              # or --response is set, print results

    if (args.noAcronyms is True):                           # remove acronym matches from response _df
        response_df = response_df[response_df['matching_type'] != 'ACRONYM']
    #
    # search for item chosen as best match be affiliation API
    #
    maxScore = response_df.score.max()                               # find maximum score
    if args.matchMax is False:
        chosen_df = response_df[response_df.chosen == True]          # create chosen dataframe where chosen = True
    else:
        chosen_df = response_df[response_df.score == maxScore]       # create chosen dataframe where score = maxScore

                                                                        # items can be chosen (chosenScore = 1) or, 
                                                                        # if --max is set the item with the max score is chosen
                                                                        # even if ROR algorithm did not chose item
    if len(chosen_df) > 0:
        newRORCount += len(chosen_df)                                   # count new RORs
        for i in chosen_df.index:                                       # add new RORs to ror_list
            ror_list.append({'affiliation':affiliation,
                                'searchString_Affiliation':chosen_df.loc[i,'substring'].replace('"',''),
                                'ROR_Affiliation':chosen_df.loc[i,'organization']['id'], 
                                'organizationLookupName_Affiliation':chosen_df.loc[i,'organization']['name'],
                                'chosen_Affiliation':chosen_df.loc[i,'chosen'], 
                                'score':chosen_df.loc[i,'score'],
                                'match_Affiliation': chosen_df.loc[i,'matching_type'],
                                'country_Affiliation':chosen_df.loc[i,'organization']['country']['country_name'],
                                'numberOfResults_Affiliation':response['number_of_results'],
                                'valid': True})
            lggr.debug(newRORCount,':', affiliation,'<'+response_df.loc[i,'substring']+'>',response_df.loc[i,'organization']['name'])
    else:           # No item choosen
        ror_list.append({'affiliation': affiliation,
                         'numberOfResults_Affiliation': response['number_of_results'],
                         'match_Affiliation': 'No Match', 'valid': False})        
#
# output final results
#
outputResults(ror_list, outputFileName, newRORCount, writeHeader)
lggr.info("{} {} RORs Found".format(outputFileName, newRORCount))

