import time #used to pause execution (simulate network slowness/lag)
from flask import Flask, jsonify, request #flask framework tools for APIs

#initialize the flask web application
app = Flask(__name__)

# memory chaos state (for demo and testing purposes , judging)
chaos_state = {
    "is healthy": True,
    "delay_seconds": 0.0
}

#(inventory data) mock database
INVENTORY_DATA = {
    1: {"stock": 14, "status": "In stock", "warehouse": "West-1"},
    2: {"stock": 3, "status": "Low stock", "warehouse": "Central-2"},
    3: {"stock": 8, "status": "In stock", "warehouse": "East-1"},
    4: {"stock": 25, "status": "In stock", "warehouse": "West-2"},
}

# core bussiness api - get product stock
#URL - http://127.0.0.1:5001/api/stock
#shopshield will call this api to get product stock information when user views product page
@app.route('/api/stock/<int:product_id>', methods=['GET'])
def get_stock(product_id):
    '''Returns real-time warehouse stock count for given id'''
    # chaos check 1 : Problem 2 (temporary slowness / timeout)
    # if chaos delay is active , will freze the threead for x sec
    if chaos_state["delay_seconds"] > 0:
        time.sleep(chaos_state["delay_seconds"])
     # chaos check 2 : problem 3 (service outage / 500 error)
     # if the service is unhealthy , return 500 error
    if not chaos_state["is healthy"]:
        return jsonify({
            "error": "Product Service Internal Failure",
            "service": "product_service"
        }), 500  
    # Normal healthy flow
    #look up product in our dictionary ; if not found, provide a default fallback
    stock_info = INVENTORY_DATA.get(
        product_id,
        {"stock": 10, "status": "In stock", "warehouse": "Unknown"}
        )

    #return stock detail as a json response with HTTP 200 OK 
    return jsonify({
        "product_id": product_id,
        "stock": stock_info["stock"],
        "status": stock_info["status"],
        "warehouse": stock_info["warehouse"],
    }), 200

# step 5 Health Check API (called by healops monitor)
#Healops pings this endpoint to check if the product service is healthy/alive

@app.route('/health')
def health():
    '''Health probe called by HealOps watchdog/montior.'''

    #if delay is active , the health check also slows down(detect degradation)
    if chaos_state["delay_seconds"] > 0:
        time.sleep(chaos_state["delay_seconds"])
    #if service is broken, return 500 error so healops sees a RED status badge
    if not chaos_state["is healthy"]:
        return jsonify({
            "service": "product_service",
            "status": "unhealthy",
            "chaos_active": True
        }), 500

    #if all is well , return 200  so healops sees a GREEN status badge
    return jsonify({
        "service": "product_service",
        "status": "healthy",
        "delay_seconds": chaos_state["delay_seconds"]
    }), 200

#step 6 Chaos lab trigers (called by healops dashboard buttons)


#trigger for problem 3 :complete service outage 
@app.route('/chaos/toggle-fail', methods=['POST','GET'])
def toggle_fail():
    '''flips is_healthy betweeen True and False to simulate an outage.'''
    chaos_state["is healthy"] = not chaos_state["is healthy"]
    curremt_status = "healthy" if chaos_state["is healthy"] else "FAILING (HTTP 500)"

    return jsonify({
        "message": f"Product Service is now {curremt_status}",
        "is healthy": chaos_state["is healthy"]
    })

#trigger for problem 2 : temporary slowness / latecy
@app.route('/chaos/set-delay', methods=['POST','GET'])
def set_delay():
    '''Adds a delay (eg 2.5 seconds) to simulate network lag or overload.'''
    #Read the ? sec=query parameter (default to 2.0 sec)
    seconds = float(request.args.get('seconds', 2.0))

    #if delay is already on , turn it off . If it is off , turn it on!
    if chaos_state["delay_seconds"] > 0:
        chaos_state["delay_seconds"] = 0.0
    else:
        chaos_state["delay_seconds"] = seconds

    return jsonify({"delay_seconds": chaos_state["delay_seconds"]})

#step 7 Entry point (run server on port 5001)

if __name__ == '__main__':
    #we choose port 5001 to avoid conflict with the shopshield app (which runs on 5000)
    print(" Product service is running on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001)