# Advanced URL Monitoring System

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-ready website monitoring tool that checks URL availability, performance, and content integrity with email alerting capabilities.

## Features

✔ **Comprehensive Health Checks**  
- HTTP status code validation  
- Response time monitoring  
- Content verification (string matching)  

✔ **Instant Alerting**  
- Email notifications with detailed diagnostics  
- Multi-recipient support  
- Configurable alert thresholds  

✔ **Production Ready**  
- Proper logging (file + console)  
- Scheduled monitoring support  
- Connection pooling for efficiency  

## Quick Start

### Prerequisites
- Python 3.8+
- Gmail account (or other SMTP provider)

### Installation
```bash
git clone https://github.com/yourusername/url-monitor.git
cd url-monitor
pip install -r requirements.txt  # Only requests needed
