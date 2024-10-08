import paho.mqtt.client as mqtt
import requests
from bs4 import BeautifulSoup

# MQTT server details
MQTT_SERVER = "192.168.1.1"
MQTT_PORT = 1883
MQTT_TOPIC = "homeassistant/sensor/electricity_price"
MQTT_USERNAME = "user"  # Replace with your username
MQTT_PASSWORD = "password"  # Replace with your password

# URL of the webpage you want to scrape
URL = "https://www.e-steiermark.com/privat/produkte/strom"  # Replace with the actual URL

# Function to extract the price from the webpage
def extract_price():
    try:
        # Make a request to fetch the webpage content
        response = requests.get(URL)

        # If request is successful
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the element with the ID and class
            price_element = soup.select_one("#product-details1 .price2 .priceEUR")

            if price_element:
                price_text = price_element.get_text().strip()

                # Check if the price contains the string "Cent"
                if "Cent" in price_text:
                    # Extract the numeric part of the string and convert to float
                    price_value = float(price_text.replace("Cent", "").replace(",", ".").strip())
                    # Convert Cent to Euro
                    euro_price = price_value / 100
                    return f"{euro_price:.4f}"  # Return the value in Euro with 3 decimal places
                else:
                    price_value = float(price_text.replace("Euro", "").replace(",", ".").strip())
                    return f"{price_value:.2f}" # Return the value in Euro with 2 decimal places
        else:
            print(f"Failed to fetch webpage. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to publish the price to the MQTT server
def publish_price(price):
    try:
        # Initialize the MQTT client with version 2 for avoiding deprecation warnings
        client = mqtt.Client(client_id="", protocol=mqtt.MQTTv311)  # Update the protocol

        # Set the username and password for the MQTT server
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Connect to the MQTT server
        client.connect(MQTT_SERVER, MQTT_PORT, 60)

        # Start the client loop to handle reconnects and callbacks
        client.loop_start()

        # Publish the price under the specified topic
        result = client.publish(MQTT_TOPIC, price)

        # Wait for the message to be sent (optional, can be removed if not needed)
        result.wait_for_publish()

        # Stop the loop and disconnect
        client.loop_stop()
        client.disconnect()

        print(f"Published price: {price} to topic {MQTT_TOPIC}")
    except Exception as e:
        print(f"An error occurred while publishing to MQTT: {e}")

# Main function
if __name__ == "__main__":
    # Extract the price from the webpage
    price = extract_price()

    # If price is successfully extracted, publish it to MQTT
    if price:
        publish_price(price)
    else:
        print("No price to publish.")
