from fastapi import FastAPI, Request
import payplug
import requests
import json

app = FastAPI()

# ---- Map IBAN value to PayPlug API key ----
PAYPLUG_KEYS = {
    "FR76 1695 8000 0130 5670 5696 366": "sk_live_41JDNiBjQYV5rL3lqXnTKS",
    "FR76 1695 8000 0100 0571 1982 492": "sk_live_3Z0k3650qIaxaIB3V2Qdgd",
    "IBAN 3": "sk_live_xxxxxxxxxxxxxxxxx3",
    # Add more as needed
}

# ---- Map IBAN value to PayPlug API test key ----
PAYPLUG_KEYS_TEST = {
    "FR76 1695 8000 0130 5670 5696 366": "sk_test_6aOfTUHBKVOihUBBv9OvrM",
    "FR76 1695 8000 0100 0571 1982 492": "sk_test_3aV1MigpgyJDhuZ6hFn4yg",
    "IBAN 3": "sk_test_xxxxxxxxxxxxxxxxx3",
    # Add more as needed
}

MONDAY_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ5ODI4NzY2OSwiYWFpIjoxMSwidWlkIjo3NDU5MTU0MSwiaWFkIjoiMjAyNS0wNC0xMFQxMzoxOToyMC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA5Mjc4ODMsInJnbiI6ImV1YzEifQ.Wow6dznT1Q4xDOo0_MgLamoVUVq8YjZDoEKycEb4W24'
MONDAY_BOARD_ID = 2024323737

def get_info_energyz(item_id, column_ids):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }
    query = """
    query ($itemId: [ID!]) {
      items (ids: $itemId) {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
    """
    variables = {"itemId": [int(item_id)]}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    try:
        item_data = response.json()
        print("RAW Monday API response:", json.dumps(item_data, indent=2), flush=True)
        items = item_data.get('data', {}).get('items', [])
        if not items:
            print("No item found for ID:", item_id, flush=True)
            return {}
        result = {}
        for column in items[0]['column_values']:
            if column['id'] in column_ids:
                result[column['id']] = {
                    "text": column.get("text"),
                    "value": column.get("value")
                }
        print("Parsed columns_data:", result, flush=True)
        return result
    except Exception as e:
        print("Error parsing Monday data:", e, flush=True)
        return {}

def get_customer_id(payment_data):
    if 'metadata' in payment_data and 'customer_id' in payment_data['metadata']:
        return payment_data['metadata']['customer_id']
    else:
        return None

def get_formula_column_value(item_id, formula_column_id):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": MONDAY_API_KEY,
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
        "itemId": [int(item_id)],
        "columnId": [formula_column_id]
    }
    data = {
        "query": query,
        "variables": variables
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        try:
            display_value = result["data"]["items"][0]["column_values"][0]["display_value"]
            return display_value
        except (KeyError, IndexError):
            return "Formula value not found"
    else:
        return f"Request failed with status code {response.status_code}"

# ------------------------- ACCOMPTE 1 (Original) -------------------------
def send_url_energyz1(url, id_, id_insta):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        'mutation {change_multiple_column_values('
        f'item_id:{id_}, board_id:{id_insta}, '
        'column_values: "{\\\"link_mkt6xsyq\\\" : {\\\"url\\\" : \\\"' + url + '\\\", \\\"text\\\":\\\"Payer\\\"}}") {id}}'
    )
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Monday link response:", r.text, flush=True)

def create_payment_ENERGYZ1(api_key, installateur, id_, Email, Adresse, Prix):
    payplug.set_secret_key(api_key)
    payment_data = {
        'amount': int(float(Prix)) * 100,
        'currency': 'EUR',
        'save_card': False,
        'customer': {
            'email': Email,
            'address1': Adresse,
            'first_name': installateur,
            'last_name': installateur
        },
        'hosted_payment': {
            'sent_by': 'OTHER',
            'return_url': 'https://energyz-company.monday.com/',
            'cancel_url': 'https://energyz-company.monday.com/',
        },
        'notification_url': 'https://energyz-prestation.onrender.com/energyz_prest_notif_1',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    print("PayPlug payment data:", payment_data, flush=True)
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}", flush=True)
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print("PayPlug error:", e, flush=True)
        return None
    
