# Repository Re-Curation Tools
This repository holds tools for updating DataCite metadata with new or revised content, i.e. re-curation.

# Environment

# Usage
## UpdateDataCiteMetadataSimple
### Usage
```
usage: updateDataCiteMetadata [-h] [-r REPOSITORY_ID] [-query QUERY] [-updateGroup UPDATEGROUP] [--countTargets] [--updateMetadata] [-limit LIMIT] [-auth AUTH]
                              [--loglevel {debug,info,warning}] [--logto FILE]

Update DataCite metadata with new content.

optional arguments:
  -h, --help            show this help message and exit
  -r REPOSITORY_ID, --repository_id REPOSITORY_ID
                        identifier for repository to update, id should be two strings separated by a dot, i.e. unavco.unavco
  -query QUERY, --query QUERY
                        query to add to URL to select records to update, i.e. publisher:UNAVCO (default is None)
  -updateGroup UPDATEGROUP, --updateGroup UPDATEGROUP
                        update group to select changes from metadataUpdates.csv
  --countTargets        Count target values in metadata without making changes (useful for debugging or testing updates)
  --updateMetadata      Update the metadata, the auth argument is required for this to happen
  -limit LIMIT, --limit LIMIT
                        limit the number of records to update, default is one record. Set hight for more records, i.e. 1000
  -auth AUTH, --auth AUTH
                        DataCite authorization token for repository to update
  --loglevel {debug,info,warning}
                        Logging level
  --logto FILE          Log file (will append to file if exists)
```

## UpdateDataCiteIdentifiers

### Usage
```
usage: updateDataCiteIdentifiers [-h] [-r REPOSITORY_ID] [-af AFFILIATIONFILE] [-target TARGET] [-idLookup IDLOOKUP] [--countTargets] [--updateMetadata]
                                 [-limit LIMIT] [-auth AUTH] [--loglevel {debug,info,warning}] [--logto FILE]

Update DataCite metadata with new identifiers.

optional arguments:
  -h, --help            show this help message and exit
  -r REPOSITORY_ID, --repository_id
	  identifier for repository to update, id should be two strings separated by a dot, i.e. unavco.unavco
  -af AFFILIATIONFILE, --affiliationFile AFFILIATIONFILE
      repository_id will be used to find a collectionContent file or enter name of file 
                        with one affiliation per line
  -target TARGET, --target TARGET
                        the target string to update wityh identifier, i.e. creators.name or creators.affiliation.name
  -idLookup IDLOOKUP, --idLookup IDLOOKUP
                        the complete path to a ROR lookup file (csv, tsv, or excel format)
  --countTargets        Count target values in metadata without making changes (useful for debugging or testing updates)
  --updateMetadata      Update the metadata, the auth argument is required for this to happen
  -limit LIMIT, --limit LIMIT
                        limit the number of affiliations to update, default is one record. Set high for more records, i.e. 100000
  -auth AUTH, --auth AUTH
                        DataCite authorization token for repository to update
  --loglevel {debug,info,warning}
                        Logging level
  --logto FILE          Log file (will append to file if exists)
```
  
  
### Arguments
### 
