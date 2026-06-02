# Feature Name

## FS-FeatureName-Action-010 [`URS-Reference`]

Description of the feature.

### Request

Details about the request.

### Response

Details about the response.

### Validation Rules

- **Data Integrity**
  - [Example Rule 1] A study cannot be locked if the protocol version is missing.
- **Business Logic**
  - [Example Rule 2] Project ID must exist in the Project Registry.

### Test coverage

| Test File                    | Test Function                              |
| ---------------------------- | ------------------------------------------ |
| tests/v1/test_api_feature.py | test_feature_validation_rule_1             |
| tests/v1/test_api_feature.py | test_feature_validation_rule_2             |
