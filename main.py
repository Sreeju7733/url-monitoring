#!/usr/bin/env python3
"""
Advanced URL Monitoring System with Alerting
===========================================


A robust website availability checker that:
- Monitors multiple URLs with configurable timeouts
- Performs comprehensive health checks (HTTP status, response time, content verification)
- Sends detailed email alerts with failure diagnostics
- Logs all events for historical tracking
- Supports scheduled monitoring via cron or systemd
"""

import requests
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional

# Configuration - Edit these values for your environment
CONFIG = {
    "urls": [
        {"url": "https://www.google.com", "expected_status": 200, "search_string": None},
        {"url": "https://www.example.com", "expected_status": 200, "search_string": "Example Domain"},
    ],
    "smtp": {
        "server": "smtp.gmail.com",
        "port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_specific_password",  # Generate at: https://myaccount.google.com/apppasswords
        "from": "monitoring@yourdomain.com",
        "to": ["admin@yourdomain.com", "backup@yourdomain.com"],
        "subject_prefix": "[URL Monitor]"
    },
    "monitoring": {
        "timeout_seconds": 10,
        "check_interval_minutes": 5,
        "max_response_time_ms": 2000
    }
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('url_monitor.log'),
        logging.StreamHandler()
    ]
)

class URLMonitor:
    """Core monitoring functionality with alerting capabilities"""
    
    def _init_(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AdvancedURLMonitor/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8'
        })

    def check_url(self, url_config: Dict) -> Dict:
        """Perform comprehensive health check for a single URL"""
        result = {
            "url": url_config["url"],
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "status_code": None,
            "response_time_ms": None,
            "error": None,
            "content_verified": None
        }

        try:
            start_time = time.time()
            response = self.session.get(
                url_config["url"],
                timeout=self.config["monitoring"]["timeout_seconds"],
                allow_redirects=True
            )
            response_time = (time.time() - start_time) * 1000
            result["response_time_ms"] = round(response_time, 2)
            result["status_code"] = response.status_code

            # Check HTTP status
            if response.status_code != url_config["expected_status"]:
                result["error"] = f"Unexpected status: {response.status_code}"
                return result

            # Check content if specified
            if url_config["search_string"]:
                content_match = url_config["search_string"] in response.text
                result["content_verified"] = content_match
                if not content_match:
                    result["error"] = "Search string not found in response"
                    return result

            # Check response time
            if response_time > self.config["monitoring"]["max_response_time_ms"]:
                result["error"] = f"Slow response: {response_time}ms"
                return result

            result["success"] = True
            return result

        except Exception as e:
            result["error"] = str(e)
            return result

    def send_alert(self, check_result: Dict) -> bool:
        """Send detailed email alert about failed check"""
        try:
            smtp_config = self.config["smtp"]
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_config["from"]
            msg['To'] = ", ".join(smtp_config["to"])
            msg['Subject'] = f"{smtp_config['subject_prefix']} Failure: {check_result['url']}"

            # Email body
            body = f"""
            URL Monitoring Alert
            -------------------
            
            URL: {check_result['url']}
            Time: {check_result['timestamp']}
            Error: {check_result['error']}
            
            Diagnostics:
            - Status Code: {check_result.get('status_code', 'N/A')}
            - Response Time: {check_result.get('response_time_ms', 'N/A')} ms
            - Content Verified: {check_result.get('content_verified', 'N/A')}
            
            Recommended Actions:
            1. Verify server connectivity
            2. Check application logs
            3. Validate recent deployments
            """
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                server.send_message(msg)
            
            logging.info(f"Alert sent for {check_result['url']}")
            return True

        except Exception as e:
            logging.error(f"Failed to send alert: {str(e)}")
            return False

    def run_checks(self) -> None:
        """Execute all configured URL checks"""
        logging.info("Starting URL monitoring checks...")
        
        for url_config in self.config["urls"]:
            result = self.check_url(url_config)
            
            if result["success"]:
                logging.info(f"✓ {url_config['url']} - {result['response_time_ms']}ms")
            else:
                logging.error(f"✗ {url_config['url']} - {result['error']}")
                self.send_alert(result)

        logging.info("Completed all checks")

def main():
    """Entry point for the monitoring system"""
    monitor = URLMonitor(CONFIG)
    monitor.run_checks()

if _name_ == "_main_":
    main()
