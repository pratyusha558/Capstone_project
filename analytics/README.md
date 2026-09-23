# Titanic Analytics & Machine Learning

## Project Overview

This project analyzes the Titanic dataset using Exploratory Data Analysis (EDA), preprocessing, classification, regression, hyperparameter tuning, and model evaluation.

The main goal is to understand the factors related to passenger survival and build machine learning models to predict survival. A separate regression model is also used to predict passenger fare.

---

## Dataset

The Titanic dataset contains information about passengers, including:

* Passenger class (`pclass`)
* Age (`age`)
* Gender (`sex`)
* Number of siblings/spouses (`sibsp`)
* Number of parents/children (`parch`)
* Fare (`fare`)
* Port of embarkation (`embarked`)
* Survival status (`survived`)

The raw dataset was saved as `titanic.csv`.

---

## 1. Exploratory Data Analysis

The dataset was explored using:

* `df.info()`
* `df.describe()`
* Dataset shape
* Missing-value percentages
* Histograms
* Box plots
* Survival-rate analysis
* Correlation matrix and heatmap

The survival classes were imbalanced, with approximately 62% of passengers not surviving and 38% surviving.

### Univariate Analysis

Histograms and box plots were created for `age` and `fare`.

The fare distribution was right-skewed because the mean fare was higher than the median and mode. The box plot also showed several high-fare outliers.

### Bivariate Analysis

Survival rates were compared by:

* Sex
* Passenger class
* Sex and passenger class together

A correlation matrix was created using:

`survived`, `pclass`, `age`, `sibsp`, `parch`, and `fare`.

### Multivariate Analysis

Multiple charts were created to understand the relationship between passenger characteristics and survival.

The analysis showed that survival was associated with factors such as gender, passenger class, and fare.

---

## 2. Missing Value Handling

Missing values were handled based on their percentage and meaning.

* `age` → median imputation
* `embarked` → rows with missing values were removed
* `embark_town` → rows with missing values were removed
* `deck` → missing values were treated as a separate `"missing"` category

For machine learning, preprocessing was performed using a pipeline so that preprocessing steps were fitted only on the training data.

---

## 3. Feature Preprocessing

The classification models used:

### Numerical Features

* `pclass`
* `age`
* `sibsp`
* `parch`
* `fare`

Missing numerical values were handled using median imputation and numerical features were standardized using `StandardScaler`.

### Categorical Features

* `sex`
* `embarked`

Missing categorical values were handled using the most frequent value and categorical variables were encoded using `OneHotEncoder`.

A `ColumnTransformer` and `Pipeline` were used to combine these preprocessing steps with the machine learning models.

---

## 4. Classification Models

Three classifiers were trained using the same train/test split:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The data was split using stratification so that the proportion of survivors and non-survivors remained similar in the training and testing sets.

The Decision Tree was also visualized using `plot_tree`.

---

## 5. Classification Evaluation

The classifiers were evaluated using:

* Accuracy
* Precision
* Recall
* F1 Score
* AUC
* Confusion Matrix
* ROC Curve

The results were:

| Model               | Accuracy | Precision |   Recall |       F1 |      AUC |
| ------------------- | -------: | --------: | -------: | -------: | -------: |
| Logistic Regression | 0.808989 |  0.783333 | 0.691176 | 0.734375 | 0.860963 |
| Decision Tree       | 0.808989 |  0.814815 | 0.647059 | 0.721311 | 0.856016 |
| Random Forest       | 0.820225 |  0.781250 | 0.735294 | 0.757576 | 0.817914 |

Random Forest achieved the highest accuracy, recall, and F1 score among the three classifiers. Logistic Regression achieved the highest AUC.

---

## 6. Class Imbalance Handling

The dataset contained more non-survivors than survivors.

Three imbalance strategies were compared using Logistic Regression:

1. Baseline without imbalance handling
2. `class_weight='balanced'`
3. SMOTE oversampling

SMOTE was applied only to the training data to avoid data leakage.

