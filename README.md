# Food-Inspection

Let's keep Chicago eating safely, one data point at a time. This project replaces random inspection rotations with a predictive model that identifies high-risk establishments before an inspector even walks through the door.

---

## Team: Science the Data (Team 6)

Developed by the brilliant minds at **Cairo University - Faculty of Engineering** under the **Credit Hour System** for the **Data Science (CMPS344)** course:

- **Omar Mahmoud Demerdash** (1220134)
- **Amr Ehab Mokhtar** (4230159)
- **Mohamed Tamer** (4230189)
- **Omar Gamal** (1220017)

For a deep dive into our methodology, please refer to the document **Science the Data (Team 6).pdf**.

---

## Project Description

Chicago has over 15,000 food establishments and a finite number of health inspectors. Currently, inspections occur roughly every 6 months regardless of actual risk. Our model flips the script by predicting which restaurants are likely to fail, allowing the city to prioritize the highest-risk locations.

### Why This Matters (Stakeholders)

- **City Health Department**: Prioritizes the top 200 highest-risk locations to catch more violations per inspector day.
- **Restaurant Owners**: Provides an early warning to perform self-audits and avoid public closure notices or reputation damage.
- **Insurance & Franchise Operators**: Identifies high-risk branches within a chain to prevent costly food safety scandals.

---

## Setup Instructions

This project uses **Poetry** for dependency management and a **Makefile** to automate your life. Ensure you have **Python 3.13** installed.

### 1. Create the Environment

Initialize your virtual environment and select the correct Python interpreter:

```bash
make create_environment
```

### 2. Install Dependencies

Pull in all necessary libraries defined in the project:

```bash
make requirements
```

---

## How to Run

Once your environment is set up, use these commands to interact with the project:

| Action               | Command          |
| :------------------- | :--------------- |
| **Run Main Script**  | `make run`       |
| **Launch Dashboard** | `make dashboard` |
| **Run Unit Tests**   | `make test-unit` |
| **Check Linting**    | `make lint`      |
| **Auto-Format Code** | `make format`    |
| **Clean Pycache**    | `make clean`     |

---

## Data Overview

The model leverages three primary datasets from the **City of Chicago (2024)**:

1.  **Chicago Food Inspections** (Primary)
2.  **Chicago Business Licenses** (Supplementary)
3.  **Sanitation Complaints** (Supplementary)

### Key Engineered Features

Our "secret sauce" includes features like:

- `establishment_age_days`: Calculated from business license start dates.
- `fail rate last 3`: Captures recent compliance trends for a specific location.
- `violation count`: Number of distinct violations in the previous inspection.
- `inspection_type_encoded`: Prioritizes complaint-triggered inspections.

### Target Variable

The model predicts a binary outcome based on the `results` column:

- **Label 1 (Fail)**: Critical or serious violations.
- **Label 0 (Pass)**: Met standards or minor violations ("Pass w/ Conditions").

---
