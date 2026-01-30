# Solution Guide: Enabling Camera Access in Offline Django Portal

This document provides a comprehensive solution to enable the camera capture feature in your offline Django-based Army Portal. The issue, as you correctly identified, is that modern web browsers require a **secure context (HTTPS)** to access the `navigator.mediaDevices.getUserMedia()` API, which is used for camera access. Running the project on the insecure **HTTP** protocol prevents the camera from opening.

The solution involves configuring your local development environment to serve the application over HTTPS using a self-signed certificate.

## 1. Technical Analysis

The project is a Django application that uses client-side JavaScript to access the camera.

| Component | Detail | Finding |
| :--- | :--- | :--- |
| **Project Type** | Django Web Application | Confirmed by `manage.py` and `settings.py`. |
| **Camera Implementation** | JavaScript `navigator.mediaDevices.getUserMedia()` | Found in `registration/templates/registration/register_candidate.html` (lines 571-577). |
| **Issue Root Cause** | Insecure Context | The `getUserMedia` API is restricted to secure origins (HTTPS) by modern browsers [1]. |
| **Solution Approach** | Use `runserver_plus` with a self-signed SSL certificate. | This allows Django's development server to serve content over HTTPS locally. |

## 2. Implementation Steps

The fix requires two main actions: generating a self-signed SSL certificate and using the `runserver_plus` command provided by the `django-extensions` package to start the server with HTTPS.

### Step 2.1: Install Required Dependencies

The `runserver_plus` command is part of the `django-extensions` package, which requires `werkzeug` and `pyOpenSSL`.

1.  **Install Packages:** Ensure you have the necessary packages installed. You can run this command in your project's virtual environment:

    ```bash
    pip install django-extensions werkzeug pyOpenSSL
    ```

2.  **Update `settings.py`:** The `django-extensions` app must be added to your `INSTALLED_APPS`. This has been done for you in `config/settings.py`:

    ```python
    # config/settings.py (Line 39)
    INSTALLED_APPS = [
        'django_extensions', # <-- ADDED
        'jazzmin',
        # ... other apps
    ]
    ```

### Step 2.2: Generate Self-Signed SSL Certificate

A self-signed certificate is necessary to establish an HTTPS connection for local, offline use.

1.  **Certificate Generation:** The following command uses `openssl` to generate a private key (`key.pem`) and a self-signed certificate (`cert.pem`) valid for one year, stored in a new `ssl` directory within your project root.

    ```bash
    # Run this command from the project root directory (where manage.py is located)
    mkdir -p ssl
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=IN/ST=Delhi/L=Delhi/O=ArmyPortal/OU=IT/CN=localhost"
    ```

    *Note: This step has been executed in the sandbox environment, and the `ssl` directory with the necessary files is now included in the final deliverable.*

### Step 2.3: Start the Server with HTTPS

Instead of the standard `python manage.py runserver`, you will now use the custom script provided, which calls `runserver_plus`.

1.  **Use the New Script:** A new Python script, `run_https.py`, and a Windows batch file, `run_https.bat`, have been created in your project root to simplify the process.

    *   **On Linux/macOS:**
        ```bash
        python run_https.py
        ```
    *   **On Windows:**
        ```bash
        run_https.bat
        ```

    This script will start the server using the generated certificates:
    ```bash
    python manage.py runserver_plus 0.0.0.0:8000 --cert-file ssl/cert.pem --key-file ssl/key.pem
    ```

2.  **Access the Portal:** The portal must now be accessed using **HTTPS** at:

    ```
    https://127.0.0.1:8000/
    ```

    **Important:** Since the certificate is self-signed (not issued by a trusted authority), your browser will display a **security warning** (e.g., "Your connection is not private"). You **must** click on **"Advanced"** or **"Show Details"** and then **"Proceed to 127.0.0.1 (unsafe)"** to bypass the warning. After this, the camera should function correctly.

### Step 2.4: Secure Cookie Configuration (Optional but Recommended)

For a more secure setup when running on HTTPS, the `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` settings should be enabled. This has been updated in your `.env` file:

```ini
# .env (Lines 41-42)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 3. Summary of Changes

The following files have been added or modified in your project:

| File | Status | Change Description |
| :--- | :--- | :--- |
| `ssl/cert.pem` | **ADDED** | Self-signed SSL certificate file. |
| `ssl/key.pem` | **ADDED** | Private key file for the certificate. |
| `run_https.py` | **ADDED** | Python script to start the server with HTTPS. |
| `run_https.bat` | **ADDED** | Windows batch file to run the HTTPS script. |
| `config/settings.py` | **MODIFIED** | Added `'django_extensions'` to `INSTALLED_APPS`. |
| `.env` | **MODIFIED** | Set `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True`. |

By following these steps and accessing the portal via `https://127.0.0.1:8000/`, the camera capture functionality will be restored.

***

### References

[1] MDN Web Docs. [MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).
