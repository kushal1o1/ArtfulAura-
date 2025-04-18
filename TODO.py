# TODO:Create a payment method for the user to pay for the order use esewa ,khalti and stripe
done= True 
#flow - payment  url hit either esewa or khalti,
# for esewa  
    # 1. get the order id and amount from the order summary page and redirect to payment.html page  

    # 2. redirect to esewa payment page with the order id and amount as parameters from payment.html page with required fields
    # 3. after payment is done, esewa will redirect to the verify-esewa url with the order id and amount as parameters
    # 4. verify the payment by checking the order id and amount with the database
    # 5. if payment is successful, update the order status to paid and redirect to the order summary page
    # 6. if payment is not successful, redirect to the order summary page with an error message
# for khalti
    # 1. get the order id and amount from the order summary page
    # 2. redirect to khalti payment page with the order id and amount as parameters
    # 3. after payment is done, khalti will redirect to the verify-khalti url with the order id and amount as parameters
    # 4. verify the payment by checking the order id and amount with the database
    # 5. if payment is successful, update the order status to paid and redirect to the order summary page
    # 6. if payment is not successful, redirect to the order summary page with an error message
    
#for standard and detail flow 
"""
    Step	Action	Purpose & What to Do
1️⃣	User hits payment URL	- Collects payment details (amount, product info, order ID)
- Redirect user to payment gateway's URL (client-side or via backend API).
2️⃣	Payment is done on gateway	- The gateway processes the payment securely.
- User is redirected back to your success_url with pidx or token.
3️⃣	Fetch payment verification	- Backend uses the received pidx to call the payment gateway’s verify endpoint securely.
- Validate transaction status, amount, order ID.
4️⃣	Verify success response	- Check for: status = Completed, amount matched, order ID matched, etc.
- Prevent spoofing or fake redirects (critical security check).
5️⃣	Create Payment object in DB	- Store pidx, payment status, timestamp, amount, etc. in a Payment model.
- Acts as a log + audit trail.
6️⃣	Update Order / OrderItems	- Set ordered = True.
- Add ref_code (tracking/order reference for customer or internal).
- Link to the payment via payment = payment_obj.
7️⃣	Return success or thank you page	- Show confirmation to user.
- Optionally send email/SMS/receipt.
    """

# TODO:Integrate a Machine Learning model to predict  feedback positive or negative
done= False
    # flow - create a model in google collab and export it to a file of pkl and then load the model in the django app and use it to predict the feedback
    # Decision changed :Hosted in hugging face  and used the API to predict the review from there 
    #create signal to predict the review and save it in the database

# TODO:Fix some UI
done= False #still not done of allauth uis

# TODO:Validate user input in the form
done= False 

# TODO: Create a robust error handling mechanism to handle errors and exceptions
done= False

# TODO:Create a standard and follow that  for maintainability
done= True #doing it for the project

# TODO:Update a readme file for the project
done= False

# TODO:Create a service file for the project to handle the business logic
done= False

# TODO:Create a Secure integration with payment gateways like Stripe etc.
done= True


# TODO: Send a email for the order confirmation and payment confirmation 

done= True


# TODO: Add new social login either mail,google or facebook
done= False #added gmail only

#TODO:add stripe for learning other payment integrations
done=True

# TODO:add a currency converter for the payment gateways or somehow handle the inconsistencies

done=False


# TODO: add email sending functionality for order confirmation and payment confirmation
done=True



