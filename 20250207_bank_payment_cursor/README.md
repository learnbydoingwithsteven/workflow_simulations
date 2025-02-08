# 🏦 Bank Payment Processing System with LLM Screening 🤖

## 🌟 Features

### 1. 💼 Client Interface
- 📝 Easy payment submission form
- 🔄 Pre-defined transaction templates:
  - 💰 Normal Business Payment
  - 💎 High Value Transaction
  - 🚨 Suspicious Pattern
  - 🌍 International Transfer
- ✨ Modern, user-friendly interface

### 2. 🏢 Bank Clerk Dashboard
- 👀 Real-time payment monitoring
- 🔄 Live transaction updates
- ⚙️ Configurable screening options:
  - 🤖 LLM-based screening (using Ollama)
  - 📊 Rule-based screening

### 3. 🤖 AI-Powered Screening (Ollama Integration)
- 🧠 Uses llama3.2:1b model
- 🔍 Analyzes for:
  - 💱 Money laundering risks
  - 📈 Unusual patterns
  - ⚠️ Suspicious activities
  - 📜 Compliance issues

### 4. 💾 Database Features
- 🔄 Real-time transaction tracking
- 📊 Payment status management
- 🏷️ Risk level classification
- 📝 Detailed screening results storage

## 🚀 How to Use

### 1. 📋 Prerequisites
```bash
# Install required packages
pip install -r requirements.txt

# Make sure Ollama is running with llama3.2:1b model
ollama run llama3.2:1b
```

### 2. 🎯 Running the Application
```bash
python payment.py
```

### 3. 💫 Workflow

#### Client Side 👤
1. 📝 Choose transaction template or create custom
2. ✍️ Fill in payment details
3. 🚀 Submit payment

#### Bank Clerk Side 👨‍💼
1. 👀 Monitor incoming payments
2. 🔍 Review screening results
3. ✅ Approve or ❌ Reject payments

## 🎨 Transaction Templates

### 1. 💼 Normal Business Payment
```json
{
    "amount": 5000.00,
    "currency": "USD",
    "purpose": "Office supplies"
}
```

### 2. 💎 High Value Transaction
```json
{
    "amount": 2500000.00,
    "currency": "USD",
    "purpose": "Property acquisition"
}
```

### 3. 🚨 Suspicious Pattern
```json
{
    "amount": 9999.99,
    "currency": "EUR",
    "purpose": "Consulting fees"
}
```

### 4. 🌍 International Transfer
```json
{
    "amount": 50000.00,
    "currency": "EUR",
    "purpose": "International trade"
}
```

## 🔒 Security Features

- 🤖 AI-powered transaction screening
- ⚡ Real-time risk assessment
- 🔍 AML (Anti-Money Laundering) checks
- 🌐 International transfer monitoring
- 📊 Risk level classification (Low/Medium/High)

## 💡 Smart Screening Logic

### 🤖 LLM Screening
- 🧠 Uses advanced AI for complex analysis
- 📊 Provides detailed risk assessment
- 🎯 Gives specific reasons for decisions

### 📊 Rule-based Screening
- 💰 Amount-based checks
- 🌍 International transfer detection
- ⚡ Quick basic compliance checks

## 🎯 Risk Levels

- 🟢 Low Risk: Standard transactions
- 🟡 Medium Risk: Needs attention
- 🔴 High Risk: Requires thorough review

## 🔄 Status Flow

1. 📥 PENDING
2. 🔍 SCREENING
3. ✅ APPROVED or ❌ REJECTED

## 💻 Technical Stack

- 🐍 Python
- 🖼️ PyQt6 (UI Framework)
- 🤖 Ollama (LLM Integration)
- 💾 SQLite (Database)
- 🔄 SQLAlchemy (ORM)

## 🚀 Future Enhancements

- 📊 Advanced analytics dashboard
- 📱 Mobile app integration
- 🔗 Blockchain transaction support
- 🌐 Multi-currency support expansion
- 📈 Machine learning pattern detection

---
🔧 Developed with ❤️ using Python and Ollama LLM 