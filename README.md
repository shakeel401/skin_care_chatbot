# PureGlow Skin Specialist Assistant

PureGlow is an AI-powered **Skincare Specialist Assistant** that helps users analyze their skin, recommend suitable skincare products, and manage skincare-related queries. The assistant integrates **LangChain, Qdrant, OpenAI GPT, HuggingFace Embeddings, and Twilio WhatsApp API** to provide personalized skincare recommendations and order management features.

---

## 🚀 Features

### 🧑‍⚕️ **Skin Analysis & Consultation**

- Analyzes skin type, concerns, and preferences using AI.
- Provides customized skincare advice.

### 🛍️ **Product Recommendations**

- Suggests skincare products based on user concerns.
- Retrieves top-rated skincare products from **Qdrant Vector Store**.

### 📦 **Order Placement & Tracking**

- Places orders for recommended skincare products.
- Sends order confirmation via **WhatsApp using Twilio**.
- Allows users to check order status using an **Order ID**.

### 🏬 **Store Information**

- Provides details about the skincare store and available products.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **AI Models:** OpenAI GPT-4o-mini, HuggingFace Embeddings
- **Vector Database:** Qdrant
- **LLM Framework:** LangChain
- **Messaging API:** Twilio WhatsApp
- **Database:** SQLite

---

## 📌 Installation & Setup

### 1️⃣ **Clone the Repository**

```bash
 git clone https://github.com/your-repo/pureglow-assistant.git
 cd pureglow-assistant
```

### 2️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3️⃣ **Set Environment Variables**

Create a `.env` file in the root directory and add your credentials:

```env
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NO=your_twilio_whatsapp_number
```

### 4️⃣ **Run the Application**

```bash
uvicorn app.main:app --reload
```

---

## 🔧 API Endpoints

### **1️⃣ Analyze Skin & Get Recommendations**

**POST** `/analyze-skin`

#### Request Body:

```json
{
  "user_input": "I have oily skin with acne. What should I use?"
}
```

#### Response:

```json
{
  "advice": "You have oily skin with acne. Use oil-free products with salicylic acid."
}
```

### **2️⃣ Get Product Recommendations**

**POST** `/recommend-products`

#### Request Body:

```json
{
  "user_query": "Best moisturizer for dry skin"
}
```

### **3️⃣ Place an Order**

**POST** `/place-order`

#### Request Body:

```json
{
  "user_name": "Ali",
  "phone_number": "+923001234567",
  "address": "Lahore, Pakistan",
  "product_name": "Hydrating Face Cream",
  "price": 1500
}
```

### **4️⃣ Check Order Status**

**POST** `/check-order-status`

#### Request Body:

```json
{
  "order_id": 123456
}
```

---