| Method                | Precision |   Recall | F1 Score |
| --------------------- | --------: | -------: | -------: |
| Baseline              |  0.783333 | 0.691176 | 0.734375 |
| Class Weight Balanced |  0.718310 | 0.750000 | 0.733813 |
| SMOTE                 |  0.735294 | 0.735294 | 0.735294 |

SMOTE gave the highest F1 score and provided an equal balance between precision and recall. Class weighting gave higher recall, while the baseline gave higher precision.

---

## 7. Hyperparameter Tuning

`GridSearchCV` was used to tune the Random Forest model.

The following parameters were searched:

* `n_estimators`
* `max_depth`
* `max_features`

Five-fold cross-validation was used to compare different parameter combinations.

The Random Forest was created with `oob_score=True` so that the Out-of-Bag (OOB) score could be calculated.

The best parameter combination and OOB score were obtained from the GridSearchCV results.

---

## 8. Fare Prediction Using Linear Regression

A multivariate Linear Regression model was created to predict `fare` using the other available passenger features.

The model was evaluated using:

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)
* R²
* Adjusted R²

Results:

| Metric      |     Value |
| ----------- | --------: |
| MAE         | 21.098604 |
| RMSE        | 41.702105 |
| R²          |  0.348163 |
| Adjusted R² |  0.309130 |

The model explains about 34.8% of the variation in fare.

A residual plot was also created. The residuals showed increasing spread at higher predicted fare values, indicating some heteroscedasticity.

---

## 9. Final Model Comparison

Classification and regression metrics were kept as separate metric groups because they measure different types of model performance.

| Model               | Accuracy | Precision |   Recall |       F1 |      AUC |       MAE |      RMSE |       R² | Adjusted R² |
| ------------------- | -------: | --------: | -------: | -------: | -------: | --------: | --------: | -------: | ----------: |
| Logistic Regression | 0.808989 |  0.783333 | 0.691176 | 0.734375 | 0.860963 |         — |         — |        — |           — |
| Decision Tree       | 0.808989 |  0.814815 | 0.647059 | 0.721311 | 0.856016 |         — |         — |        — |           — |
| Random Forest       | 0.820225 |  0.781250 | 0.735294 | 0.757576 | 0.817914 |         — |         — |        — |           — |
| Linear Regression   |        — |         — |        — |        — |        — | 21.098604 | 41.702105 | 0.348163 |    0.309130 |

### Final Recommendation

Random Forest is recommended as the classification model because it achieved the highest accuracy (82.02%), recall (73.53%), and F1 score (75.76%). Its F1 score shows a good balance between precision and recall. Logistic Regression had the highest AUC at 0.861, while Decision Tree had the highest precision at 81.48%. Overall, Random Forest provided the strongest combination of the main classification metrics in this experiment.

---

## 10. Saving the Complete Pipeline

The complete Random Forest pipeline, including preprocessing and the trained model, was saved using Joblib.

```python
import joblib

joblib.dump(
    full_pipeline,
    'titanic_random_forest_pipeline.joblib'
)
```

The saved pipeline was then reloaded:

```python
loaded_pipeline = joblib.load(
    'titanic_random_forest_pipeline.joblib'
)
```

The reloaded pipeline was tested on raw input data and successfully produced predictions.

This confirms that the saved artifact can perform preprocessing and prediction end-to-end without manually preprocessing new data.

---

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* Imbalanced-learn
* Joblib
* Jupyter Notebook / VS Code

---

## Project Structure

```text
analytics/
│
├── titanic.csv
├── titanic_random_forest_pipeline.joblib
├── README.md
└── notebook / Python files
```

---

## How to Run

### 1. Install the required libraries

```bash
pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn joblib
```

### 2. Open the project

Open the `analytics` folder in VS Code.

### 3. Run the notebook or Python file

Run the cells/scripts in order to perform:

* Data loading
* EDA
* Data preprocessing
* Classification
* Imbalance handling
* Hyperparameter tuning
* Regression
* Model evaluation
* Pipeline saving

The saved `.joblib` file can then be loaded and used for predictions on new raw data.