def set_payer_energyz1(IDM):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        "mutation {change_multiple_column_values(item_id:" + str(IDM) +
        ",board_id:" + str(MONDAY_BOARD_ID) +
        ', column_values: "{\\\"status\\\" : {\\\"label\\\" : \\\"Payé acompte 1\\\"}}") {id}}'
    )
    data = {'query': query}
    print("Setting payment status to 'Payé acompte 1'", flush=True)
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Status column update response:", r.text, flush=True)
   
@app.post("/to_pay_energyz_prest_1")
async def to_pay_energyz_prest_1(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6rkzt',     # Montant Acompte 1 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6rkzt", {}).get("numeric", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ1(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz1(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)
    return {"status": "processed"}

@app.post("/energyz_prest_notif_1")
async def energyz_prest_notif_1(request: Request):
    body = await request.json()
    print("Received notification from PayPlug:", body, flush=True)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            if idm:
                set_payer_energyz1(idm)
        except Exception as e:
            print("Error in notif:", e, flush=True)
    return {"status": "processed"}

# --------------------- ACCOMPTE 2 ---------------------
def send_url_energyz2(url, id_, id_insta):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        'mutation {change_multiple_column_values('
        f'item_id:{id_}, board_id:{id_insta}, '
        'column_values: "{\\\"link_mkt6bs9p\\\" : {\\\"url\\\" : \\\"' + url + '\\\", \\\"text\\\":\\\"Payer\\\"}}") {id}}'
    )
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Monday link response:", r.text, flush=True)

def create_payment_ENERGYZ2(api_key, installateur, id_, Email, Adresse, Prix):
    payplug.set_secret_key(api_key)
    payment_data = {
        'amount': int(float(Prix)) * 100,
        'currency': 'EUR',
        'save_card': False,
        'customer': {
            'email': Email,
            'address1': Adresse,
            'first_name': installateur,
            'last_name': installateur
        },
        'hosted_payment': {
            'sent_by': 'OTHER',
            'return_url': 'https://energyz-company.monday.com/',
            'cancel_url': 'https://energyz-company.monday.com/',
        },
        'notification_url': 'https://energyz-prestation.onrender.com/energyz_prest_notif_2',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    print("PayPlug payment data:", payment_data, flush=True)
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}", flush=True)
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print("PayPlug error:", e, flush=True)
        return None
    
def set_payer_energyz2(IDM):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        "mutation {change_multiple_column_values(item_id:" + str(IDM) +
        ",board_id:" + str(MONDAY_BOARD_ID) +
        ', column_values: "{\\\"status\\\" : {\\\"label\\\" : \\\"Payé acompte 2\\\"}}") {id}}'
    )
    data = {'query': query}
    print("Setting payment status to 'Payé acompte 2'", flush=True)
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Status column update response:", r.text, flush=True)
   
@app.post("/to_pay_energyz_prest_2")
async def to_pay_energyz_prest_2(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6bjsz',     # Montant Acompte 2 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6bjsz", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ2(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz2(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)
    return {"status": "processed"}

@app.post("/energyz_prest_notif_2")
async def energyz_prest_notif_2(request: Request):
    body = await request.json()
    print("Received notification from PayPlug:", body, flush=True)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            if idm:
                set_payer_energyz2(idm)
        except Exception as e:
            print("Error in notif:", e, flush=True)
    return {"status": "processed"}

# --------------------- ACCOMPTE 3 ---------------------
def send_url_energyz3(url, id_, id_insta):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        'mutation {change_multiple_column_values('
        f'item_id:{id_}, board_id:{id_insta}, '
        'column_values: "{\\\"link_mkt62ky4\\\" : {\\\"url\\\" : \\\"' + url + '\\\", \\\"text\\\":\\\"Payer\\\"}}") {id}}'
    )
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Monday link response:", r.text, flush=True)

