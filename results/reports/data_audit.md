# OncoTrace Data & Target Audit Report

- **Total Records:** 1904
- **Total Columns:** 693

## 1. Value Counts: overall_survival
```text
overall_survival
0    1103
1     801
```

## 2. Value Counts: death_from_cancer
```text
death_from_cancer
Living                  801
Died of Disease         622
Died of Other Causes    480
NaN                       1
```

## 3. Target Cross-Tabulation
Mapping `overall_survival` against `death_from_cancer` to deduce event encoding.
```text
death_from_cancer  Died of Disease  Died of Other Causes  Living  NaN
overall_survival                                                     
0                              622                   480       0    1
1                                0                     0     801    0
```

## 4. Mixed-Type Column Inspection
Investigating column indices 678, 688, 690, 692 for potential leakage or schema issues.
- **`rasgef1b_mut`** (Index 678):
  - Dtype: `object`
  - Missing: 0
  - Sample unique values: `['0', 'V418A', 'S343G', 'R140Q', 'X2_splice']`
- **`hras_mut`** (Index 688):
  - Dtype: `object`
  - Missing: 0
  - Sample unique values: `['0', 'Q61R', 'N86T']`
- **`smarcb1_mut`** (Index 690):
  - Dtype: `object`
  - Missing: 0
  - Sample unique values: `['0', 'D159N', 'I28L']`
- **`siah1_mut`** (Index 692):
  - Dtype: `object`
  - Missing: 0
  - Sample unique values: `['0', 'T249A']`

## 5. Patient IDs & Survival Time Anomalies
- Missing `patient_id`: 0
- Duplicate `patient_id`: 0
- Duplicate full rows: 0
- Negative survival months: 0
- Zero survival months: 1
