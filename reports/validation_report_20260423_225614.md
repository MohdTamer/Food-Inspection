# Validation Report

Generated: 2026-04-23 22:56:14

---

## 1. Basic Statistics

| Metric | Value |
|--------|-------|
| Rows | 196,825 |
| Columns | 59 |
| Fully duplicate rows | 149 |
| Duplicate Inspection IDs | 149 |

### Column Data Types

| Column | Type |
|--------|------|
| Inspection ID | `int64` |
| DBA Name | `str` |
| AKA Name | `str` |
| License # | `float64` |
| Facility Type | `str` |
| Risk | `str` |
| Address | `str` |
| City | `str` |
| State | `str` |
| Zip | `float64` |
| Inspection Date | `datetime64[us]` |
| Inspection Type | `str` |
| Results | `str` |
| Violations | `str` |
| Latitude | `float64` |
| Longitude | `float64` |
| Location | `str` |
| Historical Wards 2003-2015 | `float64` |
| Zip Codes | `float64` |
| Community Areas | `float64` |
| Census Tracts | `float64` |
| Wards | `float64` |
| BL_ID | `str` |
| BL_LICENSE_ID | `float64` |
| ACCOUNT NUMBER | `float64` |
| SITE NUMBER | `float64` |
| BL_LEGAL_NAME | `str` |
| BL_DBA_NAME | `str` |
| BL_ADDRESS | `str` |
| BL_CITY | `str` |
| BL_STATE | `str` |
| BL_ZIP_CODE | `float64` |
| WARD | `float64` |
| PRECINCT | `float64` |
| WARD PRECINCT | `str` |
| POLICE DISTRICT | `float64` |
| COMMUNITY AREA | `float64` |
| COMMUNITY AREA NAME | `str` |
| NEIGHBORHOOD | `str` |
| LICENSE CODE | `float64` |
| LICENSE DESCRIPTION | `str` |
| BUSINESS ACTIVITY ID | `str` |
| BUSINESS ACTIVITY | `str` |
| LICENSE NUMBER | `float64` |
| APPLICATION TYPE | `str` |
| APPLICATION CREATED DATE | `str` |
| APPLICATION REQUIREMENTS COMPLETE | `str` |
| PAYMENT DATE | `str` |
| CONDITIONAL APPROVAL | `str` |
| LICENSE TERM START DATE | `str` |
| LICENSE TERM EXPIRATION DATE | `str` |
| LICENSE APPROVED FOR ISSUANCE | `str` |
| DATE ISSUED | `str` |
| LICENSE STATUS | `str` |
| LICENSE STATUS CHANGE DATE | `str` |
| SSA | `float64` |
| BL_LATITUDE | `float64` |
| BL_LONGITUDE | `float64` |
| BL_LOCATION | `str` |

### Missing Values

