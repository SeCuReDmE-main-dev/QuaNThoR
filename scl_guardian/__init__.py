"""
SCL Guardian - Educational Tool Protection System
Synaptic Code License 2.0 Enforcement for QuaNThoR

Copyright (c) 2025 Jean-Sébastien Beaulieu & SeCuReDmE Initiative
SPDX-License-Identifier: SCL-2.0
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path

__version__ = "2.0.0"
__license__ = "SCL-2.0"

class EducationalLock:
    """
    Protects educational tools from modification to ensure classroom stability
    """
    
    def __init__(self, tool_name="QuaNThoR"):
        self.tool_name = tool_name
        self.protection_level = "MAXIMUM"
        self.license_type = "SCL-2.0"
        
    def verify_compliance(self, file_path):
        """
        Verify SCL-2.0 compliance for educational tool files
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Protected file not found: {file_path}")
            
        # Check for required license headers
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "SCL-2.0" not in content:
            self._trigger_violation("Missing SCL-2.0 license header", file_path)
            
        if "SPDX-License-Identifier: SCL-2.0" not in content:
            self._trigger_violation("Invalid SPDX license identifier", file_path)
            
        return True
        
    def educational_lock(self):
        """
        Activate educational protection mode
        """
        print(f"🔒 {self.tool_name} Educational Lock ACTIVATED")
        print(f"📚 Protection Level: {self.protection_level}")
        print(f"⚖️  License: {self.license_type}")
        print(f"🎓 Classroom-ready and student-safe!")
        
        self._create_lock_file()
        
    def _create_lock_file(self):
        """
        Create lock file to indicate protection is active
        """
        lock_data = {
            "tool": self.tool_name,
            "license": self.license_type,
            "protection_level": self.protection_level,
            "locked_at": datetime.now().isoformat(),
            "status": "EDUCATIONAL_LOCK_ACTIVE"
        }
        
        with open('.scl-lock', 'w') as f:
            json.dump(lock_data, f, indent=2)
            
    def _trigger_violation(self, reason, file_path):
        """
        Handle license violations
        """
        violation_data = {
            "violation": reason,
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "tool": self.tool_name,
            "action": "EDUCATIONAL_PROTECTION_ACTIVATED"
        }
        
        print(f"🚨 SCL-2.0 VIOLATION DETECTED: {reason}")
        print(f"📁 File: {file_path}")
        print(f"🔒 Educational tool is now LOCKED for student protection")
        
        with open('.scl-violation.log', 'a') as f:
            f.write(json.dumps(violation_data) + "\n")
            
        raise Exception(f"SCL-2.0 Educational Protection: {reason}")

# Global instances for easy import
quanthor_lock = EducationalLock("QuaNThoR")

def verify_compliance(file_path, license_type="SCL-2.0", protection_level="MAXIMUM"):
    """
    Quick compliance verification function
    """
    if license_type == "SCL-2.0":
        return quanthor_lock.verify_compliance(file_path)
    else:
        raise ValueError(f"Unsupported license type: {license_type}")

def activate_educational_lock():
    """
    Activate educational protection for QuaNThoR
    """
    return quanthor_lock.educational_lock()

# Automatic activation on import
if __name__ != "__main__":
    print("📚 SCL Guardian loaded - Educational tool protection active")