def create_payment_ENERGYZ3(api_key, installateur, id_, Email, Adresse, Prix):
    payplug.set_secret_key(api_key)
    payment_data = {
        'amount': int(float(Prix)) * 100,
        'currency': 'EUR',
        'save_card': False,
        'customer': {
            'email': Email,
            'address1': Adresse,
            'first_name': installateur,
            'last_name': installateur
        },
        'hosted_payment': {
            'sent_by': 'OTHER',
            'return_url': 'https://energyz-company.monday.com/',
            'cancel_url': 'https://energyz-company.monday.com/',
        },
        'notification_url': 'https://energyz-prestation.onrender.com/energyz_prest_notif_3',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    print("PayPlug payment data:", payment_data, flush=True)
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}", flush=True)
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print("PayPlug error:", e, flush=True)
        return None
    
def set_payer_energyz3(IDM):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        "mutation {change_multiple_column_values(item_id:" + str(IDM) +
        ",board_id:" + str(MONDAY_BOARD_ID) +
        ', column_values: "{\\\"status\\\" : {\\\"label\\\" : \\\"Payé acompte 3\\\"}}") {id}}'
    )
    data = {'query': query}
    print("Setting payment status to 'Payé acompte 3'", flush=True)
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Status column update response:", r.text, flush=True)
   
@app.post("/to_pay_energyz_prest_3")
async def to_pay_energyz_prest_3(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6z42w',     # Montant Acompte 3 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6z42w", {}).get("numeric", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ3(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz3(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)
    return {"status": "processed"}

@app.post("/energyz_prest_notif_3")
async def energyz_prest_notif_3(request: Request):
    body = await request.json()
    print("Received notification from PayPlug:", body, flush=True)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            if idm:
                set_payer_energyz3(idm)
        except Exception as e:
            print("Error in notif:", e, flush=True)
    return {"status": "processed"}

# --------------------- ACCOMPTE 4 ---------------------
def send_url_energyz4(url, id_, id_insta):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        'mutation {change_multiple_column_values('
        f'item_id:{id_}, board_id:{id_insta}, '
        'column_values: "{\\\"link_mkt65km6\\\" : {\\\"url\\\" : \\\"' + url + '\\\", \\\"text\\\":\\\"Payer\\\"}}") {id}}'
    )
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Monday link response:", r.text, flush=True)

def create_payment_ENERGYZ4(api_key, installateur, id_, Email, Adresse, Prix):
    payplug.set_secret_key(api_key)
    payment_data = {
        'amount': int(float(Prix)) * 100,
        'currency': 'EUR',
        'save_card': False,
        'customer': {
            'email': Email,
            'address1': Adresse,
            'first_name': installateur,
            'last_name': installateur
        },
        'hosted_payment': {
            'sent_by': 'OTHER',
            'return_url': 'https://energyz-company.monday.com/',
            'cancel_url': 'https://energyz-company.monday.com/',
        },
        'notification_url': 'https://energyz-prestation.onrender.com/energyz_prest_notif_4',
        'metadata': {
            'customer_id': id_,
            'customer_insta': installateur
        },
    }
    print("PayPlug payment data:", payment_data, flush=True)
    try:
        payment = payplug.Payment.create(**payment_data)
        print(f"Payment URL: {payment.hosted_payment.payment_url}", flush=True)
        return payment.hosted_payment.payment_url
    except payplug.exceptions.PayplugError as e:
        print("PayPlug error:", e, flush=True)
        return None

