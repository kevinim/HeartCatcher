from firebase import firebase


# Initialize Firebase
firebase = firebase.FirebaseApplication('https://cis9590-355fe-default-rtdb.firebaseio.com/', None)


# # # Importing Data
# data = {
#     'ID': 'USER_00001',
#     'Age': '50',
#     'Hypertension': 'Y',
#     'HeartDisease': 'N',
#     'Married': 'Y',
#     'Employment': 'N',
#     'AvgGlucoseLvl': '100',
#     'Smoking': 'Y'
# }
# # Post Data
# # Database Name/Table Name
# firebase.post('cis9590-355fe-default-rtdb/Biometrics', data)

# # Importing Data
data = {
    'ID': 'USER_00001',
    'Email': 'hwangbinim@gmail.com',
    'Password': 'trial@123'
}
# Post Data
# Database Name/Table Name
firebase.post('cis9590-355fe-default-rtdb/Users', data)

# # Get Data
# result = firebase.get('cis9590-355fe-default-rtdb/Users', '')
# #print(result)

# # Get Specific column like email or password

# for i in result.keys():
# #    print(result[i]['Email'])
#     print(result[i]['Password'])