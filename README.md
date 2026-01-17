# 🌧️ Smart Rain-Responsive IoT System

A secure, four-layer IoT solution designed to detect rainfall intensity and trigger automated physical responses. This project demonstrates the integration of edge computing (ESP32), secure cloud communication (MQTT over TLS), and real-time data visualization (Streamlit) using Google Cloud Platform (GCP).

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Hardware Required](#-hardware-required)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [Security Measures](#-security-measures)

---

## 🔍 Overview

This system automates the protection of outdoor assets such as clotheslines or open windows by detecting rainfall and triggering an immediate physical response. An ESP32-S3 microcontroller reads analog data from a rain sensor and executes local decision logic. When rain is detected, a servo motor is actuated to simulate a protective mechanism.

Simultaneously, telemetry data is securely transmitted to a Google Cloud Platform (GCP) Virtual Machine via MQTT over TLS. A custom Python MQTT–Firestore bridge processes the incoming data and stores it in Firebase Firestore, which is then visualized using a Streamlit web dashboard.

---

## ✨ Key Features

- **Real-Time Sensing**  
  Continuous monitoring of rainfall intensity using analog sensor input.

- **Automated Actuation**  
  Immediate servo motor response based on edge-level logic, ensuring operation even without internet connectivity.

- **Secure Cloud Communication**  
  MQTT over TLS (Port 8883) with encrypted data transmission.

- **Cloud Middleware Layer**  
  Python-based MQTT bridge isolates IoT devices from direct database access.

- **Live Data Visualization**  
  Streamlit dashboard displays current rain status, historical trends, and system activity.

---

## 🏗 System Architecture

The system follows a **Four-Layer IoT Architecture**:

### 1. Perception Layer
- Sensors: Analog Rain Sensor  
- Actuators: SG90 Servo Motor  
- Edge Device: Maker Feather AIoT S3 (ESP32-S3)

### 2. Transport Layer
- Protocol: MQTT over TLS (Encrypted)  
- Network: WiFi Connectivity  
- Security: GCP Firewall (Port 8883 only)

### 3. Processing Layer
- MQTT Broker: Eclipse Mosquitto (GCP VM)  
- Middleware: Python MQTT–Firestore Bridge (`bridge.py`)  
- Database: Google Firebase Firestore

### 4. Application Layer
- User Interface: Streamlit Web Dashboard

---

## 🛠 Hardware Required

| Component | Description | Connection Pin |
|---------|-------------|----------------|
| Microcontroller | Maker Feather AIoT S3 (ESP32-S3) | N/A |
| Rain Sensor | Analog/Digital Rain Module | Analog A4 |
| Servo Motor | SG90 Micro Servo | Digital D5 (PWM) |
| Power Supply | USB-C Cable / Power Bank | USB |

---

## 💻 Tech Stack

- Firmware: C++ (Arduino IDE)  
- Cloud Platform: Google Cloud Platform (Compute Engine VM)  
- Messaging Protocol: MQTT (Eclipse Mosquitto)  
- Backend Logic: Python 3.x (`paho-mqtt`, `firebase-admin`)  
- Database: Google Firebase Firestore (NoSQL)  
- Frontend Dashboard: Streamlit  

---

## 🚀 Installation & Setup

### 1. Hardware Setup

- Connect Rain Sensor **Analog** pin to ESP32 **A4**
- Connect Rain Sensor **VCC/GND** to ESP32 **3.3V/GND**
- Connect Servo **Signal** pin to ESP32 **D5 (PWM)**
- Power the system via USB

---

### 2. Cloud Configuration (GCP)

- Create a Compute Engine VM (e.g., Debian 12)
- Install Mosquitto MQTT Broker
- Configure MQTT to use TLS on Port 8883
- Generate self-signed SSL/TLS certificates
- Configure GCP Firewall to allow TCP traffic on Port 8883 only

---

### 3. Software Deployment

#### A. ESP32 Firmware

- Open the firmware in the `firmware/` directory using Arduino IDE
- Update `secrets.h` with WiFi credentials and TLS certificates
- Flash the firmware to the ESP32

#### B. Python MQTT–Firestore Bridge

- Place `bridge.py` and `serviceAccountKey.json` on the GCP VM
- Install dependencies:
```bash
pip install paho-mqtt firebase-admin