def set_payer_energyz4(IDM):
    apiKey = MONDAY_API_KEY
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey}
    query = (
        "mutation {change_multiple_column_values(item_id:" + str(IDM) +
        ",board_id:" + str(MONDAY_BOARD_ID) +
        ', column_values: "{\\\"status\\\" : {\\\"label\\\" : \\\"Payé acompte 4\\\"}}") {id}}'
    )
    data = {'query': query}
    print("Setting payment status to 'Payé acompte 3'", flush=True)
    r = requests.post(url=apiUrl, json=data, headers=headers)
    print("Status column update response:", r.text, flush=True)
   
@app.post("/to_pay_energyz_prest_4")
async def to_pay_energyz_prest_4(request: Request):
    body = await request.json()
    if "challenge" in body:
        return {"challenge": body["challenge"]}
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt63d7r',     # Montant Acompte 4 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt63d7r", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ4(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz4(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)
    return {"status": "processed"}

@app.post("/energyz_prest_notif_4")
async def energyz_prest_notif_4(request: Request):
    body = await request.json()
    print("Received notification from PayPlug:", body, flush=True)
    if body.get('is_paid') and body.get('is_live'):
        try:
            idm = get_customer_id(body)
            if idm:
                set_payer_energyz4(idm)
        except Exception as e:
            print("Error in notif:", e, flush=True)
    return {"status": "processed"}

#-------------------- Multi-acompte Paiment energyz ----------------------------
# Helper functions to generate each accompte link
def generate_acompte_1_link(body):
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6rkzt',     # Montant Acompte 1 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6rkzt", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ1(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz1(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)

def generate_acompte_2_link(body):
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6bjsz',     # Montant Acompte 2 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6bjsz", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ2(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz2(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)

def generate_acompte_3_link(body):
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt6z42w',     # Montant Acompte 3 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt6z42w", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ3(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz3(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)

def generate_acompte_4_link(body):
    try:
        id_ = body['event']['pulseId']
        _insta = body['event']['pulseName']
        column_ids = [
            'location_mksap4tf',    # Adresse
            'email_mksa3z84',       # E-mail
            'formula_mksadzsw',     # Compte PPG associé (IBAN)
            'numeric_mkt63d7r',     # Montant Acompte 4 (TTC)
        ]
        columns_data = get_info_energyz(id_, column_ids)
        print("API response columns_data:", columns_data, flush=True)

        address = columns_data.get("location_mksap4tf", {}).get("text", "")
        email = columns_data.get("email_mksa3z84", {}).get("text", "")
        prix = columns_data.get("numeric_mkt63d7r", {}).get("value", "")
        print("Extracted address:", address, flush=True)
        print("Extracted email:", email, flush=True)
        print("Extracted prix:", prix, flush=True)

        iban_key = get_formula_column_value(id_, 'formula_mksadzsw')
        print("IBAN Key (from formula):", iban_key, flush=True)  
        api_key = PAYPLUG_KEYS.get(iban_key)
        if not api_key:
            print(f"Unknown IBAN key: {iban_key}", flush=True)
            return {"status": "error", "reason": "Unknown IBAN key"}

        url = create_payment_ENERGYZ4(api_key, _insta, id_, email, address, prix)
        print('Generated payment url:', url, flush=True)
        if url:
            send_url_energyz4(url, id_, MONDAY_BOARD_ID)
        else:
            print("Failed to generate payment link.", flush=True)
            return {"status": "error", "reason": "Payment link generation failed"}
    except Exception as e:
        print("Error in /to_pay_energyz_prest:", e, flush=True)

# New endpoint for generating ALL links at once
@app.post("/to_pay_energyz_all")
async def to_pay_energyz_all(request: Request):
    body = await request.json()
    # (Optional: handle webhook verification for Monday)
    if "challenge" in body:
        return {"challenge": body["challenge"]}

    generate_acompte_1_link(body)
    generate_acompte_2_link(body)
    generate_acompte_3_link(body)
    generate_acompte_4_link(body)

    return {"status": "all links generated"}