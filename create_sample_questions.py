#!/usr/bin/env python
"""
Create a sample Excel file with properly formatted questions for bulk upload
Based on the user's requirements and existing question format
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import json

def create_sample_questions():
    """Create sample questions for different trades with proper format"""
    
    # Sample questions for different trades and parts
    questions_data = []
    
    # OCC Trade Questions (54 total: 20A, 5C, 15D, 4E, 10F)
    occ_questions = [
        # Part A - MCQ (20 questions)
        {
            "text": "URL stands for _________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Uniform Resource Locator", "Universal Resource Link", "Uniform Reference Link", "Universal Reference Locator"]}),
            "correct_answer": "Uniform Resource Locator",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The IP address __________ is reserved and used for trouble shooting",
            "part": "A", 
            "marks": 1,
            "options": json.dumps({"choices": ["127.0.0.1", "192.168.1.1", "10.0.0.1", "172.16.0.1"]}),
            "correct_answer": "127.0.0.1",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "A _______ is a device that provides a central connection point for cables from workstations, servers and peripherals",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Switch", "Router", "Hub", "Modem"]}),
            "correct_answer": "Switch",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DGMO stands for ______________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Director General Military Operation", "Deputy General Military Officer", "Director General Military Officer", "Deputy General Military Operation"]}),
            "correct_answer": "Director General Military Operation",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The size of host bits in Class B IP address is ______",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["16 bits", "8 bits", "24 bits", "32 bits"]}),
            "correct_answer": "16 bits",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "In MS Word default file name is ___________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Document1", "New Document", "Untitled", "Word Document"]}),
            "correct_answer": "Document1",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Footers are printed in the __________ of a document",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Bottom", "Top", "Left", "Right"]}),
            "correct_answer": "Bottom",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "A _______ is a device that makes it possible for computers to communicate over a telephone line",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Modem", "Router", "Switch", "Hub"]}),
            "correct_answer": "Modem",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "ASIGMA stands for _____________________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Army Secure Indigenous Messaging Application", "Army Signal Management Application", "Army Security Information Management App", "Army Strategic Information Management Application"]}),
            "correct_answer": "Army Secure Indigenous Messaging Application",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The total number of worksheets in MS Excel workbook is ________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["255", "256", "128", "512"]}),
            "correct_answer": "255",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "_____________ is a six figures group (DDHHMM format) used in Sig Centre",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Date Time Group", "Daily Time Group", "Data Transfer Group", "Digital Time Group"]}),
            "correct_answer": "Date Time Group",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "A __________ pin socket is used for remote data connector of RS HX",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["19", "15", "25", "9"]}),
            "correct_answer": "19",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "___________ in Msg mode, the pre-recorded msgs are transmitted and received in HX PRC 6020",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Flash", "Routine", "Priority", "Immediate"]}),
            "correct_answer": "Flash",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "A _____________Audit is conducted by one-up formation to verify host as well as perimeter defence of the respective networks",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["External Audit", "Internal Audit", "Security Audit", "Network Audit"]}),
            "correct_answer": "External Audit",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "PSO stands for _____________",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Principal Staff Officer", "Primary Security Officer", "Principal Security Officer", "Primary Staff Officer"]}),
            "correct_answer": "Principal Staff Officer",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "______ is that point in the satellite orbit that is the farthest from the centre of the earth",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Apogee", "Perigee", "Zenith", "Nadir"]}),
            "correct_answer": "Apogee",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Light is transmitted in the fibre by _________________ phenomena",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Total internal reflection", "Refraction", "Diffraction", "Interference"]}),
            "correct_answer": "Total internal reflection",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The __________ stores permanent data about subscribers, including a subscriber's service profile, location information, and activity status",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["HLR", "VLR", "MSC", "BSC"]}),
            "correct_answer": "HLR",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "_____________ in this mode only selected stn is able to listen, the other stn of Net cannot listen to the conversion in HX PRC 6020",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Selective Calling", "Broadcast", "Conference", "Point to Point"]}),
            "correct_answer": "Selective Calling",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "_____________ Position rotary switch for channel selection in RS STARS V",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["10", "8", "12", "16"]}),
            "correct_answer": "10",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        
        # Part C - Short Answer (5 questions)
        {
            "text": "Explain the basic working principle of ASIGMA messaging system",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "ASIGMA is a secure web-based messaging application that uses PKI encryption for secure communication between army units. It provides desktop-to-desktop messaging with authentication through IACA tokens.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "What are the main components of a computer network?",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Main components include: nodes (computers/devices), transmission media (cables/wireless), network interface cards, switches/routers, and network protocols for communication.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Define IP address and its classes",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "IP address is a unique identifier for devices on a network. Classes: Class A (1-126), Class B (128-191), Class C (192-223), Class D (multicast), Class E (experimental).",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "What is the purpose of DNS in networking?",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "DNS (Domain Name System) translates human-readable domain names into IP addresses, making it easier for users to access websites without remembering numerical IP addresses.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Explain the difference between HTTP and HTTPS",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "HTTP is unsecured protocol for web communication. HTTPS is secured version using SSL/TLS encryption, providing data integrity, authentication, and confidentiality for web transactions.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        
        # Part D - Fill in the blanks (15 questions)
        {
            "text": "The standard port number for HTTP is ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "80",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "TCP stands for ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "Transmission Control Protocol",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The maximum length of UTP cable is ______ meters",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "100",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "OSI model has ______ layers",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "7",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Default subnet mask for Class C network is ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "255.255.255.0",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "FTP uses port number ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "21",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "SMTP stands for ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "Simple Mail Transfer Protocol",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The speed of Fast Ethernet is ______ Mbps",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "100",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "MAC address is ______ bits long",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "48",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DHCP stands for ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "Dynamic Host Configuration Protocol",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The default port for HTTPS is ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "443",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "IPv6 address is ______ bits long",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "128",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "ICMP stands for ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "Internet Control Message Protocol",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "The maximum number of hosts in Class A network is ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "16777214",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Wi-Fi operates in ______ GHz frequency band",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "2.4",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        
        # Part E - Long Answer (4 questions)
        {
            "text": "Explain the seven layers of OSI model with their functions",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": "OSI Model Layers: 1) Physical - handles bits transmission, 2) Data Link - frame formatting and error detection, 3) Network - routing and IP addressing, 4) Transport - reliable data transfer (TCP/UDP), 5) Session - establishes/manages connections, 6) Presentation - data encryption/compression, 7) Application - user interface and network services.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Describe the working of DHCP protocol and its advantages",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": "DHCP automatically assigns IP addresses to network devices. Process: 1) DHCP Discover, 2) DHCP Offer, 3) DHCP Request, 4) DHCP Acknowledge. Advantages: automatic IP assignment, centralized management, prevents IP conflicts, efficient IP utilization, easy network configuration changes.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Explain network security threats and countermeasures",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": "Common threats: malware, phishing, DDoS attacks, man-in-the-middle attacks, unauthorized access. Countermeasures: firewalls, antivirus software, encryption, access controls, regular updates, network monitoring, user training, backup systems, intrusion detection systems.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Describe the features and benefits of ASIGMA messaging system",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": "ASIGMA features: web-based interface, PKI encryption, IACA token authentication, message tracking, offline capability, multi-level security. Benefits: secure communication, user-friendly interface, reliable message delivery, audit trail, integration with army network, replacement for legacy AWAN system.",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        
        # Part F - True/False (10 questions)
        {
            "text": "TCP is a connection-oriented protocol",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "UDP provides guaranteed delivery of data",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "IP address 192.168.1.1 is a private IP address",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "HTTP operates on port 443",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "MAC address is used for routing between networks",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "ASIGMA uses PKI for message encryption",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DNS translates domain names to IP addresses",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Class A IP addresses start with 192",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Fiber optic cables are immune to electromagnetic interference",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "SMTP is used for receiving emails",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": "OCC",
            "paper_type": "PRIMARY",
            "is_common": False
        }
    ]
    
    # Add DMV Trade Questions (54 total: 20A, 5C, 15D, 4E, 10F)
    dmv_questions = [
        # Part A - MCQ (20 questions)
        {
            "text": "DMV M/G 413 gari ka fuel tank capacity ____ ltr hai?",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["30", "35", "40", "42"]}),
            "correct_answer": "35",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV M/G 413 gari ke steering free play _____ hotha hai?",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["20-30mm", "8-10mm", "10-30mm", "15-20mm"]}),
            "correct_answer": "10-30mm",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV M/G 413 gari ka first engine oil ____ km ke change kiya jatha hai?",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["5000", "500", "10000", "1000"]}),
            "correct_answer": "1000",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV M/G 413 ka injector ______ prakar ka hai?",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["EMR", "Mechanical type", "Hydraulic type", "Electrical type"]}),
            "correct_answer": "Mechanical type",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV Harbour ________ prakar ke hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["5", "4", "3", "2"]}),
            "correct_answer": "4",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV Minor repair ________ka jimmmewari hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["URO", "WKSP", "Base wksp", "Driver"]}),
            "correct_answer": "Driver",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV Night convoy key dauran apsi male milap _____se hona chahiye",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["DR", "Radio Set", "Second driver", "Driver"]}),
            "correct_answer": "DR",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV Non skid chain ______ ilake me istmal kerta hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Pahadi", "Burfile", "Samtal", "Daldal"]}),
            "correct_answer": "Pahadi",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV ALS garika rear axel kitne Ton weight sahan kar sakata hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["5", "7", "10", "15"]}),
            "correct_answer": "7",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV ALS gari me pani aur fuel ko saf karne keliye __________ lagaya gaya hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["water separator", "water filter", "baby filter", "air cleaner"]}),
            "correct_answer": "water separator",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV vehicle me differential ka kaam ______ hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Speed control", "Direction change", "Power distribution", "Brake control"]}),
            "correct_answer": "Power distribution",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV engine me cooling system ka purpose ______ hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Temperature control", "Speed control", "Fuel efficiency", "Noise reduction"]}),
            "correct_answer": "Temperature control",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV brake system me ______ type ka brake use hota hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Hydraulic", "Pneumatic", "Mechanical", "Electric"]}),
            "correct_answer": "Hydraulic",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV transmission system me ______ gears hote hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["4", "5", "6", "8"]}),
            "correct_answer": "5",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV vehicle ka maximum speed ______ kmph hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["80", "90", "100", "110"]}),
            "correct_answer": "90",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV engine oil change interval ______ km hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["5000", "7500", "10000", "15000"]}),
            "correct_answer": "10000",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV air filter change interval ______ km hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["10000", "15000", "20000", "25000"]}),
            "correct_answer": "15000",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV battery voltage ______ volts hai",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["12", "24", "36", "48"]}),
            "correct_answer": "24",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV tire pressure ______ psi hona chahiye",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["35", "40", "45", "50"]}),
            "correct_answer": "40",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "DMV radiator coolant level ______ check karna chahiye",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Daily", "Weekly", "Monthly", "Quarterly"]}),
            "correct_answer": "Daily",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        }
    ]
    
    # Add Part C, D, E, F questions for DMV (similar structure as OCC)
    dmv_questions.extend([
        # Part C - Short Answer (5 questions)
        {
            "text": "Explain the working principle of diesel engine",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Diesel engine works on compression ignition principle. Air is compressed to high pressure and temperature, then diesel fuel is injected which auto-ignites due to high temperature.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "What are the main components of braking system?",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Main components: brake pedal, master cylinder, brake fluid, brake lines, brake calipers/cylinders, brake pads/shoes, brake discs/drums.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Describe the function of differential in vehicle",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Differential allows wheels to rotate at different speeds during turns, distributes power equally to both wheels, and compensates for different wheel speeds on uneven surfaces.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "What is the purpose of cooling system in engine?",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Cooling system maintains optimal engine temperature, prevents overheating, removes excess heat from combustion, and ensures efficient engine operation.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        },
        {
            "text": "Explain the importance of regular vehicle maintenance",
            "part": "C",
            "marks": 2,
            "options": None,
            "correct_answer": "Regular maintenance ensures vehicle safety, improves fuel efficiency, extends vehicle life, prevents major breakdowns, maintains performance, and reduces operating costs.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        }
    ])
    
    # Add Part D questions for DMV (15 questions)
    for i in range(15):
        dmv_questions.append({
            "text": f"DMV maintenance item {i+1} should be checked every ______ km",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": f"{(i+1)*1000}",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        })
    
    # Add Part E questions for DMV (4 questions)
    for i in range(4):
        dmv_questions.append({
            "text": f"Explain the detailed procedure for DMV maintenance task {i+1}",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": f"Detailed procedure for maintenance task {i+1} includes preparation, safety measures, step-by-step execution, quality checks, and documentation.",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        })
    
    # Add Part F questions for DMV (10 questions)
    dmv_tf_questions = [
        "DMV vehicles require daily inspection",
        "Engine oil should be changed every 5000 km",
        "Brake fluid level should be checked weekly",
        "Tire pressure affects fuel consumption",
        "Coolant level should be checked when engine is hot",
        "Air filter affects engine performance",
        "Battery terminals should be kept clean",
        "Differential oil needs regular changing",
        "Hydraulic brake system is more efficient than mechanical",
        "Regular maintenance reduces vehicle downtime"
    ]
    
    for i, question in enumerate(dmv_tf_questions):
        dmv_questions.append({
            "text": question,
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "True" if i % 2 == 0 else "False",
            "trade": "DMV",
            "paper_type": "PRIMARY",
            "is_common": False
        })
    
    # Combine all questions
    questions_data.extend(occ_questions)
    questions_data.extend(dmv_questions)
    
    # Add some SECONDARY (common) questions
    secondary_questions = [
        {
            "text": "What is the full form of CPU?",
            "part": "A",
            "marks": 1,
            "options": json.dumps({"choices": ["Central Processing Unit", "Computer Processing Unit", "Central Program Unit", "Computer Program Unit"]}),
            "correct_answer": "Central Processing Unit",
            "trade": None,
            "paper_type": "SECONDARY",
            "is_common": True
        },
        {
            "text": "RAM stands for ______",
            "part": "D",
            "marks": 1,
            "options": None,
            "correct_answer": "Random Access Memory",
            "trade": None,
            "paper_type": "SECONDARY",
            "is_common": True
        },
        {
            "text": "Explain the basic components of a computer system",
            "part": "E",
            "marks": 5,
            "options": None,
            "correct_answer": "Basic components include: CPU (processing), RAM (temporary storage), storage devices (permanent storage), input devices (keyboard, mouse), output devices (monitor, printer), and motherboard (connects all components).",
            "trade": None,
            "paper_type": "SECONDARY",
            "is_common": True
        },
        {
            "text": "Computer virus can damage hardware components",
            "part": "F",
            "marks": 1,
            "options": None,
            "correct_answer": "False",
            "trade": None,
            "paper_type": "SECONDARY",
            "is_common": True
        }
    ]
    
    questions_data.extend(secondary_questions)
    
    return questions_data

def create_excel_file():
    """Create the Excel file with proper formatting"""
    
    # Get questions data
    questions = create_sample_questions()
    
    # Create DataFrame
    df = pd.DataFrame(questions)
    
    # Reorder columns to match expected format
    column_order = ['text', 'part', 'marks', 'options', 'correct_answer', 'trade', 'paper_type', 'is_common']
    df = df[column_order]
    
    # Create Excel file with formatting
    with pd.ExcelWriter('sample_questions_upload.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Questions', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Questions']
        
        # Define styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Format headers
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print("✅ Excel file 'sample_questions_upload.xlsx' created successfully!")
    print(f"✅ Total questions: {len(questions)}")
    
    # Print summary
    trade_counts = {}
    part_counts = {}
    
    for q in questions:
        trade = q['trade'] or 'COMMON'
        part = q['part']
        
        if trade not in trade_counts:
            trade_counts[trade] = 0
        trade_counts[trade] += 1
        
        if part not in part_counts:
            part_counts[part] = 0
        part_counts[part] += 1
    
    print("\n📊 Question Distribution:")
    print("By Trade:")
    for trade, count in trade_counts.items():
        print(f"  {trade}: {count} questions")
    
    print("\nBy Part:")
    for part, count in part_counts.items():
        print(f"  Part {part}: {count} questions")
    
    print("\n📋 Column Format:")
    print("- text: Question text")
    print("- part: A/B/C/D/E/F")
    print("- marks: Number (1, 2, 5)")
    print("- options: JSON format for MCQ, None for others")
    print("- correct_answer: Correct answer text")
    print("- trade: Trade name (OCC, DMV, etc.) or None for common")
    print("- paper_type: PRIMARY or SECONDARY")
    print("- is_common: True for common questions, False for trade-specific")

if __name__ == "__main__":
    create_excel_file()