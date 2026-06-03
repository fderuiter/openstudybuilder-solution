# USDM Mapping

## FS-USDM-Mapping-010 [`URS-USDM`]

The USDM mapping module translates study definitions from the native domain models into the CDISC USDM standard JSON schema.

### Test coverage

| Test File                                                    | Test Function                               |
| ------------------------------------------------------------ | ------------------------------------------- |
| tests/integration/api/ddf/test_usdm_mappings.py              | test_ddf_study                              |


# SDTM Listings

## FS-SDTM-Listings-010 [`URS-SDTM`]

The SDTM listing module exports study design concepts into standard SDTM tables such as Trial Arms (TA) and Trial Summary (TS).

### Test coverage

| Test File                                                            | Test Function                               |
| -------------------------------------------------------------------- | ------------------------------------------- |
| tests/integration/api/study_design_listings/test_sdtm_listings_ta.py | test_ta_listing                             |
| tests/integration/api/study_design_listings/test_sdtm_listings_ts.py | test_ts_listing                             |
| tests/integration/api/study_design_listings/test_sdtm_listings_te.py | test_te_listing                             |
| tests/integration/api/study_design_listings/test_sdtm_listings_tv.py | test_tv_listing                             |


# CTR XML Service

## FS-CTR-XML-010 [`URS-CTR`]

The CTR module generates an ODM XML file with specific extensions to meet the CTR compliance requirements.

### Test coverage

| Test File                                                    | Test Function                               |
| ------------------------------------------------------------ | ------------------------------------------- |
| tests/integration/services/test_ctr_odm_xml.py               | test_xml_response                           |
