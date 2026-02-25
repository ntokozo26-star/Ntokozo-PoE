#Define the error handling for invalid user input 
#Promt user to enter what they would like to calculate: Investement of Bond
#if user inputs Investment
    #Request for the investment amount, interest rate, years of investment and calculation type 
    #Calculate the investment value based on the calculation type\
    #print the results
#if user inputs Bond 
    #Request the user to enter the value of the house
    #Request the user to enter the interest %
    #Request the user to enter the repayment months
    #calculate the repayment amount 
    #Print the results
   
import math

#Function to safely get a valid float input
def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))  
        except ValueError:
            print("Invalid input! Please enter a valid number.")  

#Function to safely get a valid integer input
def get_valid_int(prompt):
    while True:
        try:
            return int(input(prompt))  
        except ValueError:
            print("Invalid input! Please enter a valid integer.")  

# Function to safely get a valid interest type input
def get_valid_interest_type():
    while True:
        interest_type = input("Enter the interest type, simple or compound: ").strip().lower()
        if interest_type == "simple" or interest_type == "compound":
            return interest_type 
        else:
            print("Invalid interest type input! Please enter either 'simple' or 'compound'.")

# Loop until the user provides a valid calc_choice
while True:
    print("Investment - to calculate the amount of interest you'll earn on your investment.")
    print("Bond       - to calculate the amount you'll have to pay on a home loan.")
    
    calc_choice = input("Enter either 'investment' or 'bond' from the menu above to proceed: ").strip().lower()

    if calc_choice == "investment":
        # Get the necessary inputs with error handling
        rand_amount = get_valid_float("Enter the rand amount you want to deposit: ")
        interest_rate = get_valid_float("Enter the interest rate as a percentage: ")
        invest_years = get_valid_int("Enter the number of years you want to invest: ")
        
        # Get a valid interest type
        interest_type = get_valid_interest_type()

        converted_rate = interest_rate / 100

        if interest_type == "simple":
            total_rand_amount = rand_amount * (1 + converted_rate * invest_years)
            print(f"Your total investment rand value after {invest_years} years with simple interest will be: {total_rand_amount:.2f}")
        elif interest_type == "compound":
            total_rand_amount = rand_amount * math.pow((1 + converted_rate), invest_years)
            print(f"Your total investment rand value after {invest_years} years with compound interest will be: {total_rand_amount:.2f}")
        break 

    elif calc_choice == "bond":
        # Get the necessary inputs with error handling
        current_value = get_valid_float("Enter the current value of the house: ")
        interest_rate = get_valid_float("Enter the interest rate as percentage: ")
        months = get_valid_int("Enter the number of months you plan to pay for the bond: ")

        monthly_rate = interest_rate / 100 / 12

        repayment = (monthly_rate * current_value) / (1 - math.pow(1 + monthly_rate, -months)) 
        print(f"Your monthly bond repayment is: {repayment:,.2f}")
        break  

    else:
        print("Invalid Calculator type, please enter either 'investment' or 'bond'.")
