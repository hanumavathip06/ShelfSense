# ShelfSense - Smart Inventory Management System

ShelfSense is a robust, full-stack inventory management dashboard. It uses a **Flask (Python)** backend powered by a **Neon Serverless Postgres** database, and a **Vite + React + TypeScript** frontend.

Follow the steps below to set up and run the project on your local machine.

## 1. Connect the Neon Database

You'll need a Neon serverless Postgres database for the backend.

1. Go to [Neon.tech](https://neon.tech/) and create a free account or log in.
2. Create a new Project (e.g., `ShelfSense`).
3. Once the database is created, navigate to the **Dashboard** for your project.
4. Locate the **Connection Details** widget.
5. You will need two connection strings:
   - **Pooled Connection (for app traffic):** In the connection widget, check the "Enable connection pooling" box (or add `-pooler` to the endpoint ID in the URL). It looks like: `postgresql://[user]:[password]@[endpoint-id]-pooler.[region].aws.neon.tech/[dbname]?sslmode=require`.
   - **Direct Connection (for migrations):** Uncheck the "Enable connection pooling" box. It looks like: `postgresql://[user]:[password]@[endpoint-id].[region].aws.neon.tech/[dbname]?sslmode=require`.

## 2. Backend Setup

Open a terminal and navigate to the `backend` directory:

```bash
cd backend
```

### Create the Environment File
Copy the example environment file to create your local `.env`:

```bash
cp .env.example .env
```
*(On Windows PowerShell, use `Copy-Item .env.example .env`)*

Open the `.env` file and fill in your Neon database URLs:
```env
# The pooled connection for standard app traffic
DATABASE_URL="postgresql://[user]:[password]@[endpoint]-pooler.aws.neon.tech/neondb?sslmode=require"

# The direct connection for running schema migrations
DATABASE_DIRECT_URL="postgresql://[user]:[password]@[endpoint].aws.neon.tech/neondb?sslmode=require"

# Provide a strong secret key for JWT authentication
JWT_SECRET_KEY="super-secret-key-change-me-in-production"
```

### Install Dependencies
Ensure you have Python 3.11+ installed. Create a virtual environment and install the requirements:

```bash
python -m venv venv

# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### Run Migrations and Seed Data
Initialize your database schema and add some sample data (including user accounts):

```bash
# Run database migrations
flask db upgrade

# Seed the database with sample categories, products, and users
python seed.py
```

### Start the Backend Server
Start the Flask development server:

```bash
python run.py
```
*The backend will now be running on `http://localhost:5000`.*

---

## 3. Frontend Setup

Open a **new, separate terminal** and navigate to the `frontend` directory:

```bash
cd frontend
```

### Check Environment Variables
Ensure the frontend knows where the backend is running. Open `frontend/.env.local` and verify it contains:
```env
VITE_API_URL=http://localhost:5000/api/v1
```

### Install Dependencies
Install the required Node.js packages:

```bash
npm install
```

### Start the Frontend Server
Start the Vite development server:

```bash
npm run dev
```

*The frontend will now be running on `http://localhost:5173`.*

---

## 4. Using the App

1. Open your browser and navigate to `http://localhost:5173`.
2. You will be redirected to the login page.
3. Log in using your user account or the initial bootstrapped admin account.
4. You're all set! Explore the Dashboard, Inventory, Alerts, and Users pages.


# Smart Inventory Management System

## Project Overview

This project is a demonstration of a Smart Inventory Management System designed for small retail businesses. It showcases key concepts and technologies involved in building a modern, data-driven inventory system.  While this is a simplified demonstration, it aims to illustrate core functionalities and architectural considerations.

**Key Features Demonstrated:**

*   **Product Inventory Management:**  Add, view, update, and delete product information (name, description, stock quantity, price).
*   **Web-based User Interface:**  A basic web frontend for interacting with the system (viewing products, adding new products).
*   **Backend API:**  A RESTful API (built with Flask in Python) for managing inventory data.
*   **Data Storage:**  Uses SQLite database for local demonstration (can be easily scaled to PostgreSQL, MySQL, or cloud-based databases).
*   **Data Visualization and Reporting:**  Python script (`data_analysis/analyze_inventory.py`) to generate basic inventory reports and visualizations (e.g., stock distribution chart, low-stock product list, total inventory value). Example report is saved in `data_analysis/reports/`.
*   **Scalability Considerations (Conceptual):**  README discusses how the system can be scaled for larger businesses (database choices, cloud hosting).
*   **Security Considerations (Conceptual):**  README outlines essential security best practices for a real-world inventory system (authentication, authorization, data validation, etc.).
*   **Mobile App Accessibility (Conceptual):**  README discusses the possibility of developing a mobile application (e.g., using React Native or Flutter) to access the system.
*   **Machine Learning and Data Analytics (Conceptual):**  README mentions potential integration of ML for demand forecasting, automated reordering, and other intelligent inventory management features.

**Note:** This is a **demonstration project** and is not intended for production use in a real business without significant further development, security hardening, and testing.

## Technology Stack

*   **Backend API:** Python, Flask (microframework), Flask-SQLAlchemy (ORM)
*   **Database (Demo):** SQLite (for local file-based storage)
*   **Frontend (Web):** HTML, CSS, JavaScript (basic example - can be enhanced with React, Vue.js, Angular for more complex UI)
*   **Data Analysis & Reporting:** Python, pandas, matplotlib, seaborn
*   **Cloud Hosting (Conceptual):**  AWS, Google Cloud, Azure (discussed in "Scalability and Cloud Hosting" section)
*   **Mobile App (Conceptual):** React Native or Flutter (discussed in "Mobile Application" section)

## Setup and Installation

1.  **Clone the GitHub Repository:**
    ```bash
    git clone [repository-url]
    cd smart-inventory-management-system
    ```

2.  **Set up Backend (Python):**
    ```bash
    cd backend
    python -m venv venv        # Create a virtual environment (recommended)
    source venv/bin/activate  # Activate virtual environment (Linux/macOS)
    venv\Scripts\activate      # Activate virtual environment (Windows)
    pip install -r requirements.txt # Install Python dependencies
    ```

3.  **Run the Backend API:**
    ```bash
    python app.py
    ```
    The Flask backend API will start running on `http://127.0.0.1:5000/` (default Flask development server address).

4.  **Open Frontend (Web Browser):**
    *   Navigate back to the project root directory (`smart-inventory-management-system`).
    *   Open the `frontend/index.html` file in your web browser.

    The frontend will attempt to connect to the backend API running on `http://127.0.0.1:5000/`.

5.  **Run Data Analysis and Reporting (Optional):**
    *   Navigate to the `data_analysis` directory: `cd data_analysis`
    *   Run the analysis script: `python analyze_inventory.py`
    *   This script will generate a basic inventory report and a stock distribution chart, saved in the `data_analysis/reports/` folder. **Note:** For this demo, the data analysis uses a sample DataFrame within the script. In a real application, it would fetch data from the database.

## Usage Instructions

1.  **Access the Web Frontend:** Open `frontend/index.html` in your browser.
2.  **View Product Inventory:** The "Product Inventory" section will display a list of products fetched from the backend API. Initially, the database will be empty, so you might see an empty list until you add products.
3.  **Add New Products:**
    *   In the "Add New Product" section, fill in the product details (Name, Description, Stock Quantity, Price).
    *   Click the "Add Product" button.
    *   If successful, you'll see an alert message, and the product list will refresh (you may need to manually refresh the browser in this basic example for the list to update instantly).

## Data Visualization and Reporting

*   **Basic Stock Distribution Chart:** The `data_analysis/analyze_inventory.py` script generates a bar chart (`stock_distribution.png` in `data_analysis/reports/`) visualizing the stock quantity for each product.
*   **Inventory Report (CSV):** The script also saves a basic inventory report in CSV format (`inventory_report.csv` in `data_analysis/reports/`) containing product details and calculated inventory value.

**To generate reports:**

1.  Navigate to the `data_analysis` directory in your terminal.
2.  Run `python analyze_inventory.py`.
3.  Check the `data_analysis/reports/` folder for the generated `stock_distribution.png` and `inventory_report.csv` files.

**Future Enhancements (Conceptual - Not Implemented in this Demo):**

*   **Enhanced Frontend UI:**  Use a JavaScript framework like React, Vue.js, or Angular to create a more interactive and feature-rich user interface (e.g., product editing, deletion, search, filtering, pagination, user authentication).
*   **Database Scalability:**  Replace SQLite with a more robust and scalable database like PostgreSQL, MySQL, or cloud-based database services (AWS RDS, Google Cloud SQL, Azure SQL Database) for handling larger datasets and concurrent users.
*   **User Authentication and Authorization:** Implement user accounts, roles, and permissions to control access to different parts of the system and ensure data security.
*   **Advanced Reporting and Analytics:** Develop more sophisticated reports and dashboards, including sales trends, low-stock alerts, demand forecasting, inventory turnover analysis, using libraries like pandas, matplotlib, seaborn, and potentially business intelligence (BI) tools.
*   **Machine Learning Integration:**
    *   **Demand Forecasting:** Integrate machine learning models to predict future demand based on historical sales data, seasonality, and other factors. This can help optimize stock levels and reduce stockouts or overstocking.
    *   **Automated Reordering:**  Develop algorithms to automatically trigger reorder points based on predicted demand and current stock levels.
    *   **Anomaly Detection:**  Use ML to detect unusual patterns in inventory data (e.g., sudden stock depletions, unexpected sales spikes) that could indicate errors or issues.
*   **Mobile Application:** Develop a mobile app (using React Native, Flutter, or native mobile development) to provide inventory access and management on mobile devices for staff in the retail environment (e.g., stocktaking, order fulfillment, receiving shipments).
*   **Cloud Hosting and Deployment:** Deploy the backend API and frontend to a cloud platform (AWS, Google Cloud, Azure) for scalability, reliability, and accessibility over the internet. Use services like AWS EC2/Elastic Beanstalk, Google App Engine/Compute Engine, Azure App Service, and database services like AWS RDS, Google Cloud SQL, Azure SQL Database.
*   **Security Hardening:** Implement comprehensive security measures:
    *   **HTTPS:**  Use HTTPS for all communication to encrypt data in transit.
    *   **Input Validation:**  Thoroughly validate all user inputs on both frontend and backend to prevent injection attacks.
    *   **Secure Authentication and Authorization:** Implement robust user authentication (e.g., JWT, OAuth 2.0) and authorization mechanisms.
    *   **Database Security:**  Securely configure and manage the database, using parameterized queries to prevent SQL injection.
    *   **Regular Security Audits and Updates:**  Conduct regular security audits and keep dependencies and frameworks up-to-date to patch vulnerabilities.

## Scalability and Cloud Hosting (Conceptual)

For a real-world, scalable inventory system, cloud hosting is highly recommended. Here's a conceptual outline:

*   **Cloud Platform:** Choose a cloud provider like AWS, Google Cloud, or Azure.
*   **Backend API Hosting:**
    *   **Containerization:** Package the Flask backend API in a Docker container.
    *   **Cloud Compute Service:** Deploy the container to a scalable compute service like AWS ECS/Fargate, Google Cloud Run, Azure Container Instances, or a platform-as-a-service (PaaS) like AWS Elastic Beanstalk, Google App Engine, Azure App Service.
    *   **Load Balancing:** Use a load balancer to distribute traffic across multiple instances of the API for high availability and scalability.
*   **Database Hosting:**
    *   Use a managed cloud database service like AWS RDS (PostgreSQL, MySQL), Google Cloud SQL (PostgreSQL, MySQL), Azure SQL Database. These services provide scalability, backups, security, and easier management compared to self-hosting databases on VMs.
*   **Frontend Hosting:**
    *   Host the static frontend files (HTML, CSS, JavaScript) on a cloud storage service optimized for web serving, like AWS S3 with CloudFront CDN, Google Cloud Storage with Cloud CDN, Azure Blob Storage with Azure CDN.
*   **Benefits of Cloud Hosting:**
    *   **Scalability:** Easily scale resources (compute, database) up or down based on demand.
    *   **Reliability and Availability:** Cloud platforms offer high uptime and redundancy.
    *   **Managed Services:**  Cloud providers manage infrastructure, operating systems, and database maintenance, reducing operational overhead.
    *   **Cost-Effectiveness:** Pay-as-you-go pricing models can be more cost-effective than maintaining on-premises infrastructure.

## Mobile Application (Conceptual)

To provide mobile access, a mobile application can be developed that interacts with the same backend API.

*   **Framework:** Choose a cross-platform framework like React Native or Flutter to develop apps for both iOS and Android from a single codebase, or consider native mobile development (Swift for iOS, Kotlin/Java for Android) for potentially better performance and access to device-specific features.
*   **API Interaction:** The mobile app would communicate with the Flask backend API over HTTP to fetch and update inventory data.
*   **Mobile Features:**  Mobile app can be designed for specific use cases in a retail environment, such as:
    *   **Stocktaking:**  Scanning barcodes and updating stock quantities directly from the app.
    *   **Order Fulfillment:**  Managing and processing customer orders.
    *   **Receiving Shipments:**  Updating inventory when new stock arrives.
    *   **Real-time Inventory Views:**  Providing staff with up-to-date inventory information on their mobile devices.
    *   **Push Notifications:**  Alerting staff about low stock levels, reorder points, or important inventory updates.

---

**To use this project for your application:**

1.  **Set up the project structure and files as described.**
2.  **Implement the backend API (even if simplified), frontend, and data analysis scripts.**
3.  **Write a comprehensive README.md file using the provided template, detailing all aspects of the system, including the conceptual discussions on scalability, security, cloud hosting, mobile app, and machine learning.**
4.  **Host the repository on GitHub.**
5.  **In your application materials and CV, provide a link to your GitHub repository.**  Highlight the project and its features, emphasizing your understanding of business processes, information systems design, data-driven decision-making, and relevant technologies.

Remember to adapt and expand upon this demonstration project to best showcase your skills and align with the specific requirements of the International Business Information Systems course at Furtwangen University. Good luck!
