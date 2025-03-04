from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import sqlite3
import random
import datetime
from langchain_core.tools import tool
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_no = os.getenv("TWILIO_PHONE_NO")

# Load Embedding Model
embed_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Connect to Qdrant
knowledge_base3 = QdrantVectorStore.from_existing_collection(
    embedding=embed_model,
    url=qdrant_url,  # Your Qdrant URL
    api_key= qdrant_api_key,
    collection_name="skincare_products"
)
knowledge_base = QdrantVectorStore.from_existing_collection(
    embedding=embed_model,
    url=qdrant_url,  # Your Qdrant URL
    api_key= qdrant_api_key,
    collection_name="skincare_store"
)

# Database Setup for Orders
conn = sqlite3.connect("skincare.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    phone_number TEXT,
    address TEXT,
    product_name TEXT,
    price REAL,
    order_time TEXT
)
""")

conn.commit()

# 1️⃣ **Tool: Get Recommended Products Based on Query**
@tool
def recommend_products(user_query: str, top_k: int = 5) -> list:
    """Returns a list of recommended skincare products from Qdrant based on user query."""
    results = knowledge_base3.similarity_search(user_query, k=top_k)
    
    if not results:
        return []
    
    return [
        {
            "product_name": doc.metadata["product_name"],
            "brand": doc.metadata["brand"],
            "notable_effects": doc.metadata.get("notable_effects", "N/A"),
            "price": f"Rs: {doc.metadata['price']}",
            "product_type": doc.metadata["product_type"],
            "skintype": doc.metadata["skintype"],
            "description": doc.metadata["description"],
            "picture_src": doc.metadata["picture_src"]
        }
        for doc in results
    ]

# Tool: Place Order & Send Confirmation Message
# Tool: Send Order Confirmation via WhatsApp
def send_order_confirmation(phone_number: str, message: str) -> str:
    """Sends an order confirmation message to the user via WhatsApp using Twilio."""
    client = Client(account_sid, auth_token)
    
    try:
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to=f"whatsapp:{phone_number}"
        )
        return "✅ Order confirmation sent successfully."
    except Exception as e:
        return f"❌ Failed to send message: {str(e)}"

@tool
def place_order(user_name: str, phone_number: str, address: str, product_name: str, price: float) -> str:
    """Places an order for a selected skincare product and sends a confirmation message with an Order ID."""
    order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_id = random.randint(100000, 999999)  # Generate Order ID

    # Store order in database
    cursor.execute(
        "INSERT INTO orders (id, user_name, phone_number, address, product_name, price, order_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_id, user_name, phone_number, address, product_name, price, order_time)
    )
    conn.commit()

    # Generate order details message
    order_message = (f"✅ Your order has been placed successfully!\n"
                     f"📦 Order ID: {order_id}\n"
                     f"👤 Name: {user_name}\n"
                     f"📞 Phone: {phone_number}\n"
                     f"🏠 Address: {address}\n"
                     f"🛍️ Product: {product_name}\n"
                     f"💰 Price: Rs: {price}\n"
                     f"🕒 Order Time: {order_time}\n"
                     f"🚚 Track your order using Order ID: {order_id}")

    # Attempt to send WhatsApp confirmation
    try:
        send_status = send_order_confirmation(phone_number, order_message)
        if "❌" in send_status:  # If sending failed, log but don't stop order booking
            print("⚠️ Notification failed:", send_status)
    except Exception as e:
        print("⚠️ Error in sending WhatsApp confirmation:", str(e))

    return order_message  # Order is still booked even if notification fails
    
    # Tool: Check Order Status by Order ID
@tool
def check_order_status(order_id: int) -> str:
    """Checks the order status using the given Order ID."""
    cursor.execute("SELECT user_name, product_name, price, order_time FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    if order:
        user_name, product_name, price, order_time = order
        return (f"📦 Order Status:\n"
                f"👤 Name: {user_name}\n"
                f"🛍️ Product: {product_name}\n"
                f"💰 Price: ${price}\n"
                f"🕒 Order Time: {order_time}\n"
                f"🚚 Status: Your order is being processed.")
    else:
        return "❌ No order found for this Order ID."
    
@tool
def analyze_skin_before_recommed(user_input: str) -> str:
    """Analyzes the user's skin type and concerns, then provides personalized skincare advice."""
    prompt = ChatPromptTemplate.from_messages([
         ("system",
         "You are a professional skincare specialist AI. Your role is to help users understand their skin type, "
         "identify skin concerns, and provide skincare recommendations. "
         "Start by asking the user about their skin type (e.g., oily, dry, combination, sensitive), their main skin concerns "
         "(e.g., acne, wrinkles, pigmentation), and any allergies or preferences. "
         "Based on their responses, provide relevant skincare tips, suggest product types, and highlight key ingredients to look for."),
        ("human", "{input}"),
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        max_tokens=200,
        temperature=0.2
    )
    
    chain = prompt | llm
    response = chain.invoke({"input": user_input})

    return response.content

@tool
def get_store_info(user_query: str, top_k: int = 5) -> list:
    """Retrieve information about the PureGlow product store using Qdrant similarity search."""
    results = knowledge_base.similarity_search(user_query, k=top_k)
    return results