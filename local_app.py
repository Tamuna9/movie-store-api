import csv
import requests
#Helper Functions


#This function loads the book from the csv file:
# inpit:none
# output: none

movies = []
cart = []



def load_movie():
    global movies
    with open(r"D:\Desktop\Success college\Python home work\movieStore\movieStore .csv","r") as file:
        reader = csv.DictReader(file)
        movies = [row for row in reader]
 
def search_movie(keyword):
    matches = []
    
    for movie in movies:
        if keyword.lower() in movie["title"].lower() or \
           keyword.lower() in movie["author"].lower() or \
           keyword.lower() in movie["genre"].lower() :
               matches.append(movie)   
        
    return matches
 
def add_to_cart(movie_id, cart):
    for movie in movies:
        if int(movie["id"]) == movie_id:
            cart.append(movie)
            return False

def checkout(cart):
    total = sum(float(movie["price"]) for movie in cart)
    try:
        response = requests.post("https://paymentgateway.com/process",
                                 data={"total": total},
                                 timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.Timeout:
        print("Timeout")
        return False
    
    except requests.exceptions.RequestException:
        print("Request error")
        return False
    
# Menu functions

def menu():
    print("Welcome to the online MovieStore")
    print("=================================")
    while True:
        print("Please choose an option:")
        print()
        print("1. Search for movies")
        print("2. View cart")
        print("3. Checkout")
        print("4. Exit")
        choice = input(">")
        
        if choice == "1":
            search_menu()
        elif choice =="2":
            view_cart_menu()
        elif choice =="3":  
            checkout_menu() 
        elif choice =="4": 
            print("Thank you for shopping with us")
            break
        else:
            print("Invalid choise.Please try again")
    

def search_menu():
    print("Search for Movie")
    print("=================")
    keyword = input("Enter a keyword:")
    results = search_movie(keyword)
    if results:
        print("{:<5} {:<40} {:<20} {:<10}".format("id", "title","author","price"))
        for movie in results:
            print("{:<5} {:<40} {:<20} ${:<9}".format(movie["id"], movie["title"],movie["author"],movie["price"]))
        add_to_cart_menu()
    else:
        print("No result found")
        
        
def add_to_cart_menu():
    print("Enter movie id to add to cart, or press Enter to back")
    choise = input(">")  
    if choise:
        try:
            movie_id = int(choise)  
            if add_to_cart(movie_id, cart):
                print("Movie added to cart")
            else:
                 print("Movie not found")
            
        except ValueError:
             print("Invalid input")
    else:
        pass
    
   
def view_cart_menu():
    print("Shopping cart")
    print("=================")
    if cart:
        print("{:<5} {:<40} {:<20} {:<10}".format("id", "title","author","prise"))
        for movie in cart:
            print("{:<5} {:<40} {:<20} ${:<9}".format(movie["id"], movie["title"],movie["author"],movie["prise"]))    
    else:
        print("Your cart is empty")

def checkout_menu():
    print("Checkout")
    print("=================")
    if cart:
        total = sum(float(movie["price"]) for movie in cart)
        print(f"Total amount: ${total:.2f}")
        
        if checkout(cart):
            print("Payment processed successfuly")
            cart.clear()
        else:
            print("Payment failed, please try again")
       
    else:
        print("Your cart is empty")
 
if __name__== "__main__":
    load_movie()
    menu()




