import os
import sys
import json

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(current_dir)

from Frontend.Main import SaveChatToLog, ClearAllChatHistory

# First clear the chat history
ClearAllChatHistory()

# Now add our test messages
print("Adding test messages...")

# First question and answer
SaveChatToLog(
    "Full form of ips", 
    "The full form of IPS is Indian Police Service."
)

# Second question and answer
SaveChatToLog(
    "Can you give me some points on benefits of ips",
    """Benefits of Indian Police Service (IPS):

1. Prestigious Career: One of India's most respected civil services
2. Leadership Role: Command police forces at district and state levels
3. Power and Authority: Significant decision-making authority in law enforcement
4. Job Security: Permanent government position with stability
5. Good Compensation: Attractive salary and benefits package
6. Career Growth: Multiple promotion opportunities throughout service
7. Diverse Responsibilities: From law enforcement to intelligence, security, and administration
8. National Service: Opportunity to serve the country and make a difference"""
)

print("Update complete. Check the chat display.") 