| Column | Missing Count | Missing % |
|--------|---------------|-----------|
| Historical Wards 2003-2015 | 196,825 | 100.0% |
| Zip Codes | 196,825 | 100.0% |
| Community Areas | 196,825 | 100.0% |
| Census Tracts | 196,825 | 100.0% |
| Wards | 196,825 | 100.0% |
| APPLICATION CREATED DATE | 178,239 | 90.56% |
| LICENSE STATUS CHANGE DATE | 155,935 | 79.23% |
| SSA | 134,988 | 68.58% |
| Violations | 52,266 | 26.55% |
| BUSINESS ACTIVITY ID | 20,600 | 10.47% |
| BUSINESS ACTIVITY | 20,600 | 10.47% |
| NEIGHBORHOOD | 11,796 | 5.99% |
| COMMUNITY AREA | 11,567 | 5.88% |
| COMMUNITY AREA NAME | 11,567 | 5.88% |
| BL_LATITUDE | 11,180 | 5.68% |
| BL_LONGITUDE | 11,180 | 5.68% |
| BL_LOCATION | 11,180 | 5.68% |
| PAYMENT DATE | 10,996 | 5.59% |
| PRECINCT | 10,621 | 5.4% |
| POLICE DISTRICT | 10,451 | 5.31% |
| LICENSE APPROVED FOR ISSUANCE | 10,320 | 5.24% |
| WARD | 10,244 | 5.2% |
| WARD PRECINCT | 10,236 | 5.2% |
| APPLICATION REQUIREMENTS COMPLETE | 9,827 | 4.99% |
| BL_ZIP_CODE | 9,796 | 4.98% |
| LICENSE TERM START DATE | 9,761 | 4.96% |
| LICENSE NUMBER | 9,715 | 4.94% |
| LICENSE TERM EXPIRATION DATE | 9,714 | 4.94% |
| BL_ID | 9,698 | 4.93% |
| BL_LICENSE_ID | 9,698 | 4.93% |
| ACCOUNT NUMBER | 9,698 | 4.93% |
| SITE NUMBER | 9,698 | 4.93% |
| BL_LEGAL_NAME | 9,698 | 4.93% |
| BL_DBA_NAME | 9,698 | 4.93% |
| BL_ADDRESS | 9,698 | 4.93% |
| BL_CITY | 9,698 | 4.93% |
| BL_STATE | 9,698 | 4.93% |
| LICENSE CODE | 9,698 | 4.93% |
| LICENSE DESCRIPTION | 9,698 | 4.93% |
| APPLICATION TYPE | 9,698 | 4.93% |
| CONDITIONAL APPROVAL | 9,698 | 4.93% |
| DATE ISSUED | 9,698 | 4.93% |
| LICENSE STATUS | 9,698 | 4.93% |
| Facility Type | 4,768 | 2.42% |
| AKA Name | 2,458 | 1.25% |
| Latitude | 690 | 0.35% |
| Longitude | 690 | 0.35% |
| Location | 690 | 0.35% |
| City | 139 | 0.07% |
| Risk | 69 | 0.04% |
| Zip | 50 | 0.03% |
| State | 42 | 0.02% |
| License # | 17 | 0.01% |
| Inspection Type | 1 | 0.0% |

---

## 2. Domain Quality Checks

⚠️ **4 issue(s) found.**

| Field | Issue | Count | Sample |
|-------|-------|-------|--------|
| Longitude | Outside Chicago range [-87.9, -87.5] | 2,626 | — |
| State | Non-IL values found | 3 | IN, NY, WI |
| City | Non-CHICAGO values found (67 unique) | 67 | GRIFFITH, NEW YORK, SCHAUMBURG, ELMHURST, NEW HOLSTEIN |
| Zip | Malformed zip codes (expected 5 digits) | 112 | 60613.0, 60666.0, 60629.0, 60618.0, 60641.0 |

---

## 3. Great Expectations Suite

**Overall Result: ❌ FAILED**

| Passed | Failed | Total |
|--------|--------|-------|
| 8 | 7 | 15 |

### Expectation Results

| Status | Expectation | Column | Unexpected Count | Sample |
|--------|-------------|--------|-----------------|--------|
| ❌ | `expect_table_columns_to_match_set` | table-level | — | — |
| ✅ | `expect_table_row_count_to_be_between` | table-level | — | — |
| ✅ | `expect_column_values_to_not_be_null` | Inspection ID | — | — |
| ❌ | `expect_column_values_to_be_unique` | Inspection ID | 298 | 2286181, 2286112, 2286143 |
| ✅ | `expect_column_values_to_not_be_null` | DBA Name | — | — |
| ✅ | `expect_column_values_to_not_be_null` | Inspection Date | — | — |
| ✅ | `expect_column_values_to_not_be_null` | Results | — | — |
| ✅ | `expect_column_values_to_be_in_set` | Results | — | — |
| ❌ | `expect_column_values_to_not_be_null` | Risk | 69 | nan, nan, nan |
| ✅ | `expect_column_values_to_be_in_set` | Risk | — | — |
| ✅ | `expect_column_values_to_be_between` | Latitude | — | — |
| ❌ | `expect_column_values_to_be_between` | Longitude | 2626 | -87.91442843927047, -87.91442843927047, -87.91442843927047 |
| ❌ | `expect_column_values_to_match_regex` | Zip | 196775 | 60613.0, 60666.0, 60629.0 |
| ❌ | `expect_column_values_to_be_in_set` | State | 3 | IN, NY, WI |
| ❌ | `expect_column_values_to_be_in_set` | City | 700 | chicago, chicago, Chicago |
