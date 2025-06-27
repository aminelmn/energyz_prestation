#---------------------------------- Paiment energyz -----------------------------
from fastapi import FastAPI
from fastapi import Request
import payplug
import requests 
import json
from fastapi.responses import JSONResponse  
app = FastAPI()


# ---- Map IBAN value to PayPlug API key ----
PAYPLUG_KEYS = {
    "IBAN 1": "sk_live_41JDNiBjQYV5rL3lqXnTKS",  
    "IBAN 2": "sk_live_xxxxxxxxxxxxxxxxx2",
    "IBAN 3": "sk_live_xxxxxxxxxxxxxxxxx3",
    # Add more as needed
}

# ---- Map IBAN value to PayPlug API test key ----
PAYPLUG_KEYS_TEST = {
    "IBAN 1": "sk_test_6aOfTUHBKVOihUBBv9OvrM",
    "IBAN 2": "sk_test_xxxxxxxxxxxxxxxxx2",
    "IBAN 3": "sk_test_xxxxxxxxxxxxxxxxx3",
    # Add more as needed
}

# ---- Functions to send URL to Monday.com ----
def send_url_energyz(url,id_,id_insta):
    apiKey = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ'
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : apiKey}

    query5 = "mutation {change_multiple_column_values(item_id:"+str(id_)+", board_id:"+str(id_insta)+", column_values: \"{\\\"link_mksaj8k7\\\" : {\\\"url\\\" : \\\""+url+"\\\", \\\"text\\\":\\\"Payer\\\"}}\") {id}}"
    #print(query5)
    data = {'query' : query5}
    r = requests.post(url=apiUrl,json=data, headers=headers) # make request
    results=json.loads(r.text)
    print(results)

def create_payment_ENERGYZ(api_key, Nom_client, id_, Email, Prix):
    payplug.set_secret_key(api_key)

    payment_data = {
    'amount': int(float(Prix))*100,
    'currency': 'EUR',
    'save_card': False,
    'customer': {
    'email': Email,

    'first_name': Nom_client,
    'last_name': Nom_client


    },
    'hosted_payment': {
    'sent_by':'OTHER',
    'return_url': 'https://energyz-company.monday.com/',
    'cancel_url': 'https://energyz-company.monday.com/',
    },
    'notification_url': 'https://energyz-prestation.onrender.com/energyz_prest_notif',  
    'metadata': {

    'customer_id': id_,
    'customer_insta': Nom_client
    },
    }
    print(payment_data)
    try:
        payment = payplug.Payment.create(**payment_data)
        print (f"Payment URL: {payment.hosted_payment.payment_url}")
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print(e)
        return (f"An error occurred: {e}")



def get_info_energyz(item_id, column_ids=1676598283):
    # API endpoint
    url = "https://api.monday.com/v2"

    # Headers
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ",
        "Content-Type": "application/json"
    }

    # GraphQL query to get item data
    query = """
    query ($itemId: [ID!]) {
      items (ids: $itemId) {
        id
        name
        column_values {
          id
          value
        }
      }
    }
    """

    # Variables for the query
    variables = {
        "itemId": [item_id]
    }

    # Make the request
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        item_data = response.json()
        result = {}
        items = item_data.get('data', {}).get('items', [])
        for item in items:
            for column in item['column_values']:
                if column['id'] in column_ids:
                    column_value = column['value']
                    if column_value:
                        try:
                            decoded_value = json.loads(column_value)
                            result[column['id']] = decoded_value
                        except json.JSONDecodeError:
                            result[column['id']] = column_value
                    else:
                        result[column['id']] = None
        return result
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None
def get_customer_id(payment_data):
    # Check if 'metadata' key exists and contains 'customer_id'
    if 'metadata' in payment_data and 'customer_id' in payment_data['metadata']:
        return payment_data['metadata']['customer_id']
    else:
        return None
    
def set_payer_energyz(IDM) :
    apiKey = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ'
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : apiKey}
    query2 = "mutation {change_multiple_column_values(item_id:"+str(IDM)+",board_id :2024323737, column_values: \"{\\\"status\\\" : {\\\"label\\\" : \\\"Paiement reçu\\\"}}\") {id}}" 
    data = {'query' : query2}
    print("audit_payé")
    
    r = requests.post(url=apiUrl, json=data, headers=headers)
import requests
import json
from typing import Dict, Any

def get_formula_column_value(item_id, formula_column_id):
    """
    Get the display value of a specific formula column for an item in monday.com
    
    Parameters:
    api_key (str): Your monday.com API key
    item_id (int): The ID of the item containing the formula column
    formula_column_id (str): The ID of the formula column
    
    Returns:
    str: The display value of the formula column
    """
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMjA4NzMzOCwiYWFpIjoxMSwidWlkIjo1NzE5ODc4MCwiaWFkIjoiMjAyNC0xMS0wNFQxNzoxMTozNi4xNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.b4fJKryT0-eAY4B0KwApnFqguyIN_RCBu0IJck2_MwQ",
        "Content-Type": "application/json"
    }
    
    query = """
    query ($itemId: [ID!], $columnId: [String!]) {
      items (ids: $itemId) {
        column_values(ids: $columnId) {
          ... on FormulaValue {
            id
            display_value
          }
        }
      }
    }
    """
    
    variables = {
        "itemId": [item_id],
        "columnId": [formula_column_id]
    }
    
    data = {
        "query": query,
        "variables": variables
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        # Extract the display_value from the response
        try:
            display_value = result["data"]["items"][0]["column_values"][0]["display_value"]
            return display_value
        except (KeyError, IndexError):
            return "Formula value not found"
    else:
        return f"Request failed with status code {response.status_code}"

# Example usage
# api_key = "your_api_key_here"
# item_id = 1234567890
# formula_column_id = "formula_column"
# formula_value = get_formula_column_value(api_key, item_id, formula_column_id)
# print(formula_value)

@app.post("/to_pay_energyz_prest")
async def to_pay_energyz_prest(request: Request):
    body = await request.json()

    # Step 1: Handle Monday.com webhook verification
    if "challenge" in body:
        return {"challenge": body["challenge"]}

    # Step 2: Normal webhook handling
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = ['email_mksa3z84', 'formula_mksadzsw', 'text_mksa2v7e']
        columns_data = get_info_energyz(id_, column_ids)
        data = [columns_data["email_mksa3z84"]["email"]]
        prix = columns_data["text_mksa2v7e"]['text']
        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        api_key = PAYPLUG_KEYS_TEST.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}")
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ(api_key, _insta, id_, data[1], int(float(prix)))
        print('url______________', url)
        send_url_energyz(url, id_, '2024323737')

    except Exception as e:
        print("Error:", e)

    return {"status": "processed"}


@app.post("/energyz_prest_notif")
async def energyz_prest_notif(request: Request):
    body = await request.json()
    print(body)

    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            set_payer_energyz(idm)
        except Exception as e:
            print("Error in notif:", e)

    return {"status": "processed"}