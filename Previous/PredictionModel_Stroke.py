import pandas as pd
import numpy as np
from numpy import percentile
from imblearn.over_sampling import SMOTE
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split

#importing our data set
df = pd.read_csv('healthcare-dataset-stroke-data.csv')

##pre-processing
#replace missing values in bmi column using using mean() imputation
df["bmi"].fillna(df["bmi"].mean(),inplace=True)

#drop rows with gender=other
df.drop(df.index[df["gender"]=="Other"], inplace=True)

#replace "children" values with "never_worked"
df["work_type"] = df["work_type"].replace(["children"], "Never_worked")

#rename the residence_type for consistency
df.rename(columns = {"Residence_type": "residence_type"}, inplace=True)

#change age column into integer from float
df["age"] = df["age"].astype("int")

#define categorical variables
cols = ["stroke", "gender", "hypertension", "heart_disease", "ever_married", "work_type", "residence_type", "smoking_status"]
df[cols] = df[cols].astype("category")

#drop id column
df.drop(["id"], axis="columns", inplace=True)


#creating a function to remove outliers
def remove_outliers(data):
    ##calculate interquartile range
    q25 = np.percentile(data, 25)
    q75 = np.percentile(data, 75)
    iqr = q75 - q25
    
    ##calculate lower and upper limits
    low_lim = q25 - (1.5 * iqr)
    up_lim = q75 + (1.5 * iqr)
    
    ##identify and remove outliers
    outliers = []
    for x in data:
        if x < low_lim:
            x = low_lim
            outliers.append(x)
        elif x > up_lim:
            x = up_lim
            outliers.append(x)
        else:
            outliers.append(x)
    return outliers

#removing outliers
df["bmi"] = remove_outliers(df['bmi'])
df["avg_glucose_level"] = remove_outliers(df["avg_glucose_level"])

#get dummies and identify predictor and outcome variables
predictors = df.drop(columns = ["stroke"])
outcome = "stroke"

X = pd.get_dummies(predictors, drop_first=True)
y = df[outcome]

##model building
#split validation
train_X, valid_X, train_y, valid_y= train_test_split(X, y, test_size=0.30, random_state=1)

#oversampling our train and test set
smote = SMOTE()
train_X, train_y = smote.fit_resample(train_X, train_y)

#creating a function to choose best features
import statsmodels.api as sm
def forward_selection(data, target, significance_level=0.05):
    initial_features = data.columns.tolist()
    best_features = []
    while (len(initial_features)>0):
        remaining_features = list(set(initial_features)-set(best_features))
        new_pval = pd.Series(index=remaining_features)
        for new_column in remaining_features:
            model = sm.OLS(target, sm.add_constant(data[best_features+[new_column]])).fit()
            new_pval[new_column] = model.pvalues[new_column]
        min_p_value = new_pval.min()
        if(min_p_value<significance_level):
            best_features.append(new_pval.idxmin())
        else:
            break
    return best_features

##selecting best features
forward_selection(X,y)

X_for_selected=X[['age',
 'work_type_Never_worked',
 'heart_disease_1',
 'avg_glucose_level',
 'ever_married_Yes',
 'hypertension_1',
 'work_type_Private']]

#splitting the new dataset with best selected features
trainx, validx, trainy, validy= train_test_split(X_for_selected, y, test_size=0.30, random_state=1)

#run naive Bayes
nb = GaussianNB()
nb.fit(trainx,trainy)

#predict class membership
prediction_train_nb=nb.predict(validx)

#predict probabilities
pred_train_prob_nb = nb.predict_proba(validx)

##writing our program
#age
print("Please enter your input to test the model")
while True:
    try:
        age = int(input("How old are you?: "))
    except ValueError:
        print("please type a valid age")
        continue
    else:
        if age <= 0:
            print("please type a valid age")
            continue
        break
    
#work type
work_type_Never_worked = input("Have you ever worked? (Y/N): ")
if work_type_Never_worked == "Y" :
    work_type_Never_worked = 0
elif work_type_Never_worked == "N" :
    work_type_Never_worked = 1


#heart disease
heart_disease_1 = input("Do you have any heart disease? (Y/N): ")
if heart_disease_1 == "Y":
    heart_disease_1 = 1
elif heart_disease_1 == "N":
    heart_disease_1 = 0

#avg_glucose_level
avg_glucose_level = float(input("What is your average glucose level (if you don't know, type 100): "))


#ever_married_yes
ever_married_Yes = input("Have you ever been married? (Y/N): ")
if ever_married_Yes == "Y":
    ever_married_Yes = 1
elif ever_married_Yes == "N":
    ever_married_Yes = 0


#hypertension_1
hypertension_1 = input("Do you have hypertension? (Y/N): ")
if hypertension_1 == "Y":
    hypertension_1 = 1
elif hypertension_1 == "N":
    hypertension_1 = 0

#work_type_private
work_type_Private = input("Do you work in private sector? (Y/N) : ")
if work_type_Private == "Y":
    work_type_Private = 1
elif work_type_Private == "N":
    work_type_Private = 0
    
user_input = [[age, work_type_Never_worked, heart_disease_1, avg_glucose_level,
       ever_married_Yes, hypertension_1, work_type_Private]]

pred_user_output = nb.predict(user_input)
pred_prob_user_output = nb.predict_proba(user_input)
result = np.round((100 * pred_prob_user_output), 1)
print(pred_user_output)


print("\n")
print("The results are out:")
print("=====================")
print("There is a", result[0][1], "% chance that the user will get a stroke.")
