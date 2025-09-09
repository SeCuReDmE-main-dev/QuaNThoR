# GitHub Choose-a-License Submission: SCL-2.0

## Pull Request Template for: https://github.com/github/choosealicense.com

**Title**: Add Synaptic Code License 2.0 (SCL-2.0) for Educational Software

### License Information

**Name**: Synaptic Code License 2.0  
**SPDX ID**: SCL-2.0  
**Category**: Educational Technology License  
**Description**: Dual-tier license providing maximum protection for educational tools and maximum freedom for integration APIs

### Proposed Addition

**File**: `_licenses/scl-2.0.txt`

**Front Matter**:
```yaml
---
title: Synaptic Code License 2.0
spdx-id: SCL-2.0
nickname: SCL-2.0
redirect_from: /licenses/scl/
source: https://github.com/SeCuReDmE-main-dev/SCL-License
description: A dual-tier license that locks educational software for stability while keeping APIs open for innovation.

how: Include the license text in your project and add headers to source files.

using:
  - QuaNThoR: Mathematical verification tool for students
  - MizZzA-r: Classroom management for teachers
  - Educational APIs: Open integration interfaces

permissions:
  - educational-use
  - api-modification
  - distribution
  - patent-use

conditions:
  - include-copyright
  - license-and-copyright-notice
  - same-license

limitations:
  - modification-prohibited-educational
  - liability
  - warranty

---
```

### Why This License Belongs on Choose-a-License

**1. Fills Gap in Educational Software Licensing**
- Traditional open source licenses don't address educational stability needs
- Educational software requires protection from student/hacker tampering
- APIs need freedom for developer innovation

**2. Active Real-World Usage**
- Multiple educational tools already using SCL-2.0
- Growing adoption in educational technology sector
- Addresses specific pain points in classroom software

**3. Clear Use Case Guidelines**
- When you want to lock educational software for stability
- When you want APIs to remain fully open
- When you need automated license enforcement

### Target Users

- **Educational Software Developers**: Creating student/teacher tools
- **EdTech Companies**: Balancing stability with innovation
- **Mathematical Verification Projects**: Academic software projects
- **Classroom Technology**: K-12 and university software

---

**Submission Details:**
- **Author**: Jean-Sébastien Beaulieu & SeCuReDmE Initiative
- **Contact**: jeansebastienbeaulieuscrde.01@gmail.com  
- **Registry**: https://github.com/SeCuReDmE-main-dev/SCL-License
- **SPDX Status**: Submitted for inclusion